from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import sys
import traceback
import json

# Force UTF-8 output so emoji in prompts/responses don't crash on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('data', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

SCREENING_CONFIDENCE_THRESHOLD = 0.70
SCREENING_MARGIN_THRESHOLD = 0.15
STRONG_CONFLICT_THRESHOLD = 0.80
MAX_EVIDENCE_CHARS = 900

URGENT_SYMPTOM_TERMS = (
    "sudden vision loss", "vision loss", "loss of sight", "severe pain",
    "eye pain", "chemical", "chemical exposure", "chemical injury", "trauma",
    "injury", "flashes", "floaters", "curtain", "shadow over vision",
    "painful red eye", "nausea", "headache", "double vision",
)

# ── NOTE: Inference (TensorFlow/Keras) is imported AFTER embeddings below ────
# This ensures PyTorch + NumPy (used by sentence-transformers) are fully
# initialized before TensorFlow's C++ runtime loads and touches NumPy.
# DO NOT move this block above the embeddings section.

# ── API Keys ─────────────────────────────────────────────────────────────────
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
GOOGLE_API_KEY   = os.environ.get("GOOGLE_API_KEY", "")

if PINECONE_API_KEY:
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
    print(f"[OK] Pinecone API key loaded ({PINECONE_API_KEY[:8]}...)")
else:
    print("[WARN] PINECONE_API_KEY not found in .env")

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print(f"[OK] Google API key loaded ({GOOGLE_API_KEY[:8]}...)")
else:
    print("[WARN] GOOGLE_API_KEY not found in .env")

# ── Embeddings (PyTorch / sentence-transformers — must load FIRST) ───────────
embeddings = None
try:
    from src.helper import download_hugging_face_embeddings
    embeddings = download_hugging_face_embeddings()
    print("[OK] Embeddings loaded.")
except Exception as e:
    print(f"[WARN] Embeddings failed to load: {e}")
    traceback.print_exc()

# ── Inference models (CNN + Fusion) — imported AFTER embeddings ──────────────
# TensorFlow loads lazily inside these functions only when an image is sent.
try:
    from src.inference import predict_cnn, predict_fusion
    print("[OK] Inference module loaded successfully.")
except Exception as e:
    print(f"[WARN] Inference module failed to load: {e}")
    traceback.print_exc()
    def predict_cnn(img_path):
        return {"diagnosis": "CNN model unavailable", "confidence": 0.0}
    def predict_fusion(img_path, txt):
        return {"diagnosis": "Fusion model unavailable", "confidence": 0.0}

# ── Pinecone Vector Store ─────────────────────────────────────────────────────
retriever = None
if embeddings and PINECONE_API_KEY:
    try:
        from langchain_pinecone import PineconeVectorStore
        docsearch = PineconeVectorStore.from_existing_index(
            index_name="eye-disease",
            embedding=embeddings
        )
        retriever = docsearch.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        print("[OK] Pinecone retriever ready.")
    except Exception as e:
        print(f"[WARN] Pinecone failed: {e}")
        traceback.print_exc()
else:
    print("[SKIP] Pinecone skipped (missing embeddings or API key).")

# ── Gemini Chat Model ─────────────────────────────────────────────────────────
chatModel = None
if GOOGLE_API_KEY:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        chatModel = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            max_output_tokens=2048
        )
        print("[OK] Gemini model ready.")
    except Exception as e:
        print(f"[WARN] Gemini model failed: {e}")
        traceback.print_exc()
else:
    print("[SKIP] Gemini skipped (no GOOGLE_API_KEY).")

