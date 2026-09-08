# 🎓 Knowledge Graph–Enhanced Hybrid RAG for Entrance Exam Intelligence

A **Knowledge Graph–Enhanced Hybrid Retrieval-Augmented Generation (RAG)** application built with **Python, LangChain, OpenAI, FAISS, NetworkX, and Streamlit**.

The project demonstrates how **Vector RAG + Knowledge Graph retrieval** can be combined to build a more contextual and relationship-aware GenAI application.

---

## 🚀 Project Overview

This project converts an entrance-exam information PDF into two complementary knowledge representations:

1. **Vector Knowledge**

   * PDF documents are split into chunks.
   * Chunks are converted into embeddings.
   * Embeddings are stored in a local **FAISS vector database**.
   * Semantic similarity search retrieves relevant document content.

2. **Graph Knowledge**

   * Important entities such as entrance exams, courses, categories, and institutions are represented as nodes.
   * Relationships between entities are represented as graph edges.
   * The graph enables relationship-based retrieval.

Both retrieval mechanisms are combined before sending the context to the **OpenAI LLM**.

### Core Architecture

```text
                         ┌─────────────────────┐
                         │       PDF           │
                         │ Entrance Exam Data  │
                         └──────────┬──────────┘
                                    │
                          Document Loading
                                    │
                          Text Splitting
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
             Embedding Generation          Entity Extraction
                     │                             │
                     ▼                             ▼
              ┌─────────────┐             ┌──────────────┐
              │    FAISS    │             │ Knowledge    │
              │ Vector DB   │             │    Graph     │
              └──────┬──────┘             └──────┬───────┘
                     │                             │
                     │ Semantic Retrieval          │
                     │                             │ Relationship Retrieval
                     └──────────────┬──────────────┘
                                    │
                           Hybrid Context
                                    │
                                    ▼
                           ┌────────────────┐
                           │   OpenAI LLM   │
                           └───────┬────────┘
                                   │
                                   ▼
                            Context-Aware
                               Answer
```

---

# 🎯 Why Hybrid RAG?

A traditional RAG system generally relies on vector similarity.

For example:

```text
User Question
     ↓
Embedding
     ↓
Vector Search
     ↓
Relevant Text Chunks
     ↓
LLM
```

This works well for finding semantically similar information.

However, many real-world enterprise questions are relationship-oriented.

For example:

```text
Which exams are related to engineering?

Which exam offers B.Tech?

Which exams are associated with medical studies?

Which exam is connected to a particular institution?
```

For these questions, understanding **relationships between entities** can improve retrieval.

Therefore, this project combines:

```text
Vector Search
     +
Knowledge Graph
     =
Hybrid RAG
```

---

# 🔗 Knowledge Graph — Core Concept

The Knowledge Graph is the key architectural component of this project.

Instead of representing the PDF only as unstructured text, relevant information is represented as:

```text
             ┌──────────────┐
             │ Entrance Exam│
             └───────┬──────┘
                     │
                  OFFERS
                     │
                     ▼
               ┌──────────┐
               │  B.Tech  │
               └──────────┘
```

Another example:

```text
Entrance Exam
      │
      ├── OFFERS ──────────────► B.Tech
      │
      ├── CATEGORY ────────────► Engineering
      │
      └── CONDUCTED_BY ───────► Institution
```

The graph provides a structured representation of domain knowledge.

---

# 🧠 Vector RAG vs Graph RAG

| Capability              | Vector RAG | Knowledge Graph |
| ----------------------- | ---------- | --------------- |
| Semantic similarity     | ✅          | ❌               |
| Text retrieval          | ✅          | Limited         |
| Entity relationships    | Limited    | ✅               |
| Multi-hop relationships | Limited    | ✅               |
| Structured knowledge    | Limited    | ✅               |
| Context retrieval       | ✅          | ✅               |
| Relationship reasoning  | Limited    | ✅               |

The project combines both approaches.

```text
                 User Query
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     FAISS Search         Graph Search
          │                     │
          │                     │
          └──────────┬──────────┘
                     │
              Context Fusion
                     │
                     ▼
                  OpenAI
                     │
                     ▼
              Final Answer
```

---

# 🏗️ Technology Stack

## Programming Language

* Python 3.10+

## GenAI / LLM

* OpenAI
* LangChain

## Vector Database

* FAISS

## Knowledge Graph

* NetworkX

## Document Processing

* PyPDF
* LangChain Document Loaders
* Recursive Character Text Splitter

## UI

* Streamlit

---

# 📁 Project Structure

