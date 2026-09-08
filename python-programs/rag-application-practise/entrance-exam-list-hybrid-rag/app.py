import os
import json
import networkx as nx

import streamlit as st

from dotenv import load_dotenv

from langchain_openai import (
    OpenAIEmbeddings,
    ChatOpenAI
)

from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

FAISS_PATH = "vectorstore/faiss_index"

GRAPH_PATH = "graph/entrance_exam_graph.json"


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=" ENTRANCE EXAM EXPLORER - DEVELOPED IN HYBRID RAG",
    page_icon="🎓",
    layout="wide"
)


st.title("🎓 ENTRANCE EXAM EXPLORER - DEVELOPED IN HYBRID RAG")

st.write(
    "Hybrid RAG using LangChain + FAISS + Knowledge Graph"
)


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

@st.cache_resource
def load_embeddings():

    print("\n" + "=" * 80)
    print("LOADING EMBEDDING MODEL")
    print("=" * 80)

    print(
        "[INFO] Loading OpenAI "
        "text-embedding-3-small..."
    )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    print(
        "[SUCCESS] Embedding model loaded"
    )

    return embeddings


# ============================================================
# LOAD FAISS
# ============================================================

@st.cache_resource
def load_vectorstore():

    print("\n" + "=" * 80)
    print("LOADING FAISS VECTOR DATABASE")
    print("=" * 80)

    embeddings = load_embeddings()

    print(
        f"[INFO] Loading FAISS from: "
        f"{FAISS_PATH}"
    )

    vectorstore = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print(
        "[SUCCESS] FAISS vector database loaded"
    )

    return vectorstore


# ============================================================
# LOAD KNOWLEDGE GRAPH
# ============================================================

