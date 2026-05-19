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

        rag_chain = (
            {
                "context": retriever | format_docs,
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
            # Image + Text → Fusion
            try:
                res = predict_fusion(filepath, msg)
                return (
                    f"**Diagnosis:** {res['diagnosis']}\n"
                    f"**Confidence:** {res['confidence']:.2%}\n\n"
                    f"*Analyzed via Multi-Modal Fusion Model.*"
                )
            except Exception as e:
                return f"Fusion inference error: {str(e)}"
        else:
            # Image only → CNN
            try:
                res = predict_cnn(filepath)
                return (
                    f"**Diagnosis:** {res['diagnosis']}\n"
                    f"**Confidence:** {res['confidence']:.2%}\n\n"
                    f"*Analyzed via Vision CNN Model.*"
                )
            except Exception as e:
                return f"CNN inference error: {str(e)}"

    # ── Text-only path → RAG ──────────────────────────────────────────────
    if msg:
        if rag_chain:
            try:
                safe_msg = msg.encode('ascii', errors='replace').decode()
                print(f"[RAG] Querying: {safe_msg}")
                response = rag_chain.invoke(msg)
                safe_resp = response[:100].encode('ascii', errors='replace').decode()
                print(f"[RAG] Response: {safe_resp}...")
                return str(response)
            except Exception as e:
                import io
                buf = io.StringIO()
                traceback.print_exc(file=buf)
                tb_str = buf.getvalue().encode('ascii', errors='replace').decode()
                print(f"[RAG ERROR] {tb_str}")
                return f"Sorry, I encountered an error. Please try again."
        else:
            return "The AI assistant is not available right now. Please check server logs."

    return "No input provided."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
