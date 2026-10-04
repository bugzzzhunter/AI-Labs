import shutil
from pathlib import Path

import streamlit as st

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

from ingest import ingest_file


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).parent

DB_DIR = BASE_DIR / "chroma_db"
UPLOAD_DIR = BASE_DIR / "uploads"
SEED_DIR = BASE_DIR / "seed_data"

SEED_FILE = SEED_DIR / "company.txt"

COLLECTION_NAME = "rag_security_lab"

TOP_K = 10


UPLOAD_DIR.mkdir(
    exist_ok=True
)

SEED_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# MODELS
# ============================================================

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


@st.cache_resource
def get_llm():

    return OllamaLLM(
        model="llama3.2"
    )


# ============================================================
# VECTOR STORE
# ============================================================

def get_vectorstore():

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=get_embeddings(),
    )


# ============================================================
# INITIALIZE SEED DATA
# ============================================================

def initialize_seed_data():

    vectorstore = get_vectorstore()

    existing = vectorstore.get(
        limit=1
    )

    if existing and existing.get("ids"):

        return

    if not SEED_FILE.exists():

        raise FileNotFoundError(
            f"Seed file not found: {SEED_FILE}"
        )

    ingest_file(
        path=SEED_FILE,
        vectorstore=vectorstore,
        is_seed=True,
    )


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_documents(
    question: str,
    top_k: int = TOP_K,
):

    vectorstore = get_vectorstore()

    return vectorstore.similarity_search_with_score(
        question,
        k=top_k,
    )


# ============================================================
# GENERATE ANSWER
# ============================================================

def answer_question(question, results):

    context_parts = []

    for document, score in results:

        source = document.metadata.get(
            "source",
            "unknown",
        )

        is_seed = document.metadata.get(
            "is_seed",
            False,
        )

        document_type = (
            "SEED"
            if is_seed
            else "UPLOADED"
        )

        context_parts.append(
            f"""
SOURCE: {source}
TYPE: {document_type}
SIMILARITY SCORE: {score:.4f}

{document.page_content}
"""
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful assistant.

Answer the question using the retrieved context.

The context may contain information from both
trusted seed documents and user-uploaded documents.

Do not invent information that is not present
in the retrieved context.

Context:

{context}

Question:

{question}

Answer:
"""
    )

    llm = get_llm()

    answer = llm.invoke(
        prompt.format(
            context=context,
            question=question,
        )
    )

    return answer, context


# ============================================================
# RESET
# ============================================================

def reset_knowledge_base():

    """
    Reset the knowledge base to seed data.

    We deliberately do NOT delete chroma_db itself.
    This avoids Windows file-locking problems.

    Instead:

        1. Delete all vectors.
        2. Delete uploaded files.
        3. Re-ingest the seed document.
    """

    vectorstore = get_vectorstore()

    # --------------------------------------------------------
    # Delete all vectors
    # --------------------------------------------------------

    existing = vectorstore.get()

    ids = existing.get(
        "ids",
        []
    )

    if ids:

        vectorstore.delete(
            ids=ids
        )

    # --------------------------------------------------------
    # Delete uploaded files
    # --------------------------------------------------------

    if UPLOAD_DIR.exists():

        for item in UPLOAD_DIR.iterdir():

            if item.is_file():

                item.unlink()

            elif item.is_dir():

                shutil.rmtree(
                    item
                )

    UPLOAD_DIR.mkdir(
        exist_ok=True
    )

    # --------------------------------------------------------
    # Restore seed data
    # --------------------------------------------------------

    if not SEED_FILE.exists():

        raise FileNotFoundError(
            f"Seed file not found: {SEED_FILE}"
        )

    ingest_file(
        path=SEED_FILE,
        vectorstore=vectorstore,
        is_seed=True,
    )


# ============================================================
# DATABASE INFO
# ============================================================

def get_database_documents():

    vectorstore = get_vectorstore()

    return vectorstore.get()


def get_chunk_count():

    data = get_database_documents()

    return len(
        data.get(
            "ids",
            []
        )
    )