@st.cache_resource
def load_graph():

    print("\n" + "=" * 80)
    print("LOADING KNOWLEDGE GRAPH")
    print("=" * 80)

    print(
        f"[INFO] Loading graph from: "
        f"{GRAPH_PATH}"
    )

    with open(
        GRAPH_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        graph_data = json.load(file)

    graph = nx.node_link_graph(
        graph_data
    )

    print(
        "[SUCCESS] Knowledge Graph loaded"
    )

    print(
        f"[INFO] Nodes : "
        f"{graph.number_of_nodes()}"
    )

    print(
        f"[INFO] Edges : "
        f"{graph.number_of_edges()}"
    )

    return graph


# ============================================================
# LOAD LLM
# ============================================================

@st.cache_resource
def load_llm():

    print("\n" + "=" * 80)
    print("LOADING CHAT MODEL")
    print("=" * 80)

    print(
        "[INFO] Initializing OpenAI Chat Model..."
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    print(
        "[SUCCESS] Chat model initialized"
    )

    return llm


# ============================================================
# GRAPH RETRIEVAL
# ============================================================

def graph_search(
    graph,
    query
):

    print("\n" + "=" * 80)
    print("GRAPH RETRIEVAL")
    print("=" * 80)

    print(
        f"[QUERY] {query}"
    )

    query_lower = query.lower()

    matched_nodes = []

    # --------------------------------------------------------
    # Find nodes matching query
    # --------------------------------------------------------

    for node, attributes in graph.nodes(
        data=True
    ):

        node_text = str(node).lower()

        full_name = str(
            attributes.get(
                "full_name",
                ""
            )
        ).lower()

        if (
            node_text in query_lower
            or query_lower in node_text
            or node_text in query_lower
            or full_name in query_lower
        ):

            matched_nodes.append(node)

    print(
        f"[INFO] Matched graph nodes : "
        f"{matched_nodes}"
    )

    # --------------------------------------------------------
    # If no exact match, search keywords
    # --------------------------------------------------------

    if not matched_nodes:

        keywords = [
            "engineering",
            "medical",
            "law",
            "design",
            "agriculture",
            "architecture",
            "science",
            "fashion",
            "management",
            "mbbs",
            "btech",
            "b.e",
            "b.arch"
        ]

        for node, attributes in graph.nodes(
            data=True
        ):

            node_text = (
                str(node) + " "
                + str(
                    attributes.get(
                        "full_name",
                        ""
                    )
                )
            ).lower()

            for keyword in keywords:

                if keyword in query_lower:

                    if keyword in node_text:

                        matched_nodes.append(
                            node
                        )

                        break

    # Remove duplicates
    matched_nodes = list(
        dict.fromkeys(
            matched_nodes
        )
    )

    # --------------------------------------------------------
    # Traverse relationships
    # --------------------------------------------------------

    graph_context = []

    for node in matched_nodes:

        print(
            f"\n[GRAPH NODE] {node}"
        )

        attributes = graph.nodes[node]

        print(
            f"[ATTRIBUTES] {attributes}"
        )

        graph_context.append(
            f"Node: {node}\n"
            f"Attributes: {attributes}"
        )

        # Outgoing relationships

        for target in graph.successors(
            node
        ):

            relationship = graph[
                node
            ][target].get(
                "relationship"
            )

            print(
                f"[RELATIONSHIP] "
                f"{node} "
                f"--{relationship}--> "
                f"{target}"
            )

            graph_context.append(
                f"{node} "
                f"--{relationship}--> "
                f"{target}"
            )

    print(
        f"\n[INFO] Graph context records : "
        f"{len(graph_context)}"
    )

    return "\n".join(
        graph_context
    )


# ============================================================
# VECTOR RETRIEVAL
# ============================================================

def vector_search(
    vectorstore,
    query,
    k=5
):

    print("\n" + "=" * 80)
    print("VECTOR RETRIEVAL - FAISS")
    print("=" * 80)

    print(
        f"[QUERY] {query}"
    )

    print(
        f"[INFO] Retrieving top {k} documents..."
    )

    documents = vectorstore.similarity_search(
        query,
        k=k
    )

    print(
        f"[SUCCESS] Retrieved "
        f"{len(documents)} documents"
    )

    vector_context = []

    for i, document in enumerate(
        documents
    ):

        print("\n" + "-" * 70)

        print(
            f"[VECTOR RESULT {i + 1}]"
        )

        print(
            f"Page : "
            f"{document.metadata.get('page')}"
        )

        print(
            "Content:"
        )

        print(
            document.page_content
        )

        vector_context.append(
            document.page_content
        )

    return "\n\n".join(
        vector_context
    )


# ============================================================
# HYBRID RETRIEVAL
# ============================================================

def hybrid_retrieval(
    query
):

    print("\n")
    print("#" * 80)
    print("HYBRID RETRIEVAL STARTED")
    print("#" * 80)

    vectorstore = load_vectorstore()

    graph = load_graph()

    # --------------------------------------------------------
    # Vector search
    # --------------------------------------------------------

    vector_context = vector_search(
        vectorstore,
        query,
        k=5
    )

    # --------------------------------------------------------
    # Graph search
    # --------------------------------------------------------

    graph_context = graph_search(
        graph,
        query
    )

    # --------------------------------------------------------
    # Context fusion
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("CONTEXT FUSION")
    print("=" * 80)

    print(
        "[INFO] Combining vector context "
        "and graph context..."
    )

    combined_context = f"""
================ VECTOR CONTEXT ================

{vector_context}


================ GRAPH CONTEXT =================

{graph_context}
"""

    print(
        "[SUCCESS] Hybrid context created"
    )

    return combined_context


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    query,
    context
):

    print("\n" + "=" * 80)
    print("LLM ANSWER GENERATION")
    print("=" * 80)

    print(
        "[INFO] Sending hybrid context "
        "to OpenAI..."
    )

    llm = load_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an entrance examination
information assistant.

Answer the user's question using
ONLY the supplied context.

The context contains two sources:

1. Vector Context
2. Knowledge Graph Context

Use both sources when appropriate.

Do not invent examination,
course, institute or eligibility
information.

If the information is not available
in the supplied context, clearly say:

"The information is not available
in the provided document."

Provide a concise and structured answer.

When useful, present the result
as a table.
"""
            ),
            (
                "human",
                """
USER QUESTION:

{question}


RETRIEVED CONTEXT:

{context}
"""
            )
        ]
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "question": query,
            "context": context
        }
    )

    print(
        "\n[SUCCESS] LLM response generated"
    )

    print(
        "\nANSWER:"
    )

    print(
        response.content
    )

    return response.content


# ============================================================
# STREAMLIT UI
# ============================================================

query = st.text_input(
    "Ask a question about entrance exams"
)


if st.button("🔍 Search"):

    if not query.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching FAISS + Knowledge Graph..."
        ):

            try:

                # ------------------------------------------------
                # Hybrid Retrieval
                # ------------------------------------------------

                context = hybrid_retrieval(
                    query
                )

                # ------------------------------------------------
                # Generate Answer
                # ------------------------------------------------

                answer = generate_answer(
                    query,
                    context
                )

                # ------------------------------------------------
                # Display Answer
                # ------------------------------------------------

                st.subheader(
                    "🤖 Answer"
                )

                st.write(
                    answer
                )

                # ------------------------------------------------
                # Show Debug Context
                # ------------------------------------------------

                with st.expander(
                    "🔎 View Retrieved Context"
                ):

                    st.text(
                        context
                    )

            except Exception as e:

                print("\n" + "!" * 80)

                print(
                    "[ERROR] Application failed"
                )

                print(
                    str(e)
                )

                print("!" * 80)

                st.error(
                    f"Error: {str(e)}"
                )