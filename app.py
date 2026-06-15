from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import sys
import traceback

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
            max_output_tokens=1024
        )
        print("[OK] Gemini model ready.")
    except Exception as e:
        print(f"[WARN] Gemini model failed: {e}")
        traceback.print_exc()
else:
    print("[SKIP] Gemini skipped (no GOOGLE_API_KEY).")

# ── RAG Chain ─────────────────────────────────────────────────────────────────
rag_chain = None
if retriever and chatModel:
    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough
        from src.prompt import system_prompt

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

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

        rag_chain = (
            {
                "context": query_optimizer | retriever | format_docs,
                "input": RunnablePassthrough()
            }
            | prompt
            | chatModel
            | StrOutputParser()
        )
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
        response = diagnosis_chain.invoke({
            "diagnosis": diagnosis,
            "confidence": f"{confidence:.1%}",
            "model_type": model_type,
            "symptoms_section": symptoms_section,
            "context": context,
        })
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
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/bot")
def bot_page():
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

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg        = request.form.get("msg", "").strip()
    image_file = request.files.get("image")

    print(f"[/get] msg={repr(msg)}, image={'yes' if image_file and image_file.filename else 'no'}")

    # ── Image upload path ─────────────────────────────────────────────────
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)

        if msg:
            # Image + Text → Fusion → Gemini doctor report
            try:
                res = predict_fusion(filepath, msg)
                if res['diagnosis'].startswith("Fusion Error"):
                    return f"⚠️ Fusion inference error: {res['diagnosis']}"
                return _explain_diagnosis(
                    diagnosis=res['diagnosis'],
                    confidence=res['confidence'],
                    model_type="Multi-Modal Fusion (InceptionV3 + BERT)",
                    patient_symptoms=msg,
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
                response = rag_chain.invoke(msg)
                safe_resp = response[:100].encode('ascii', errors='replace').decode()
                print(f"[RAG] Response (KB): {safe_resp}...")
                return str(response)
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
                        return str(response) + "\n\n---\n⚠️ *OcuCare Knowledge Base is temporarily offline. This response is from OcuAI general knowledge only.*"
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
                return str(response) + "\n\n---\n⚠️ *OcuCare Knowledge Base not connected. Response from OcuAI general knowledge.*"
            except Exception as e:
                return f"Sorry, OcuAI is unavailable: {str(e)[:100]}"
        else:
            return "The AI assistant is not available right now. Please check server logs."

    return "No input provided."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