```text
entrance-exam-hybrid-rag/
│
├── data/
│   └── ALL INDIA ENTRANCE EXAMS FOR HIGHER STUDIES.pdf
│
├── vectorstore/
│   └── faiss_index/
│       ├── index.faiss
│       └── index.pkl
│
├── graph/
│   └── entrance_exam_graph.json
│
├── ingest.py
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔄 End-to-End Processing Flow

## Step 1 — Document Loading

The PDF is loaded using LangChain's `PyPDFLoader`.

```python
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()
```

Each PDF page becomes a LangChain `Document`.

Conceptually:

```text
PDF
 │
 ├── Page 1
 ├── Page 2
 ├── Page 3
 ├── Page 4
 └── Page 5
```

Metadata such as page number is retained.

This is useful for displaying the source page along with the generated answer.

---

# ✂️ Step 2 — Text Splitting

Large documents should not be directly passed to the embedding model.

The document is divided into smaller chunks.

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

chunks = text_splitter.split_documents(documents)
```

### Why Chunking?

Chunking improves:

* Retrieval precision
* Embedding quality
* Context management
* LLM input efficiency

The overlap helps preserve context between adjacent chunks.

```text
Original Document

┌─────────────────────────────────────┐
│ Page content                        │
└─────────────────────────────────────┘

             ↓

Chunk 1
┌──────────────────────┐
│ Exam information ... │
└──────────────────────┘

Chunk 2
       ┌──────────────────────┐
       │ ... overlapping text │
       └──────────────────────┘
```

---

# 🧠 Step 3 — Embedding Generation

Each text chunk is converted into a vector representation.

The implementation uses:

```text
text-embedding-3-small
```

Example:

```python
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

Conceptually:

```text
"Which exams offer B.Tech?"
              │
              ▼
        Embedding Model
              │
              ▼
      [0.023, -0.17, ...]
```

The vector represents the semantic meaning of the text.

---

# 🗄️ Step 4 — FAISS Vector Database

The generated embeddings are stored in FAISS.

```python
vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)
```

The index is persisted locally:

```python
vectorstore.save_local(
    "./vectorstore/faiss_index"
)
```

This means the application does not need to recreate embeddings every time it starts.

---

# 🔗 Step 5 — Knowledge Graph Creation

The second knowledge representation is the Knowledge Graph.

NetworkX is used to create the graph.

```python
import networkx as nx

graph = nx.DiGraph()
```

The graph contains:

### Nodes

Examples:

```text
JEE Main
JEE Advanced
NEET
B.Tech
MBBS
Engineering
Medical
IIT
```

### Relationships

Examples:

```text
JEE Main → OFFERS → B.Tech

JEE Advanced → OFFERS → B.Tech

NEET → OFFERS → MBBS

Exam → CATEGORY → Engineering

Exam → CATEGORY → Medical
```

Graphically:

```text
                    ┌──────────────┐
                    │ Engineering  │
                    └──────▲───────┘
                           │
                        CATEGORY
                           │
                     ┌─────┴─────┐
                     │  JEE Main │
                     └─────┬─────┘
                           │
                         OFFERS
                           │
                           ▼
                       ┌───────┐
                       │ B.Tech│
                       └───────┘
```

---

# 🔎 Step 6 — User Query

The user enters a natural-language question through Streamlit.

Example:

```text
Which entrance exams are available for B.Tech?
```

The same question is sent to both retrieval mechanisms.

```text
                    User Query
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Vector Search          Graph Search
```

---

# 🔍 Step 7 — FAISS Retrieval

FAISS performs semantic similarity search.

```python
docs = vectorstore.similarity_search_with_score(
    query,
    k=5
)
```

The system retrieves the most relevant PDF chunks.

Example:

```text
Query:
Which exams are available for B.Tech?

FAISS Results:

1. JEE Main information
2. JEE Advanced information
3. BITSAT information
4. IIST information
5. ...
```

---

# 🔗 Step 8 — Knowledge Graph Retrieval

The graph is searched for matching entities and related nodes.

For example:

```text
Query:
Which exams offer B.Tech?
```

Graph traversal can identify:

```text
JEE Main
   │
   └── OFFERS → B.Tech

JEE Advanced
   │
   └── OFFERS → B.Tech
```

This provides relationship-aware context.

---

# 🔀 Step 9 — Hybrid Context Fusion

The results from both retrieval mechanisms are combined.

```text
FAISS Context
     +
Graph Context
     ↓
Hybrid Context
```

Example:

```text
VECTOR CONTEXT

JEE Main is an entrance examination...
JEE Advanced is associated with...


GRAPH CONTEXT

JEE Main → OFFERS → B.Tech
JEE Advanced → OFFERS → B.Tech
```

The combined context is then supplied to the LLM.

---

# 🤖 Step 10 — LLM Answer Generation

The OpenAI chat model receives:

```text
System Instructions
        +
User Question
        +
Vector Context
        +
