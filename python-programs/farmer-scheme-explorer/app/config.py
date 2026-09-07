import os

from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_CHAT_MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

FAISS_INDEX_PATH = os.getenv(
    "FAISS_INDEX_PATH",
    "vectorstore/faiss_index",
)

TOP_K = int(
    os.getenv("TOP_K", "2")
)


if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is not configured. "
        "Please add it to the .env file."
    )