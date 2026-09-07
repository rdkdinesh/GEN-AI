import os
import json
import asyncio
from dotenv import load_dotenv
from neo4j import GraphDatabase, AsyncGraphDatabase
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, LLMGraphTransformer

# Load environment variables (.env file)
load_dotenv()

# Environment Credentials
NEO4J_URI = os.getenv("NEO4J_URI", "bolt+ssc://your-instance.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

NODE_LABELS = ["Department", "Scheme", "Benefit", "TargetAudience"]


def setup_database_schema(uri, auth):
    """
    Uses the native Neo4j Driver to apply database schema rules,
    creating uniqueness constraints on node IDs before inserting data.
    """
    print("\n[Native Driver] Establishing connection to setup constraints...")
    with GraphDatabase.driver(uri, auth=auth) as driver:
        # Verify connection connectivity
        driver.verify_connectivity()
        print("[Native Driver] Successfully connected to Neo4j instance.")

        with driver.session() as session:
            for label in NODE_LABELS:
                constraint_query = (
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) "
                    f"REQUIRE n.id IS UNIQUE;"
                )
                session.run(constraint_query)
                print(f"[Schema Setup] Applied uniqueness constraint for label: :{label}")


def load_and_clean_documents(json_path: str) -> list[Document]:
    """
    Loads raw JSON data and sanitizes text strings to remove excess whitespace
    and formatting issues before creating LangChain Document objects.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find JSON file at path: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        schemes_data = json.load(f)

    documents = []
    for item in schemes_data:
        raw_details = item.get("details", "")
        # Sanitize whitespace and newline characters
        clean_details = " ".join(raw_details.split())
        
        link = item.get("link", "N/A")
        content = (
            f"Department: Agriculture - Farmers Welfare Department. "
            f"Scheme details: {clean_details}. Official Link: {link}"
        )
        
        documents.append(
            Document(page_content=content, metadata={"link": link})
        )

    print(f"\nStep 1 [Document Loader]: Loaded and sanitized {len(documents)} documents.")
    return documents


async def run_knowledge_graph_pipeline():
    # --- STEP 0: DATABASE SCHEMA SETUP WITH NATIVE DRIVER ---
    print(f"Attempting login for user: '{NEO4J_USER}' to URI: '{NEO4J_URI}'")
    setup_database_schema(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))

    # --- STEP 1: LOAD DOCUMENTS ---
    json_path = os.path.join("data", "tn_schemes.json")
    try:
        documents = load_and_clean_documents(json_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # --- STEP 2 & 3: LLM GRAPH EXTRACTION (ASYNC) ---
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=NODE_LABELS,
        allowed_relationships=["OFFERS", "PROVIDES", "BENEFITS"],
    )

    print("\nStep 2 & 3 [Entity Extraction]: Extracting graph structures concurrently via LLM...")
    # Asynchronously process documents to speed up API processing time
    graph_documents = await transformer.aconvert_to_graph_documents(documents)
    print(f"[Entity Extraction] Successfully generated {len(graph_documents)} graph documents.")

    # --- STEP 4: GRAPH STORAGE (LANGCHAIN NEO4J INTEGRATION) ---
    print("\nStep 4 [Graph Storage]: Connecting LangChain Neo4j client...")
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
    )

    print("[Graph Storage] Saving extracted nodes and relationships into Neo4j...")
    graph.add_graph_documents(
        graph_documents
    )

    print("\nPipeline Complete! Knowledge Graph successfully built in Neo4j.")

    fetch_and_print_graph_summary()



def fetch_and_print_graph_summary():
    # Cypher query to retrieve structured records
    cypher_query = """
    MATCH (d:Department)-[:OFFERS]->(s:Scheme)
    OPTIONAL MATCH (s)-[:PROVIDES]->(b:Benefit)
    OPTIONAL MATCH (s)-[:BENEFITS]->(t:TargetAudience)
    RETURN 
        d.id AS department,
        s.id AS scheme,
        collect(DISTINCT b.id) AS benefits,
        collect(DISTINCT t.id) AS audience
    ORDER BY scheme ASC
    """

    print("\n" + "=" * 80)
    print(" KNOWLEDGE GRAPH SUMMARY: TAMIL NADU FARMER SCHEMES")
    print("=" * 80)

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            results = session.run(cypher_query)
            records = list(results)

            if not records:
                print("No graph data found. Make sure the extraction pipeline ran successfully.")
                return

            print(f" Total Schemes Found: {len(records)}\n")

            for idx, record in enumerate(records, 1):
                dept = record["department"] or "Not Specified"
                scheme = record["scheme"] or "Unknown Scheme"
                benefits = record["benefits"] or ["None specified"]
                audience = record["audience"] or ["General"]

                print(f"[{idx}] SCHEME: {scheme}")
                print(f"    Department : {dept}")
                print(f"    Audience   : {', '.join(audience)}")
                print("    Benefits   :")
                for benefit in benefits:
                    print(f"      - {benefit}")
                print("-" * 80)

if __name__ == "__main__":
    # Run the main asynchronous pipeline loop
    asyncio.run(run_knowledge_graph_pipeline())