Graph Context
```

Conceptually:

```text
                  ┌─────────────────┐
                  │   User Query    │
                  └────────┬────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
    Vector Context                     Graph Context
          │                                 │
          └────────────────┬────────────────┘
                           │
                           ▼
                    Context Fusion
                           │
                           ▼
                      OpenAI LLM
                           │
                           ▼
                    Final Response
```

The prompt instructs the model to use the supplied context and avoid unsupported information.

This helps keep the generated answer grounded in the retrieved knowledge.

---

# 🖥️ Streamlit User Interface

The application provides a web-based interface.

The UI displays:

### 🎯 AI Answer

The final response generated by the LLM.

### 📊 Retrieval Summary

Information about:

* Number of vector results
* Number of graph relationships
* Hybrid retrieval status

### 🧠 FAISS Vector Retrieval

Displays:

* Retrieved chunks
* Similarity/distance information
* Source PDF page

### 🔗 Knowledge Graph

Displays relationships such as:

```text
JEE Main
   ↓
OFFERS
   ↓
B.Tech
```

### 📄 Source Documents

The corresponding PDF page information is displayed so users can understand where the retrieved information originated.

---

# 💬 Example Questions

Try questions such as:

```text
Which entrance exams are available for B.Tech?
```

```text
Which exams are related to engineering?
```

```text
Which entrance exams are related to MBBS?
```

```text
Which exams are related to design?
```

```text
Which exam is associated with IITs?
```

```text
Which entrance exams are related to agriculture?
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>

cd entrance-exam-hybrid-rag
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

# 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
langchain
langchain-community
langchain-openai
langchain-text-splitters
faiss-cpu
pypdf
networkx
python-dotenv
streamlit
```

---

# 🔐 4. Configure OpenAI API Key

Create:

```text
.env
```

Add:

```text
OPENAI_API_KEY=your_openai_api_key
```

Do not commit the `.env` file to GitHub.

Add it to `.gitignore`:

```text
.env
venv/
__pycache__/
vectorstore/
*.pyc
```

---

# 📥 5. Prepare the PDF

Place the source document inside:

```text
data/
```

Example:

```text
data/
└── ALL INDIA ENTRANCE EXAMS FOR HIGHER STUDIES.pdf
```

---

# 🏗️ 6. Build the Knowledge Base

Run:

```bash
python ingest.py
```

The ingestion pipeline performs:

```text
PDF Loading
     ↓
Text Extraction
     ↓
Text Splitting
     ↓
Embedding Generation
     ↓
FAISS Creation
     ↓
Knowledge Graph Creation
     ↓
Local Persistence
```

The console provides detailed information about each stage.

Example:

```text
==================================================
STEP 1: LOADING PDF
==================================================

PDF loaded successfully

Pages found: 5

Page 1 loaded
Page 2 loaded
Page 3 loaded
...

==================================================
STEP 2: TEXT SPLITTING
==================================================

Total chunks created: ...

==================================================
STEP 3: CREATING EMBEDDINGS
==================================================

Embedding model: text-embedding-3-small

==================================================
STEP 4: CREATING FAISS VECTOR DATABASE
==================================================

FAISS index created successfully

==================================================
STEP 5: CREATING KNOWLEDGE GRAPH
==================================================

Nodes: ...
Edges: ...

