from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import (
    OPENAI_CHAT_MODEL,
    TOP_K,
)

from app.vector_store import load_faiss_index


SYSTEM_PROMPT = """
You are a helpful Farmer Scheme Assistant.

Your job is to answer questions about farmer schemes
using ONLY the information provided in the retrieved context.

Rules:

1. Do not invent scheme information.
2. Do not assume eligibility that is not present in the context.
3. Do not invent subsidy amounts.
4. Do not invent application procedures.
5. If the answer is not available in the context,
   clearly say that the information is not available
   in the provided farmer scheme database.
6. When appropriate, provide:
   - Scheme Name
   - Department
   - Description
   - Eligibility
   - Documents Required
   - GO & Guidelines
7. Keep the response clear and farmer-friendly.
8. If multiple schemes match, list the relevant schemes.
9. Mention that eligibility/application details should be
   verified with the concerned department when appropriate.

Retrieved Context:

{context}
"""


def create_llm():

    return ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        temperature=0,
    )


def create_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            (
                "human",
                "{question}",
            ),
        ]
    )


def format_documents(documents):

    formatted = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        formatted.append(
            f"""
--- Scheme {index} ---

{document.page_content}
""".strip()
        )

    return "\n\n".join(formatted)


def ask_question(question: str):

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    vector_store = load_faiss_index()

    documents = vector_store.similarity_search(
        question,
        k=TOP_K,
    )

    if not documents:
        return {
            "answer": (
                "I could not find any relevant farmer "
                "scheme information."
            ),
            "sources": [],
        }

    context = format_documents(
        documents
    )

    prompt = create_prompt()

    llm = create_llm()

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    sources = []

    for document in documents:

        sources.append(
            {
                "scheme": document.metadata.get(
                    "scheme"
                ),
                "department": document.metadata.get(
                    "department"
                ),
                "sno": document.metadata.get(
                    "sno"
                ),
            }
        )

    return {
        "answer": response.content,
        "sources": sources,
    }