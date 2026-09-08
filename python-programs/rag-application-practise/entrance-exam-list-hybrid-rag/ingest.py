import os
import re
import json
import networkx as nx

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

PDF_PATH = "data/ALL INDIA ENTRANCE EXAMS FOR HIGHER STUDIES.pdf"

FAISS_PATH = "vectorstore/faiss_index"

GRAPH_PATH = "graph/entrance_exam_graph.json"


# ============================================================
# STEP 1 - LOAD PDF
# ============================================================

def load_pdf():

    print("\n" + "=" * 80)
    print("STEP 1 : DOCUMENT LOADING")
    print("=" * 80)

    print(f"[INFO] PDF file      : {PDF_PATH}")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(
            f"PDF not found: {PDF_PATH}"
        )

    print("[INFO] Starting PDF loading...")

    loader = PyPDFLoader(PDF_PATH)

    documents = loader.load()

    print(f"[SUCCESS] PDF loaded successfully")
    print(f"[INFO] Number of pages loaded : {len(documents)}")

    for i, doc in enumerate(documents):

        print("\n" + "-" * 70)

        print(f"[PAGE {i + 1}]")

        print(f"Metadata : {doc.metadata}")

        preview = doc.page_content[:500]

        print("Content Preview:")
        print(preview)

    return documents


# ============================================================
# STEP 2 - TEXT SPLITTING
# ============================================================

