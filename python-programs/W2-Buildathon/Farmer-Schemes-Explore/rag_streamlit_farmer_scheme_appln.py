import os
import pandas as pd
import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TN Agri Schemes Chat Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURATION CONSTANTS ---
EXCEL_FILE_PATH = "TN_Agri_GoScheme.xlsx"
FAISS_INDEX_DIR = "./faiss_db_for_farmer_schemes"

# --- HELPER FUNCTIONS & VECTOR STORE ---
@st.cache_data
def load_excel_data(file_path: str):
    """Loads and caches raw Excel data."""
    if not os.path.exists(file_path):
        return None
    return pd.read_excel(file_path, sheet_name="GoScheme Data")

@st.cache_resource
def get_faiss_vectorstore(excel_path: str, index_dir: str):
    """Initializes embeddings and loads or builds the FAISS vector store."""
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    if os.path.exists(index_dir) and os.path.exists(os.path.join(index_dir, "index.faiss")):
        vectorstore = FAISS.load_local(
            folder_path=index_dir,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        df = load_excel_data(excel_path)
        if df is None:
            return None

        documents = []
        for idx, row in df.iterrows():
            s_no = str(row.get('S.No', idx + 1)).strip()
            dept = str(row.get('Department', 'N/A')).strip()
            scheme_name = str(row.get('Scheme', 'N/A')).strip()
            desc = str(row.get('Scheme Description', 'N/A')).strip()
            eligibility = str(row.get('Eligibility Criteria', 'N/A')).strip()
            documents_req = str(row.get("Document's Required", 'N/A')).strip()
            go_guidelines = str(row.get('GO & Guidelines', 'N/A')).strip()

            content = f"""
            Scheme Name: {scheme_name}
            Department: {dept}
            Scheme Description: {desc}
            Eligibility Criteria: {eligibility}
            Required Documents: {documents_req}
            GO Guidelines Status: {go_guidelines}
            """

            metadata = {
                "s_no": s_no,
                "department": dept,
                "scheme_name": scheme_name,
                "go_guidelines": go_guidelines,
                "description": desc,
                "eligibility": eligibility,
                "documents": documents_req
            }
            documents.append(Document(page_content=content.strip(), metadata=metadata))

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(index_dir)

    return vectorstore

# --- APP HEADER & SIDEBAR ---
st.title("🌾 Tamil Nadu Agri Schemes AI Assistant")
st.caption("Ask questions about government schemes via Chat API powered by FAISS Vector Store")

df_data = load_excel_data(EXCEL_FILE_PATH)

if df_data is None:
    st.error(f"❌ Could not find Excel file: `{EXCEL_FILE_PATH}`. Please ensure your Excel file exists.")
    st.stop()

with st.spinner("Initializing Vector Store..."):
    vectorstore = get_faiss_vectorstore(EXCEL_FILE_PATH, FAISS_INDEX_DIR)

st.sidebar.header("⚙️ Chat Settings")
departments = ["All Departments"] + list(df_data["Department"].dropna().unique())
selected_dept = st.sidebar.selectbox("Filter by Department:", departments)
top_k = st.sidebar.slider("Top Matches to Retrieve (k):", min_value=1, max_value=10, value=3)

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("Total Schemes Indexed", len(df_data))

# --- TABS LAYOUT ---
tab_chat, tab_table = st.tabs(["💬 Chat API Interface", "📊 Excel Dataset"])

# --- TAB 1: CHAT INTERFACE ---
with tab_chat:
    # Initialize Session State for Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your Tamil Nadu Agriculture Schemes assistant. Ask me anything about subsidies, eligibility criteria, or required documents."}
        ]

    # Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "results" in message:
                for idx, (doc, score) in enumerate(message["results"], 1):
                    meta = doc.metadata
                    with st.expander(f"📌 **Match #{idx}: {meta.get('scheme_name')}** ({meta.get('department')})"):
                        st.markdown(f"**S.No:** {meta.get('s_no')} | **FAISS Score:** `{score:.4f}`")
                        st.markdown("**Description:** " + meta.get("description", "N/A"))
                        st.markdown("**Eligibility:** " + meta.get("eligibility", "N/A"))
                        st.markdown("**Documents:** " + meta.get("documents", "N/A"))

    # Chat API Input Box
    if user_input := st.chat_input("Ask a question (e.g., What documents are required for drip irrigation?)"):
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process Query with FAISS
        with st.chat_message("assistant"):
            with st.spinner("Searching scheme vector database..."):
                raw_results = vectorstore.similarity_search_with_score(user_input, k=top_k * 2)

            # Apply Department Filter
            filtered_results = []
            for doc, score in raw_results:
                if selected_dept == "All Departments" or doc.metadata.get("department") == selected_dept:
                    filtered_results.append((doc, score))
                if len(filtered_results) >= top_k:
                    break

            if not filtered_results:
                reply_text = "I couldn't find any relevant schemes matching your query and department filter."
                st.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            else:
                reply_text = f"Here are the top **{len(filtered_results)} matching schemes** retrieved from the portal:"
                st.markdown(reply_text)

                for idx, (doc, score) in enumerate(filtered_results, 1):
                    meta = doc.metadata
                    with st.expander(f"📌 **Match #{idx}: {meta.get('scheme_name')}** ({meta.get('department')})", expanded=(idx == 1)):
                        st.markdown(f"**S.No:** {meta.get('s_no')} | **FAISS Score:** `{score:.4f}`")
                        st.markdown("**Description:** " + meta.get("description", "N/A"))
                        st.markdown("**Eligibility:** " + meta.get("eligibility", "N/A"))
                        st.markdown("**Documents:** " + meta.get("documents", "N/A"))

                # Save Assistant Message with Results to Session State
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply_text,
                    "results": filtered_results
                })

# --- TAB 2: EXCEL DATASET VIEW ---
with tab_table:
    st.subheader("Raw Exported Dataset")
    st.dataframe(df_data, use_container_width=True, hide_index=True)
    with open(EXCEL_FILE_PATH, "rb") as file:
        st.download_button(
            label="📥 Download Excel File (.xlsx)",
            data=file,
            file_name="TN_Agri_GoScheme.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )