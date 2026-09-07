# 🌾 Farmer Scheme RAG Application

A Retrieval-Augmented Generation (RAG) application that allows users to ask natural-language questions about farmer and agriculture schemes stored in an Excel file.

The application uses **LangChain** for the RAG pipeline, **FAISS** as a local vector database, and **OpenAI** for embeddings and ChatGPT-based answer generation.

## Architecture

```text
Excel Scheme Data
       │
       ▼
  Data Ingestion
       │
       ▼
OpenAI Embeddings
       │
       ▼
 Local FAISS DB
       │
       ▼
Semantic Retrieval
       │
       ▼
   OpenAI ChatGPT
       │
       ▼
Grounded Scheme Answer
       │
       ▼
 Streamlit / REST API
```

## Technology Stack

- Python
- LangChain
- OpenAI ChatGPT
- OpenAI Embeddings
- FAISS
- Pandas / OpenPyXL
- FastAPI
- Streamlit

## Key Features

- Read farmer scheme information from Excel
- Convert scheme records into searchable documents
- Generate embeddings using OpenAI
- Store embeddings locally using FAISS
- Retrieve relevant schemes using semantic search
- Generate answers using OpenAI ChatGPT
- Provide REST API using FastAPI
- Provide interactive chat UI using Streamlit
- Display retrieved scheme sources
- Prevent answers from being generated outside the available scheme data

## Project Flow

### 1. Data Ingestion

Run:

```bash
python ingest.py
```

This reads:

```text
data/TN_Agri_GoScheme.xlsx
```

and creates the local FAISS vector database:

```text
vectorstore/faiss_index/
```

### 2. Start FastAPI

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

### 3. Start Streamlit

```bash
streamlit run streamlit_app.py
```

Users can then ask questions such as:

```text
What schemes are available for farmers?

What are the eligibility criteria?

What documents are required?

Which schemes are related to agricultural mechanisation?
```

## RAG Approach

Each farmer scheme is stored as a complete document containing:

- Scheme Name
- Department
- Scheme Description
- Eligibility Criteria
- Documents Required
- GO & Guidelines

When a user asks a question, the application retrieves the most relevant scheme records from the local FAISS database and provides them as context to ChatGPT.

This helps produce **context-aware and grounded answers based on the Excel scheme data**.

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
FAISS_INDEX_PATH=vectorstore/faiss_index
TOP_K=5
```

## Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI

Create `.env`:

```text
OPENAI_API_KEY=your-api-key
```

### 3. Build FAISS index

```bash
python ingest.py
```

### 4. Start FastAPI

```bash
uvicorn app.main:app --reload
```

### 5. Start Streamlit

```bash
streamlit run streamlit_app.py
```

The application retrieves relevant information from the farmer-scheme knowledge base and generates answers based on the retrieved context.

## Important

The **scheme data and FAISS vector database are stored locally**. OpenAI is used for embedding generation and natural-language answer generation.
