from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from config import (
    FAISS_DB_DIR,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    TOP_K,
)


class PDFRAG:

    def __init__(self):

        print(
            "Loading local embedding model..."
        )

        # ----------------------------------------------------
        # Embedding Model
        # ----------------------------------------------------

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            },
        )

        # ----------------------------------------------------
        # Load Local FAISS Database
        # ----------------------------------------------------

        print(
            "Loading FAISS vector database..."
        )

        if not FAISS_DB_DIR.exists():

            raise FileNotFoundError(
                "FAISS database not found. "
                "Run ingest.py first."
            )

        self.vector_store = (
            FAISS.load_local(
                str(FAISS_DB_DIR),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        )

        # ----------------------------------------------------
        # Retriever
        # ----------------------------------------------------

        self.retriever = (
            self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": TOP_K
                },
            )
        )

        # ----------------------------------------------------
        # Local Ollama LLM
        # ----------------------------------------------------

        print(
            f"Loading Ollama model: "
            f"{OLLAMA_MODEL}"
        )

        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            temperature=0,
        )

        # ----------------------------------------------------
        # RAG Prompt
        # ----------------------------------------------------

        self.prompt = ChatPromptTemplate.from_template(
            """
You are a PDF question-answering assistant.

You must answer the question using ONLY
the context retrieved from the PDF.

Rules:

1. Do not use outside knowledge.
2. Do not hallucinate.
3. Do not make up information.
4. If the answer cannot be found in the
   provided context, respond exactly:

   "I could not find the answer in the provided PDF."

5. Give a clear and concise answer.
6. Preserve terminology used in the PDF.
7. Mention relevant page numbers when possible.

Context
=======
{context}
=======

Question
========
{question}
========

Answer:
"""
        )

    # ========================================================
    # RETRIEVE
    # ========================================================

    def retrieve(self, question):

        documents = self.retriever.invoke(
            question
        )

        return documents

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        documents
    ):

        context = []

        for document in documents:

            page = document.metadata.get(
                "page",
                "unknown"
            )

            source = document.metadata.get(
                "source",
                "unknown"
            )

            # PDF page numbers are zero-based
            # in LangChain metadata.
            display_page = (
                page + 1
                if isinstance(page, int)
                else page
            )

            context.append(
                f"""
Source: {source}
Page: {display_page}

{document.page_content}
"""
            )

        return "\n\n".join(
            context
        )

    # ========================================================
    # ASK QUESTION
    # ========================================================

    def ask(self, question):

        # ----------------------------------------------------
        # Retrieve relevant chunks
        # ----------------------------------------------------

        documents = self.retrieve(
            question
        )

        if not documents:

            return {
                "answer":
                    "I could not find the answer "
                    "in the provided PDF.",
                "sources": []
            }

        # ----------------------------------------------------
        # Build Context
        # ----------------------------------------------------

        context = self.build_context(
            documents
        )

        # ----------------------------------------------------
        # Create Prompt
        # ----------------------------------------------------

        messages = self.prompt.invoke(
            {
                "context": context,
                "question": question
            }
        )

        # ----------------------------------------------------
        # Call Local LLM
        # ----------------------------------------------------

        response = self.llm.invoke(
            messages
        )

        # ----------------------------------------------------
        # Build Sources
        # ----------------------------------------------------

        sources = []

        for document in documents:

            page = document.metadata.get(
                "page",
                "unknown"
            )

            if isinstance(page, int):
                page = page + 1

            source = document.metadata.get(
                "source",
                "unknown"
            )

            source_info = {
                "source": source,
                "page": page
            }

            if source_info not in sources:
                sources.append(
                    source_info
                )

        return {
            "answer": response.content,
            "sources": sources
        }