def split_documents(documents):

    print("\n" + "=" * 80)
    print("STEP 2 : TEXT SPLITTING")
    print("=" * 80)

    print("[INFO] Creating RecursiveCharacterTextSplitter...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    print("[INFO] Chunk size     : 800")
    print("[INFO] Chunk overlap  : 150")

    chunks = text_splitter.split_documents(documents)

    print(f"\n[SUCCESS] Text splitting completed")
    print(f"[INFO] Number of chunks created : {len(chunks)}")

    for i, chunk in enumerate(chunks[:10]):

        print("\n" + "-" * 70)

        print(f"[CHUNK {i + 1}]")

        print(f"Source page : {chunk.metadata.get('page')}")

        print("Content:")
        print(chunk.page_content[:500])

    return chunks


# ============================================================
# STEP 3 - CREATE EMBEDDINGS
# ============================================================

def create_embeddings():

    print("\n" + "=" * 80)
    print("STEP 3 : EMBEDDING MODEL")
    print("=" * 80)

    print("[INFO] Initializing OpenAI Embeddings...")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    print("[SUCCESS] Embedding model initialized")

    print("[INFO] Embedding model : text-embedding-3-small")

    return embeddings


# ============================================================
# STEP 4 - CREATE FAISS VECTOR DATABASE
# ============================================================

def create_faiss(chunks, embeddings):

    print("\n" + "=" * 80)
    print("STEP 4 : FAISS VECTOR DATABASE")
    print("=" * 80)

    print("[INFO] Creating FAISS vector database...")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    print("[SUCCESS] FAISS vector database created")

    print(f"[INFO] Saving FAISS index to : {FAISS_PATH}")

    os.makedirs(
        os.path.dirname(FAISS_PATH),
        exist_ok=True
    )

    vectorstore.save_local(
        FAISS_PATH
    )

    print("[SUCCESS] FAISS index saved successfully")

    return vectorstore


# ============================================================
# STEP 5 - BUILD KNOWLEDGE GRAPH
# ============================================================

def create_knowledge_graph(documents):

    print("\n" + "=" * 80)
    print("STEP 5 : KNOWLEDGE GRAPH CREATION")
    print("=" * 80)

    print("[INFO] Creating NetworkX knowledge graph...")

    graph = nx.DiGraph()

    # --------------------------------------------------------
    # Helper function
    # --------------------------------------------------------

    def add_exam(
        exam,
        full_name="",
        exam_type="",
        courses=None,
        institutes=None,
        location="",
        website=""
    ):

        courses = courses or []
        institutes = institutes or []

        print("\n[GRAPH] Adding Exam Node")
        print(f"        Exam       : {exam}")
        print(f"        Full Name  : {full_name}")
        print(f"        Exam Type  : {exam_type}")

        graph.add_node(
            exam,
            type="EXAM",
            full_name=full_name,
            exam_type=exam_type,
            location=location,
            website=website
        )

        # ----------------------------------------------------
        # Course relationships
        # ----------------------------------------------------

        for course in courses:

            print(
                f"        Relationship: {exam} "
                f"--OFFERS--> {course}"
            )

            graph.add_node(
                course,
                type="COURSE"
            )

            graph.add_edge(
                exam,
                course,
                relationship="OFFERS"
            )

        # ----------------------------------------------------
        # Institute relationships
        # ----------------------------------------------------

        for institute in institutes:

            print(
                f"        Relationship: {exam} "
                f"--FOR_INSTITUTE--> {institute}"
            )

            graph.add_node(
                institute,
                type="INSTITUTE"
            )

            graph.add_edge(
                exam,
                institute,
                relationship="FOR_INSTITUTE"
            )

    # ========================================================
    # ENTRANCE EXAMS FROM PDF
    # ========================================================

    add_exam(
        exam="JEE Main",
        full_name="Joint Entrance Examination Main",
        exam_type="Written Exam",
        courses=[
            "B.E",
            "B.Tech",
            "B.Arch"
        ],
        institutes=[
            "NITs",
            "IIITs"
        ],
        website="http://jeemain.nic.in"
    )

    add_exam(
        exam="JEE Advanced",
        full_name="Indian Institute of Technology Joint Entrance Exam",
        exam_type="Written Exam",
        courses=[
            "B.E",
            "B.Tech"
        ],
        institutes=[
            "IITs"
        ],
        website="www.advance.nic.in"
    )

    add_exam(
        exam="NEET",
        full_name="National Eligibility Entrance Test",
        exam_type="Written Exam",
        courses=[
            "MBBS",
            "BDS"
        ],
        institutes=[
            "Medical Colleges in India"
        ],
        website="www.aipmt.nic.in"
    )

    add_exam(
        exam="AFMC",
        full_name="Armed Forces Medical College Entrance Exam",
        exam_type="Written Exam",
        courses=[
            "MBBS"
        ],
        institutes=[
            "Armed Forces Medical College"
        ],
        website="www.afmc.nic.in"
    )

    add_exam(
        exam="NID NEED",
        full_name="National Entrance Exam for Design",
        exam_type="Written Exam",
        courses=[
            "Design"
        ],
        institutes=[
            "National Institute of Design",
            "Other Design Institutes"
        ],
        website="www.nid.edu"
    )

    add_exam(
        exam="CLAT",
        full_name="Common Law Admission Test",
        exam_type="Written Exam",
        courses=[
            "Law"
        ],
        institutes=[
            "National Law Universities"
        ],
        website="www.clat.ac.in"
    )

    add_exam(
        exam="BITSAT",
        full_name="Birla Institute of Technology and Science Admission Test",
        exam_type="Online Exam",
        courses=[
            "B.E"
        ],
        institutes=[
            "BITS Pilani",
            "BITS Hyderabad",
            "BITS Goa"
        ],
        website="www.bits-pilani.ac.in"
    )

    add_exam(
        exam="NCHMCT",
        full_name="National Council for Hotel Management Catering Technology Joint Entrance Exam",
        exam_type="Written Exam",
        courses=[
            "B.Sc Hospitality",
            "Hotel Administration"
        ],
        institutes=[
            "Hotel Management Institutes"
        ],
        website="www.nchm.nic.in"
    )

    add_exam(
        exam="NDA and NA",
        full_name="National Defense Academy and Naval Academy",
        exam_type="Written Exam",
        courses=[
            "Army",
            "Navy",
            "Air Force"
        ],
        institutes=[
            "National Defense Academy",
            "Naval Academy"
        ],
        website="www.nda.nic.in"
    )

    add_exam(
        exam="IIST",
        full_name="Indian Institute of Space Technology",
        exam_type="Written Exam",
        courses=[
            "B.Tech Avionics",
            "Aerospace Engineering",
            "Physical Science"
        ],
        institutes=[
            "Indian Institute of Space Technology"
        ],
        location="Thiruvananthapuram",
        website="www.iist.ac.in"
    )

    add_exam(
        exam="JNU",
        full_name="Jawaharlal Nehru University",
        exam_type="Written Exam",
        courses=[
            "B.A Foreign Language"
        ],
        institutes=[
            "Jawaharlal Nehru University"
        ],
        location="New Delhi",
        website="www.jnu.ac.in"
    )

    add_exam(
        exam="ISI",
        full_name="Indian Statistical Institute",
        exam_type="Written Exam",
        courses=[
            "B.Sc Statistics",
            "B.Sc Mathematics"
        ],
        institutes=[
            "ISI Kolkata",
            "ISI Bengaluru"
        ],
        location="Kolkata / Bengaluru",
        website="www.isical.ac.in"
    )

    add_exam(
        exam="IISER",
        full_name="Indian Institutes of Science Education and Research",
        exam_type="Written Exam",
        courses=[
            "BS-MS Biology",
            "BS-MS Chemistry",
            "BS-MS Mathematics",
            "BS-MS Physics",
            "Earth Sciences"
        ],
        institutes=[
            "IISER Pune",
            "IISER Bhopal",
            "IISER Kolkata",
            "IISER Mohali",
            "IISER Thiruvananthapuram"
        ],
        website="www.iiserpune.ac.in"
    )

    add_exam(
        exam="NATA",
        full_name="National Aptitude Test in Architecture",
        exam_type="Computer Based Test",
        courses=[
            "B.Arch"
        ],
        institutes=[
            "Architecture Institutes"
        ],
        website="www.nata.in"
    )

    add_exam(
        exam="AIPVT",
        full_name="All India Pre-Veterinary Test",
        exam_type="Written Exam",
        courses=[
            "B.V.Sc",
            "Animal Husbandry"
        ],
        institutes=[
            "Veterinary Colleges"
        ],
        website="www.vci.nic.in"
    )

    add_exam(
        exam="AIEEA",
        full_name="All India Entrance Examination for Agriculture and Allied Sciences",
        exam_type="Written Exam",
        courses=[
            "Agriculture",
            "Horticulture",
            "Fisheries",
            "Forestry",
            "Home Science",
            "Sericulture",
            "Biotechnology",
            "Agricultural Engineering",
            "Dairy Technology",
            "Food Science"
        ],
        institutes=[
            "Agriculture Universities"
        ],
        website="www.icar.org.in"
    )

    add_exam(
        exam="UCEED",
        full_name="Undergraduate Common Entrance Examination for Design",
        exam_type="Written Exam",
        courses=[
            "B.Des",
            "Product Design",
            "Communication Design",
            "Interaction Design",
            "Mobility Design",
            "Animation Design"
        ],
        institutes=[
            "IIT Bombay"
        ],
        website="www.uceed.in"
    )

    add_exam(
        exam="FDDI AIST",
        full_name="Footwear Design and Development Institute All India Selection Test",
        exam_type="Computer Based Entrance Test",
        courses=[
            "Footwear Design"
        ],
        institutes=[
            "Footwear Design and Development Institute"
        ],
        website="www.fddiindia.com"
    )

    add_exam(
        exam="NEST",
        full_name="National Entrance Screening Test",
        exam_type="Written Exam",
        courses=[
            "Integrated M.Sc Biology",
            "Integrated M.Sc Chemistry",
            "Integrated M.Sc Mathematics",
            "Integrated M.Sc Physics"
        ],
        institutes=[
            "NISER"
        ],
        website="www.niser.ac.in"
    )

    add_exam(
        exam="RIE CEE",
        full_name="Regional Institute of Education Common Entrance Exam",
        exam_type="Written Exam",
        courses=[
            "B.Sc B.Ed",
            "B.A B.Ed",
            "M.Sc B.Ed"
        ],
        institutes=[
            "Regional Institute of Education"
        ],
        website="www.rieajmer.raj.nic.in"
    )

    add_exam(
        exam="CUCET",
        full_name="Central Universities Common Entrance Test",
        exam_type="Written Exam",
        courses=[
            "Integrated UG",
            "PG",
            "Research Programs",
            "BA B.Ed",
            "BSc B.Ed",
            "BA LLB",
            "MA",
            "MSc"
        ],
        institutes=[
            "Central Universities"
        ],
        website="www.cucet2015.co.in"
    )

    add_exam(
        exam="HSEE",
        full_name="Humanities and Social Sciences Entrance Examination",
        exam_type="Written Exam",
        courses=[
            "Integrated MA Developmental Studies",
            "MA English Studies"
        ],
        institutes=[
            "IIT Madras"
        ],
        website="www.hsee.iitm.ac.in"
    )

    add_exam(
        exam="TISS",
        full_name="Tata Institute of Social Sciences",
        exam_type="Written Exam",
        courses=[
            "BA Social Work",
            "Integrated BA MA"
        ],
        institutes=[
            "Tata Institute of Social Sciences"
        ],
        website="www.tiss.edu.in"
    )

    add_exam(
        exam="NIFT",
        full_name="National Institute of Fashion Technology",
        exam_type="Written Exam",
        courses=[
            "Fashion Technology",
            "Design Management"
        ],
        institutes=[
            "National Institute of Fashion Technology"
        ],
        website="www.nift.ac.in"
    )

    add_exam(
        exam="CPT",
        full_name="Common Proficiency Test",
        exam_type="Written Exam",
        courses=[
            "CA"
        ],
        institutes=[
            "ICAI"
        ],
        website="www.icai.org"
    )

    add_exam(
        exam="CS Programme",
        full_name="Institute of Company Secretaries of India",
        exam_type="Written Exam",
        courses=[
            "Company Secretary"
        ],
        institutes=[
            "ICSI"
        ],
        website="www.icsi.edu"
    )

    add_exam(
        exam="JIPMER",
        full_name="Jawaharlal Institute of Postgraduate Medical Education and Research",
        exam_type="Entrance Exam",
        courses=[
            "MBBS"
        ],
        institutes=[
            "JIPMER Pondicherry"
        ]
    )

    # ========================================================
    # SAVE GRAPH
    # ========================================================

    print("\n" + "-" * 80)

    print("[INFO] Knowledge Graph Statistics")

    print(f"[INFO] Number of nodes : {graph.number_of_nodes()}")

    print(f"[INFO] Number of edges : {graph.number_of_edges()}")

    print("\n[INFO] Graph Relationships:")

    for source, target, data in graph.edges(data=True):

        print(
            f"  {source} "
            f"--{data['relationship']}--> "
            f"{target}"
        )

    os.makedirs(
        os.path.dirname(GRAPH_PATH),
        exist_ok=True
    )

    graph_data = nx.node_link_data(graph)

    with open(
        GRAPH_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            graph_data,
            file,
            indent=2
        )

    print(f"\n[SUCCESS] Knowledge Graph saved to:")
    print(f"         {GRAPH_PATH}")

    return graph


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 80)
    print("  STUDENT ENTRANCE EXAM EXPLORER - DEVELOPED IN HYBRID RAG - INGESTION PIPELINE")
    print("=" * 80)

    print("\nArchitecture:")
    print("PDF")
    print("  -> Document Loading")
    print("  -> Text Splitting")
    print("  -> Embeddings")
    print("  -> FAISS")
    print()
    print("PDF")
    print("  -> Entity / Relationship Extraction")
    print("  -> Knowledge Graph")

    # Step 1
    documents = load_pdf()

    # Step 2
    chunks = split_documents(documents)

    # Step 3
    embeddings = create_embeddings()

    # Step 4
    vectorstore = create_faiss(
        chunks,
        embeddings
    )

    # Step 5
    graph = create_knowledge_graph(
        documents
    )

    print("\n" + "=" * 80)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 80)

    print(f"[INFO] FAISS index : {FAISS_PATH}")
    print(f"[INFO] Graph       : {GRAPH_PATH}")

    print("\nYou can now run:")
    print("    streamlit run app.py")


if __name__ == "__main__":
    main()