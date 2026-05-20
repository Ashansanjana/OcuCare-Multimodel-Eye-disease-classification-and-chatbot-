# 👁️ OcuCare: Multimodal Eye Disease Classification & RAG Chatbot (OcuAI)

OcuCare is a premium, state-of-the-art multimodal artificial intelligence platform designed to aid in the diagnosis, classification, and understanding of various ophthalmic (eye) diseases. By fusing medical images, symptom text, and structured medical literature retrieval, OcuCare provides precise ocular insights through three operational modes:

1. **RAG-Powered Chatbot (OcuAI)**: Retrieves knowledge from curated ophthalmology PDFs to answer text questions using a Retrieval-Augmented Generation (RAG) framework with Pinecone and Google's Gemini LLM.
2. **Vision CNN Diagnosis**: Leverages a deep CNN model to analyze fundus eye images directly and classify them into four categories: Cataract, Diabetic Retinopathy, Glaucoma, or Normal.
3. **Multimodal Fusion Classifier**: Fuses fundus images and textual symptom descriptions using a deep learning pipeline (combining InceptionV3 and BERT embeddings) to perform joint inference.

---

## 🚀 Key Features
- 🧠 **Multi-Modal Diagnostics**: Combine visual fundus details with natural language descriptions of patient symptoms for balanced diagnostic reports.
- 📚 **Vector-Search RAG**: Cleaned medical PDFs are split, embedded using HuggingFace sentence-transformers (`all-MiniLM-L6-v2`), and indexed on a serverless AWS Pinecone index for lightning-fast semantic retrieval.
- 📡 **Space-Mission Themed AI (OcuAI)**: Offers a precise, authoritative, yet warm response profile following specialized eye-health boundaries, prioritizing user safety by flagging critical conditions for immediate ground specialist consultation.
- ⚡ **Lazy Inference Architecture**: The Flask backend loads heavy TensorFlow, PyTorch, and NLP models lazily and strictly sequences imports to prevent memory/NumPy conflicts.

---

## 🛠️ Technology Stack
- **Core App Framework**: Flask (Python)
- **Large Language Model (LLM)**: Gemini via `langchain-google-genai`
- **Vector Database**: Pinecone Serverless (AWS `us-east-1`)
- **Text Embeddings**: HuggingFace Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Deep Learning & Computer Vision**:
  - TensorFlow & Keras (Custom CNN Model & InceptionV3 feature extraction)
  - PyTorch (InceptionV3 image projection + BERT-uncased text classification)
  - HuggingFace Transformers (BERT Tokenization)
- **PDF Extraction**: `pypdf`, LangChain Directory Loaders

---

## 📁 Project Architecture & Directory Structure
```filepath
Medical-chatbot/
│
├── Bert_Models/              # PyTorch multimodal models
│   ├── fusion_classifier.pth # Saved state dict for multimodal model
│   └── diagnosis_map.json    # Map from class indexes to labels
│
├── CNN_models/               # Local CNN models (image-only)
│   └── my_model.keras        # Standalone Keras eye disease classifier
│
├── src/                      # Backend application modules
│   ├── helper.py             # Document loading, chunking, and embedding setup
│   ├── inference.py          # Vision CNN and BERT Multimodal inference pipelines
│   └── prompt.py             # System prompt boundaries for OcuAI
│
├── static/                   # Static UI assets (CSS, JS, custom styling)
├── templates/                # Frontend HTML structures
│   ├── chat.html             # Floating widget-style test chat page
│   └── chatbot_page.html     # Dedicated full-page terminal UI page
│
├── data/                     # Local data storage
│   ├── uploads/              # Uploaded user images (processed temporarily)
│   └── *.pdf                 # Medical literature PDF manuals used for indexing
│
├── app.py                    # Main Flask application entrypoint & API endpoints
├── store_index.py            # Extraction & Pinecone upload indexing pipeline
├── requirements.txt          # Precise package dependency tracking
└── .gitignore                # Optimized repository ignoring configurations
```

---

## 💻 Setup & Installation Instructions

Follow these steps to configure your development environment and launch the OcuCare platform locally.

### 1. Prerequisites
- Python **3.10** or **3.11** (recommended)
- Pip package manager
- A **Pinecone API Key** and a **Google Gemini API Key**

### 2. Environment Configuration
Create a `.env` file in the root of the workspace containing your operational API keys:
```env
PINECONE_API_KEY=your_pinecone_api_key
GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Install Dependencies
Run the installation command within your virtual environment:
```bash
pip install -r requirements.txt
```

### 4. Build/Populate the Pinecone Vector Store
To load your custom ophthalmology PDF textbooks or brochures from the `data/` folder and populate your Pinecone database:
```bash
python store_index.py
```

### 5. Launch the Flask Server
Fire up the application server to host the interactive interface:
```bash
python app.py
```
Open your web browser and navigate to `http://localhost:8080` to experience the premium interface.

---

## 🧪 Verification and Testing Scripts
The repository includes several validation scripts inside the root to test functional units separately:
- `test_pinecone.py`: Tests the connection and vector retriever with Pinecone.
- `test_gemini.py` / `test_gemini2.py` / `test_gemini3.py`: Validates LLM completion interfaces using the Gemini developer API.
- `test_predict.py`: Evaluates local CNN model execution against mock matrices to verify target output logits and classification states.
- `test_import.py`: Ensures heavy model imports don't collide or cause broken environment loops.

---

## ⚠️ Medical Disclaimer
*OcuCare is a demonstration of multimodal machine learning techniques and does not constitute formal medical software. All model inference and LLM chat completions are intended strictly for educational, research, and informational discovery. Users should always consult a licensed ground specialist or doctor for ocular medical diagnoses.*