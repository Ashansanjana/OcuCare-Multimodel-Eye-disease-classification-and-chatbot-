from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from langchain_core.documents import Document

# Extract text from PDF files
def load_pdf_file(data):
    """
    Load all PDF files from a directory using PyPDFLoader.
    Returns a list of Document objects.
    """
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents


def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Keep only page_content + source metadata for each Document.
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        page = doc.metadata.get("page")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src, "page": page}
            )
        )
    return minimal_docs


# Split the documents into smaller chunks
def text_split(minimal_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
    )
    texts_chunk = text_splitter.split_documents(minimal_docs)
    return texts_chunk


def download_hugging_face_embeddings():
    """
    Load the HuggingFace sentence-transformer embeddings model.
    Tries a normal (online-aware) load first; if the network is unavailable,
    falls back to the locally cached model so the server starts cleanly offline.
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Attempt 1: standard load (uses cache, updates from Hub if reachable) ──
    try:
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        return embeddings
    except Exception as online_err:
        print(f"[helper] Online load failed ({type(online_err).__name__}). "
              "Retrying with local cache only...")

    # ── Attempt 2: force local-only from Hugging Face cache ──────────────────
    import os
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"local_files_only": True},
    )
    print("[helper] Embeddings loaded from local cache (offline mode).")
    return embeddings