# ── RAG Chain ─────────────────────────────────────────────────────────────────
rag_chain = None
query_optimizer = None
if retriever and chatModel:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough
        from src.prompt import system_prompt

        def format_docs(docs):
            blocks = []
            for idx, doc in enumerate(docs, 1):
                label = _doc_source_label(doc, idx)
                blocks.append(f"[{idx}] Source: {label}\n{doc.page_content}")
            return "\n\n".join(blocks)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Chain to optimize search query (correct spelling/typos)
        query_optimizer = (
            ChatPromptTemplate.from_messages([
                ("system", "You are an expert query optimizer for an ophthalmology search database. "
                           "Your task is to take the user's input, correct any spelling errors or typos (e.g. 'glucoma' -> 'glaucoma', 'symptomps' -> 'symptoms'), "
                           "and output ONLY the corrected search query. Do not add any extra text or explanation."),
                ("human", "{input}")
            ])
            | chatModel
            | StrOutputParser()
        )

        rag_chain = prompt | chatModel | StrOutputParser()
        print("[OK] RAG chain ready.")
    except Exception as e:
        print(f"[WARN] RAG chain failed: {e}")
        traceback.print_exc()
else:
    print("[SKIP] RAG chain skipped (missing retriever or chat model).")

# ── Direct Gemini Fallback Chain (no Pinecone — used when KB is offline) ─────
# Answers using Gemini alone when the network/Pinecone is unreachable.
direct_chain = None
if chatModel:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from src.prompt import offline_system_prompt
        
        _direct_prompt = ChatPromptTemplate.from_messages([
            ("system", offline_system_prompt),
            ("human", "{input}"),
        ])
        direct_chain = (
            _direct_prompt
            | chatModel
            | StrOutputParser()
        )
        print("[OK] Direct Gemini fallback chain ready.")
    except Exception as e:
        print(f"[WARN] Direct chain setup failed: {e}")
else:
    print("[SKIP] Direct chain skipped (no chat model).")

# ── Diagnosis Explanation Chain (CNN/Fusion model output → Gemini) ─────────────
diagnosis_chain = None
if chatModel:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from src.prompt import diagnosis_system_prompt

        _diag_prompt_template = ChatPromptTemplate.from_messages([
            ("system", diagnosis_system_prompt),
            ("human", "Please generate the full OcuAI Diagnostic Report for this patient now."),
        ])
        diagnosis_chain = _diag_prompt_template | chatModel | StrOutputParser()
        print("[OK] Diagnosis explanation chain ready.")
    except Exception as e:
        print(f"[WARN] Diagnosis chain setup failed: {e}")
        traceback.print_exc()
else:
    print("[SKIP] Diagnosis chain skipped (no chat model).")


def _top_probabilities(result: dict, limit: int = 3) -> str:
    probs = result.get("all_probs") or {}
    if not probs:
        return "No probability distribution returned."
    ranked = sorted(probs.items(), key=lambda item: item[1], reverse=True)[:limit]
    return "\n".join(f"- {label}: {score:.1%}" for label, score in ranked)


def _is_uncertain(result: dict) -> bool:
    return bool(_uncertainty_reasons(result))


def _has_urgent_symptom_text(text: str) -> bool:
    msg = (text or "").lower()
    return any(term in msg for term in URGENT_SYMPTOM_TERMS)


def _uncertainty_reasons(result: dict) -> list:
    reasons = []
    confidence = float(result.get("confidence", 0.0))
    if confidence < SCREENING_CONFIDENCE_THRESHOLD:
        reasons.append(
            f"top model score is below threshold ({confidence:.1%} < {SCREENING_CONFIDENCE_THRESHOLD:.0%})"
        )

    probs = result.get("all_probs") or {}
    ranked = sorted(probs.items(), key=lambda item: item[1], reverse=True)
    if len(ranked) >= 2:
        margin = float(ranked[0][1]) - float(ranked[1][1])
        if margin < SCREENING_MARGIN_THRESHOLD:
            reasons.append(
                f"top two predictions are too close ({margin:.1%} margin < {SCREENING_MARGIN_THRESHOLD:.0%})"
            )
    elif not probs:
        reasons.append("probability distribution is unavailable")
    return reasons


def _normalize_label(label: str) -> str:
    label = (label or "").strip().lower()
    if label in ("retinal disease", "diabetic retinopathy"):
        return "retinal disease"
    return label


