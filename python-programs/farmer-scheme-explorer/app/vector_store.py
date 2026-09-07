from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import (
    OPENAI_EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
)


def create_embeddings():
    """
    Create OpenAI embedding model.
    """

    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL
    )


def create_faiss_index(documents):
    """
    Create FAISS vector store from documents
    and persist it locally.
    """

    embeddings = create_embeddings()

    vector_store = FAISS.from_documents(
        documents,
        embeddings,
    )

    index_path = Path(FAISS_INDEX_PATH)

    index_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        str(index_path)
    )

    return vector_store


def load_faiss_index():
    """
    Load an existing local FAISS index.
    """

    index_path = Path(FAISS_INDEX_PATH)

    if not index_path.exists():
        raise FileNotFoundError(
            "FAISS index not found. "
            "Run: python ingest.py"
        )

    embeddings = create_embeddings()

    vector_store = FAISS.load_local(
        str(index_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store