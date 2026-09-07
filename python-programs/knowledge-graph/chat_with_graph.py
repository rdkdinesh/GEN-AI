import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- PROMPT TEMPLATE WITH DOUBLE ESCAPED CURLY BRACES ---
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a Neo4j graph database.
Instructions:
1. Use ONLY the provided node labels and relationship types from the schema:
   Node Labels: [Department, Scheme, Benefit, TargetAudience]
   Relationships:
     - (Department)-[:OFFERS]->(Scheme)
     - (Scheme)-[:PROVIDES]->(Benefit)
     - (Scheme)-[:BENEFITS]->(TargetAudience)

2. ALWAYS use case-insensitive string matching with `toLower()` and `CONTAINS` for filtering properties.
   Do NOT use exact match syntax like {{id: 'small farmers'}}. 
   Example: WHERE toLower(t.id) CONTAINS toLower('small farmers')

3. Return node properties like s.id, d.id, b.id, t.id.

Schema:
{schema}

Question: {question}
Cypher Query:"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)


def start_graph_chat():
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD
    )
    graph.refresh_schema()

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    cypher_chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        cypher_prompt=cypher_prompt,  # Pass the corrected prompt template
        verbose=True,
        allow_dangerous_requests=True
    )

    print("\n" + "=" * 80)
    print(" KNOWLEDGE GRAPH AI ASSISTANT READY")
    print("=" * 80 + "\n")

    while True:
        try:
            user_query = input("User > ")
            if user_query.strip().lower() in ["exit", "quit", "q"]:
                break
            if not user_query.strip():
                continue

            print("\nSearching Knowledge Graph...")
            response = cypher_chain.invoke({"query": user_query})

            print("\nAI Assistant:")
            print(response["result"])
            print("-" * 80 + "\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError processing query: {e}\n")


if __name__ == "__main__":
    start_graph_chat()