def _assess_multimodal_consistency(image_result: dict, fusion_result: dict) -> dict:
    image_label = image_result.get("diagnosis", "")
    fusion_label = fusion_result.get("diagnosis", "")
    image_conf = float(image_result.get("confidence", 0.0))
    fusion_conf = float(fusion_result.get("confidence", 0.0))
    labels_agree = _normalize_label(image_label) == _normalize_label(fusion_label)

    if labels_agree:
        status = "agreement"
        message = "Image-only and multimodal evidence point to the same supported condition."
    elif image_conf >= STRONG_CONFLICT_THRESHOLD and fusion_conf >= STRONG_CONFLICT_THRESHOLD:
        status = "conflict"
        message = "Image evidence and symptom-influenced fusion evidence strongly disagree."
    else:
        status = "uncertain"
        message = "The evidence is mixed or not confident enough for a reliable screening result."

    return {
        "status": status,
        "message": message,
        "image_label": image_label,
        "fusion_label": fusion_label,
        "image_confidence": image_conf,
        "fusion_confidence": fusion_conf,
    }


def _uncertain_screening_response(reason: str, image_result: dict = None,
                                  fusion_result: dict = None,
                                  symptoms: str = "") -> str:
    lines = [
        "OcuAI Screening Support Result",
        "",
        "Screening Status: Uncertain / unsupported",
        "",
        f"Reason: {reason}",
        "",
        "This is not a definitive medical diagnosis. The system is designed as a research prototype for screening support and patient education.",
    ]

    if symptoms:
        lines.extend([
            "",
            "Reported Symptoms:",
            symptoms,
        ])

    if image_result:
        lines.extend([
            "",
            "Image-only model evidence:",
            f"- Top result: {image_result.get('diagnosis', 'Unavailable')} ({float(image_result.get('confidence', 0.0)):.1%})",
            _top_probabilities(image_result),
        ])

    if fusion_result:
        lines.extend([
            "",
            "Image + symptom fusion evidence:",
            f"- Top result: {fusion_result.get('diagnosis', 'Unavailable')} ({float(fusion_result.get('confidence', 0.0)):.1%})",
            _top_probabilities(fusion_result),
        ])

    lines.extend([
        "",
        "Recommended action:",
        "- Do not rely on this output as a diagnosis.",
        "- Use a valid medical eye image such as a fundus/retinal scan when image screening is required.",
        "- If symptoms are sudden, severe, painful, or involve vision loss, seek urgent ophthalmology care.",
        "- For non-urgent symptoms, consult a licensed eye-care professional for an in-person evaluation.",
    ])
    return "\n".join(lines)


def _triage_prefix(user_message: str) -> str:
    if _has_urgent_symptom_text(user_message):
        urgency = "Urgency flag: Possible urgent symptom mentioned. Prompt in-person ophthalmology care is recommended."
    else:
        urgency = "Urgency flag: No automatic emergency symptom detected from text alone."
    return (
        "Text-only triage mode\n"
        "No medical eye image was provided, so OcuAI cannot perform image-based screening. "
        "This response is educational triage support, not a diagnosis.\n"
        f"{urgency}\n\n"
        "---\n\n"
    )


def _doc_source_label(doc, index: int) -> str:
    metadata = getattr(doc, "metadata", {}) or {}
    source = metadata.get("source") or "Knowledge base document"
    page = metadata.get("page")
    if isinstance(page, int) or (isinstance(page, str) and page.isdigit()):
        return f"[{index}] {os.path.basename(str(source))}, page {int(page) + 1}"
    return f"[{index}] {os.path.basename(str(source))}"


