# Local PDF RAG Application

A completely local Retrieval Augmented Generation (RAG)
application using:

- Python
- LangChain
- ChromaDB
- HuggingFace Embeddings
- Ollama
- Qwen 2.5
- PyPDF

## Architecture

PDF
↓
PyPDFLoader
↓
Text Chunking
↓
HuggingFace Embeddings
↓
Chroma Vector Database
↓
Retriever
↓
Ollama Qwen LLM
↓
Answer

## Installation

Install dependencies:

pip install -r requirements.txt

## Install Ollama Model

ollama pull qwen2.5:3b

## Ingestion

Place the PDF inside:

data/What_Is_AI_Encylopedia.pdf

Run:

python src/ingest.py

## Run Application

python src/main.py

## Example

Question:

What is strong AI?

The application retrieves relevant chunks
from the local Chroma database and sends
the retrieved context to the local Qwen model.

## Storage

Vector database:

faiss_db/

No external vector database is required.

## Privacy

PDF documents, embeddings, retrieved chunks,
and LLM processing remain local when using
local HuggingFace embeddings and Ollama.