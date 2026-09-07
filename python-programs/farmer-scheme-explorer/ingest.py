from app.excel_loader import load_excel
from app.vector_store import create_faiss_index


EXCEL_FILE = "data/TN_Agri_GoScheme.xlsx"


def main():

    print("=" * 60)
    print("Farmer Scheme RAG - Data Ingestion")
    print("=" * 60)

    print("\nReading Excel...")

    documents = load_excel(
        EXCEL_FILE
    )

    print(
        f"Loaded {len(documents)} schemes."
    )

    print("\nCreating FAISS vector database...")

    create_faiss_index(
        documents
    )

    print("\nFAISS database created successfully.")

    print(
        "\nVector database location:"
        " vectorstore/faiss_index"
    )

    print("\nIngestion completed.")


if __name__ == "__main__":
    main()