def _format_retrieved_evidence(docs) -> str:
    if not docs:
        return (
            "\n\n---\n"
            "Knowledge Base Evidence\n"
            "No retrieved knowledge-base passages were returned for this question."
        )

    lines = [
        "\n\n---",
        "Knowledge Base Evidence",
        "Retrieved passages used for source-grounded answering:",
    ]
    for idx, doc in enumerate(docs, 1):
        snippet = " ".join((getattr(doc, "page_content", "") or "").split())
        if len(snippet) > MAX_EVIDENCE_CHARS:
            snippet = snippet[:MAX_EVIDENCE_CHARS].rstrip() + "..."
        lines.extend([
            "",
            _doc_source_label(doc, idx),
            snippet,
        ])
    return "\n".join(lines)


def _format_docs_for_prompt(docs) -> str:
    blocks = []
    for idx, doc in enumerate(docs or [], 1):
        label = _doc_source_label(doc, idx)
        blocks.append(f"[{idx}] Source: {label}\n{getattr(doc, 'page_content', '')}")
    return "\n\n".join(blocks) if blocks else "No relevant OcuCare knowledge-base context was retrieved."


def _retrieve_evidence_for_query(user_message: str):
    if not retriever:
        return []
    optimized = user_message
    if query_optimizer:
        try:
            optimized = query_optimizer.invoke({"input": user_message})
        except Exception as e:
            print(f"[RAG] Query optimizer failed for evidence retrieval: {e}")
    docs = retriever.invoke(optimized)
    print(f"[RAG] Retrieved {len(docs)} evidence docs for text-only answer.")
    return docs


def _explain_diagnosis(diagnosis: str, confidence: float, model_type: str,
                       patient_symptoms: str = "") -> str:
    """
    Takes raw model prediction and generates a doctor-formatted, explainable
    report by:
      1. Retrieving relevant disease context from the Pinecone knowledge base.
      2. Invoking Gemini (diagnosis_chain) with the structured diagnosis prompt.
    Falls back to a simple text summary if the chain is unavailable.
    """
    # ── Fallback if LLM chain is not ready ───────────────────────────────────
    if not diagnosis_chain:
        lines = [
            f"**Diagnosis:** {diagnosis}",
            f"**Confidence:** {confidence:.2%}",
            f"\n*Analyzed via {model_type}.*",
        ]
        if patient_symptoms:
            lines.insert(2, f"**Reported Symptoms:** {patient_symptoms}")
        return "\n".join(lines)

    try:
        # ── Step 1: Retrieve KB context for the predicted disease ─────────────
        context = ""
        if retriever:
            query = f"{diagnosis} eye disease symptoms causes treatment ophthalmology"
            try:
                docs = retriever.invoke(query)
                context = "\n\n".join(doc.page_content for doc in docs)
                print(f"[Diagnosis] Retrieved {len(docs)} KB docs for '{diagnosis}'.")
            except Exception as re:
                print(f"[Diagnosis] KB retrieval failed: {re}")
                context = "Knowledge base context unavailable."
        else:
            context = "Knowledge base not connected."

        # ── Step 2: Build the symptoms section ────────────────────────────────
        symptoms_section = ""
        if patient_symptoms:
            symptoms_section = f"  Patient Reported Symptoms: {patient_symptoms}\n"

        # ── Step 3: Invoke Gemini with the diagnosis prompt ───────────────────
        print(f"[Diagnosis] Generating Gemini report for '{diagnosis}' ({confidence:.2%})...")
        payload = {
            "diagnosis": diagnosis,
            "confidence": f"{confidence:.1%}",
            "model_type": model_type,
            "symptoms_section": symptoms_section,
            "context": context,
        }
        response = diagnosis_chain.invoke(payload)

        required_sections = (
            "What This Condition Means",
            "Why The Model May Have Predicted This",
            "Common Symptoms",
            "Causes And Risk Factors",
            "Treatment And Management",
            "Clinical Recommendation",
        )
        if len(str(response)) < 900 or not all(section in str(response) for section in required_sections):
            print("[Diagnosis] Short/incomplete report detected. Retrying once...")
            response = diagnosis_chain.invoke(payload)

        print(f"[Diagnosis] Report generated ({len(response)} chars).")
        return response

    except Exception as e:
        traceback.print_exc()
        err = str(e)[:150]
        return (
            f"**Diagnosis:** {diagnosis}\n"
            f"**Confidence:** {confidence:.2%}\n\n"
            f"*Analyzed via {model_type}.*\n\n"
            f"⚠️ Detailed explanation unavailable: {err}"
        )