Knowledge graph saved successfully
```

---

# ▶️ 7. Start the Application

Run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL similar to:

```text
http://localhost:8501
```

Open the URL in your browser.

---

# 🔄 Complete Runtime Flow

```text
                    USER
                     │
                     ▼
              Streamlit UI
                     │
                     ▼
                User Query
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      FAISS Search          Graph Search
          │                     │
          ▼                     ▼
    Semantic Context      Relationship Context
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
              Context Fusion
                     │
                     ▼
                OpenAI LLM
                     │
                     ▼
               Final Answer
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Source Pages        Graph Relations
```

---

# 🧩 Architecture Components

## 1. Document Layer

Responsible for:

* PDF loading
* Page extraction
* Metadata preservation

Technology:

```text
PyPDFLoader
```

---

## 2. Chunking Layer

Responsible for:

* Splitting large documents
* Maintaining contextual overlap

Technology:

```text
RecursiveCharacterTextSplitter
```

---

## 3. Embedding Layer

Responsible for:

* Converting text into vector representations

Technology:

```text
OpenAI Embeddings
```

---

## 4. Vector Retrieval Layer

Responsible for:

* Semantic similarity search
* Retrieving relevant document chunks

Technology:

```text
FAISS
```

---

## 5. Knowledge Graph Layer

Responsible for:

* Entity representation
* Relationship representation
* Graph traversal

Technology:

```text
NetworkX
```

---

## 6. Hybrid Retrieval Layer

Responsible for combining:

```text
Vector Context
+
Graph Context
```

This is the main intelligence layer connecting the two retrieval approaches.

---

## 7. Generation Layer

Responsible for:

* Context processing
* Answer generation
* Grounded responses

Technology:

```text
OpenAI LLM
```

---

## 8. Presentation Layer

Responsible for:

* User interaction
* Search
* Retrieval visualization
* Source display
* Graph relationship display

Technology:

```text
Streamlit
```

---

# 📐 Architectural Advantages

### 1. Semantic Understanding

FAISS allows the system to retrieve content based on semantic similarity rather than exact keyword matching.

### 2. Relationship Awareness

The Knowledge Graph explicitly represents relationships between entities.

### 3. Context Enrichment

Graph information can enrich the text retrieved from the vector database.

### 4. Source Traceability

PDF page metadata can be retained and displayed with retrieved information.

### 5. Local Vector Storage

FAISS can be persisted locally without requiring a managed vector database.

### 6. Extensible Architecture

The architecture can later be extended with:

* Neo4j
* GraphRAG
* Reranking
* Multi-hop retrieval
* Hybrid scoring
* Automated entity extraction
* Agentic RAG

---

# 🔮 Future Enhancements

The current implementation provides the foundation for a more advanced enterprise RAG architecture.

## 1. Automated Knowledge Graph Extraction

Instead of manually defining graph relationships, use an LLM or NLP pipeline to automatically extract:

```text
Entities
+
Relationships
+
Properties
```

from the document.

---

## 2. Neo4j Integration

NetworkX is useful for a lightweight local implementation.

For production-scale graph workloads, the architecture can evolve to:

```text
                 ┌───────────────┐
                 │     FAISS     │
                 │ Vector Search │
                 └───────┬───────┘
                         │
                         │
                 ┌───────▼───────┐
                 │     Neo4j     │
                 │ Knowledge     │
                 │    Graph      │
                 └───────┬───────┘
                         │
                         ▼
                  Hybrid Retrieval
```

---

## 3. Reranking

Retrieved vector and graph results can be reranked before sending them to the LLM.

```text
FAISS Results
      +
Graph Results
      ↓
   Reranker
      ↓
Top-K Context
      ↓
     LLM
```

---

## 4. Multi-Hop Graph Retrieval

Future versions can support questions requiring multiple relationships.

Example:

```text
Exam
 ↓
Institution
 ↓
Course
 ↓
Category
```

This enables more sophisticated graph-based reasoning.

---

## 5. Interactive Graph Visualization

The UI can be extended with an interactive graph where users can explore:

```text
Exam → Course → Category → Institution
```

---

# 🔐 Security Considerations

Never commit:

```text
.env
```

or API keys to GitHub.

Use:

```text
.env
```

for local development and environment variables/secrets management for deployment.

---

# 🧪 Learning Objectives

This project demonstrates practical implementation of:

* Document-based RAG
* LangChain pipelines
* PDF ingestion
* Text chunking
* Embeddings
* Vector databases
* FAISS retrieval
* Knowledge Graphs
* Graph traversal
* Hybrid retrieval
* Context fusion
* LLM-based generation
* Source-aware responses
* Streamlit application development

---

# ⭐ Key Takeaway

The main architectural idea behind this project is:

```text
              Traditional RAG
                    │
             Semantic Search
                    │
                    ▼
                 FAISS
```

versus:

```text
              Hybrid RAG
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
      Vector RAG          Graph RAG
          │                   │
       Semantic          Relationships
       Similarity           & Entities
          │                   │
          └─────────┬─────────┘
                    ▼
              Hybrid Context
                    │
                    ▼
                   LLM
```

**Vector RAG helps find relevant information.**

**Knowledge Graph helps understand how information is connected.**

**Hybrid RAG brings both together.**

---

# 👨‍💻 Project Purpose

This project was built as a practical exploration of **GenAI Architecture, Hybrid RAG, GraphRAG, Knowledge Graphs, and enterprise-oriented information retrieval**.

It demonstrates how unstructured documents can be transformed into both:

```text
Unstructured Knowledge
        +
Structured Relationships
        ↓
Hybrid AI Retrieval
        ↓
Context-Aware Generation
```

---

# 📌 Author

**Dinesh Kumar**

AI & Java Full Stack Developer | GenAI Architect

Interested in:

* Generative AI
* RAG
* GraphRAG
* Knowledge Graphs
* LangChain
* LLM Applications
* AI Architecture
* Java
* Python
* Enterprise AI

---

# ⭐ If You Find This Useful

If this project helps you understand **Hybrid RAG + Knowledge Graph architecture**, consider giving the repository a ⭐.

Feel free to explore, experiment, and extend the architecture.
