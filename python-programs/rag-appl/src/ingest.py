from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    PDF_FILE,
    FAISS_DB_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def load_pdf():

    if not PDF_FILE.exists():
        raise FileNotFoundError(
            f"PDF not found: {PDF_FILE}"
        )

    print()
    print("=" * 60)
    print("STEP 1 - LOAD PDF")
    print("=" * 60)

    loader = PyPDFLoader(
        str(PDF_FILE)
    )

    documents = loader.load()

    print(
        f"PDF: {PDF_FILE.name}"
    )

    print(
        f"Pages loaded: {len(documents)}"
    )

    return documents


def split_documents(documents):

    print()
    print("=" * 60)
    print("STEP 2 - SPLIT DOCUMENT")
    print("=" * 60)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    return chunks


def create_embeddings():

    print()
    print("=" * 60)
    print("STEP 3 - CREATE EMBEDDING MODEL")
    print("=" * 60)

    print(
        f"Embedding model: {EMBEDDING_MODEL}"
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    return embeddings


def create_faiss_database(
    chunks,
    embeddings
):

    print()
    print("=" * 60)
    print("STEP 4 - CREATE FAISS DATABASE")
    print("=" * 60)

    FAISS_DB_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    vector_store.save_local(
        str(FAISS_DB_DIR)
    )

    print(
        f"FAISS database saved to:"
    )

    print(
        FAISS_DB_DIR
    )

    return vector_store


def main():

    print()
    print("=" * 60)
    print("LOCAL PDF → FAISS INGESTION")
    print("=" * 60)

    documents = load_pdf()

    chunks = split_documents(
        documents
    )

    embeddings = create_embeddings()

    create_faiss_database(
        chunks,
        embeddings
    )

    print()
    print("=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()