print("\n[READY] Flask server initializing...\n")

# ── Routes ────────────────────────────────────────────────────────────────────
def _has_react_frontend():
    return os.path.exists(os.path.join(FRONTEND_DIST, "index.html"))


def _extract_json_object(raw_text: str) -> dict:
    text = str(raw_text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _fallback_patient_summary(messages: list) -> dict:
    user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
    recent = " ".join(user_messages[-4:]).strip()
    return {
        "summary_text": (
            "This is an automatic non-diagnostic summary of recent eye-health chats. "
            + (f"Recent patient-reported concerns include: {recent[:500]}" if recent else "No patient concerns were found yet.")
        ),
        "symptoms": [],
        "topics": [],
        "red_flags": [],
        "image_history": [],
        "recommended_next_steps": [
            "Use this summary only as a preparation aid for professional eye care.",
            "Seek urgent care for sudden vision loss, severe pain, trauma, chemical exposure, flashes, floaters, or curtain-like vision changes.",
        ],
        "safety_note": "This is not a diagnosis. It summarizes user-reported information and AI screening-support outputs.",
    }


@app.route("/app/<path:filename>")
def react_assets(filename):
    if _has_react_frontend():
        return send_from_directory(FRONTEND_DIST, filename)
    return ("React frontend has not been built yet.", 404)


@app.route("/")
def index():
    if _has_react_frontend():
        return send_from_directory(FRONTEND_DIST, "index.html")
    return render_template("chat.html")

@app.route("/bot")
def bot_page():
    if _has_react_frontend():
        return send_from_directory(FRONTEND_DIST, "index.html")
    return render_template("chatbot_page.html")

@app.route("/health")
def health():
    return {
        "status": "running",
        "embeddings": embeddings is not None,
        "retriever": retriever is not None,
        "chatModel": chatModel is not None,
        "rag_chain": rag_chain is not None,
    }


@app.route("/summary", methods=["POST"])
def patient_summary():
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages") or []
    if not isinstance(messages, list):
        return jsonify({"error": "messages must be a list"}), 400

    cleaned = []
    for item in messages[-120:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role") if item.get("role") in ("user", "assistant") else "unknown"
        content = str(item.get("content") or "")[:1800]
        image_note = " [image uploaded]" if item.get("image_present") else ""
        if content or image_note:
            cleaned.append({"role": role, "content": content + image_note})

    if not cleaned:
        return jsonify(_fallback_patient_summary([]))

    if not chatModel:
        return jsonify(_fallback_patient_summary(cleaned))

    transcript = "\n".join(
        f"{item['role'].upper()}: {item['content']}" for item in cleaned
    )[:14000]

    prompt = f"""
You are generating an automatic Eye Health Summary for a logged-in user of OcuCare.

Rules:
- This is NOT a medical diagnosis.
- Summarize only what appears in the transcript.
- Do not invent patient demographics, diseases, test results, doctors, hospitals, or appointments.
- Use cautious language: "reported", "discussed", "screening support", "may need".
- If urgent symptoms are present, include them in red_flags and recommended_next_steps.
- Return ONLY valid JSON. No markdown.

JSON shape:
{{
  "summary_text": "short patient-friendly paragraph",
  "symptoms": ["reported symptoms or concerns"],
  "topics": ["eye-health topics or conditions discussed"],
  "red_flags": ["urgent warning signs mentioned, or empty array"],
  "image_history": ["image upload/screening notes, or empty array"],
  "recommended_next_steps": ["safe next steps"],
  "safety_note": "This is not a diagnosis..."
}}

Transcript:
{transcript}
"""

    try:
        response = chatModel.invoke(prompt)
        content = getattr(response, "content", response)
        data = _extract_json_object(str(content))
        fallback = _fallback_patient_summary(cleaned)
        return jsonify({
            "summary_text": str(data.get("summary_text") or fallback["summary_text"]),
            "symptoms": data.get("symptoms") if isinstance(data.get("symptoms"), list) else [],
            "topics": data.get("topics") if isinstance(data.get("topics"), list) else [],
            "red_flags": data.get("red_flags") if isinstance(data.get("red_flags"), list) else [],
            "image_history": data.get("image_history") if isinstance(data.get("image_history"), list) else [],
            "recommended_next_steps": data.get("recommended_next_steps") if isinstance(data.get("recommended_next_steps"), list) else fallback["recommended_next_steps"],
            "safety_note": str(data.get("safety_note") or fallback["safety_note"]),
        })
    except Exception as e:
        print(f"[Summary ERROR] {e}")
        traceback.print_exc()
        return jsonify(_fallback_patient_summary(cleaned))


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg        = request.form.get("msg", "").strip()
    image_file = request.files.get("image")

    print(f"[/get] msg={repr(msg)}, image={'yes' if image_file and image_file.filename else 'no'}")

    # ── Image upload path ─────────────────────────────────────────────────
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)

        if msg:
            # Image + Text -> cross-check image-only evidence against fusion.
            try:
                image_res = predict_cnn(filepath)
                if image_res['diagnosis'].startswith("CNN Error"):
                    return f"⚠️ CNN inference error: {image_res['diagnosis']}"

                fusion_res = predict_fusion(filepath, msg)
                if fusion_res['diagnosis'].startswith("Fusion Error"):
                    return f"⚠️ Fusion inference error: {fusion_res['diagnosis']}"

                consistency = _assess_multimodal_consistency(image_res, fusion_res)
                if _has_urgent_symptom_text(msg):
                    reason = (
                        "Urgent symptom text was reported. Emergency red-flag symptoms should not be overridden "
                        "by a normal or agreeing image-screening result. "
                        f"Image-only result: {consistency['image_label']} "
                        f"({consistency['image_confidence']:.1%}); "
                        f"fusion result: {consistency['fusion_label']} "
                        f"({consistency['fusion_confidence']:.1%})."
                    )
                    return _uncertain_screening_response(
                        reason=reason,
                        image_result=image_res,
                        fusion_result=fusion_res,
                        symptoms=msg,
                    )

                if consistency["status"] != "agreement" or _is_uncertain(fusion_res) or _is_uncertain(image_res):
                    uncertainty_bits = []
                    image_uncertainty = "; ".join(_uncertainty_reasons(image_res))
                    fusion_uncertainty = "; ".join(_uncertainty_reasons(fusion_res))
                    if image_uncertainty:
                        uncertainty_bits.append(f"Image model uncertainty: {image_uncertainty}")
                    if fusion_uncertainty:
                        uncertainty_bits.append(f"Fusion uncertainty: {fusion_uncertainty}")
                    reason = (
                        f"{consistency['message']} "
                        f"Image-only result: {consistency['image_label']} "
                        f"({consistency['image_confidence']:.1%}); "
                        f"fusion result: {consistency['fusion_label']} "
                        f"({consistency['fusion_confidence']:.1%})."
                    )
                    if uncertainty_bits:
                        reason += " " + " ".join(f"{bit}." for bit in uncertainty_bits)
                    return _uncertain_screening_response(
                        reason=reason,
                        image_result=image_res,
                        fusion_result=fusion_res,
                        symptoms=msg,
                    )

                symptoms_with_crosscheck = (
                    f"{msg}\n"
                    f"Image-only cross-check agreed: {image_res['diagnosis']} "
                    f"({image_res['confidence']:.1%})."
                )
                return _explain_diagnosis(
                    diagnosis=fusion_res['diagnosis'],
                    confidence=fusion_res['confidence'],
                    model_type="Multi-Modal Fusion (InceptionV3 + BERT) with image-only consistency check",
                    patient_symptoms=symptoms_with_crosscheck,
                )
            except Exception as e:
                traceback.print_exc()
                return f"⚠️ Fusion inference error: {str(e)}"
        else:
            # Image only → CNN → Gemini doctor report
            try:
                res = predict_cnn(filepath)
                if res['diagnosis'].startswith("CNN Error"):
                    return f"⚠️ CNN inference error: {res['diagnosis']}"
                if _is_uncertain(res):
                    uncertainty_note = "; ".join(_uncertainty_reasons(res))
                    return _uncertain_screening_response(
                        reason=f"The image-only model is uncertain: {uncertainty_note}.",
                        image_result=res,
                    )
                return _explain_diagnosis(
                    diagnosis=res['diagnosis'],
                    confidence=res['confidence'],
                    model_type="Vision CNN (Keras/TensorFlow)",
                )
            except Exception as e:
                traceback.print_exc()
                return f"⚠️ CNN inference error: {str(e)}"

    # ── Text-only path → RAG (with Gemini direct fallback) ──────────────
    if msg:
        if rag_chain:
            try:
                safe_msg = msg.encode('ascii', errors='replace').decode()
                print(f"[RAG] Querying: {safe_msg}")
                docs = _retrieve_evidence_for_query(msg)
                response = rag_chain.invoke({
                    "input": msg,
                    "context": _format_docs_for_prompt(docs),
                })
                safe_resp = response[:100].encode('ascii', errors='replace').decode()
                print(f"[RAG] Response (KB): {safe_resp}...")
                return _triage_prefix(msg) + str(response) + _format_retrieved_evidence(docs)
            except Exception as rag_err:
                # Pinecone / network failure — fall back to direct Gemini
                err_str = str(rag_err)
                is_network_err = any(k in err_str for k in (
                    "getaddrinfo", "MaxRetry", "NameResolution",
                    "ConnectionError", "Timeout", "ConnectTimeout"
                ))
                if is_network_err and direct_chain:
                    print(f"[RAG] Pinecone unreachable, falling back to direct Gemini...")
                    try:
                        response = direct_chain.invoke(msg)
                        print(f"[RAG] Response (direct Gemini): {response[:80].encode('ascii', errors='replace').decode()}...")
                        return _triage_prefix(msg) + str(response) + "\n\n---\n⚠️ *OcuCare Knowledge Base is temporarily offline. This response is from OcuAI general knowledge only. Citations are unavailable.*"
                    except Exception as direct_err:
                        print(f"[Direct Gemini ERROR] {direct_err}")
                        return "Sorry, I could not reach OcuAI at this time. Please check your internet connection."
                else:
                    import io
                    buf = io.StringIO()
                    traceback.print_exc(file=buf)
                    print(f"[RAG ERROR] {buf.getvalue().encode('ascii', errors='replace').decode()}")
                    return f"Sorry, I encountered an error. Please try again."

        elif direct_chain:
            # rag_chain never built (no Pinecone) — use Gemini directly
            print(f"[Direct] No RAG chain, using direct Gemini for: {msg[:60]}")
            try:
                response = direct_chain.invoke(msg)
                return _triage_prefix(msg) + str(response) + "\n\n---\n⚠️ *OcuCare Knowledge Base not connected. Response from OcuAI general knowledge. Citations are unavailable.*"
            except Exception as e:
                return f"Sorry, OcuAI is unavailable: {str(e)[:100]}"
        else:
            return "The AI assistant is not available right now. Please check server logs."

    return "No input provided."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5051"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"[READY] Serving on http://{host}:{port}")
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except OSError as e:
        print(f"[ERROR] Could not start server on {host}:{port}: {e}")
        print("[HELP] Try another local port, for example:")
        print("       $env:HOST='127.0.0.1'; $env:PORT='5052'; python app.py")
