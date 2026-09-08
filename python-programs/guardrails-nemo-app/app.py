import asyncio
import os
import traceback

from dotenv import load_dotenv

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# ============================================================
# STEP 1 - APPLICATION START
# ============================================================

print("\n" + "=" * 70)
print("[1] APPLICATION START")
print("=" * 70)


# ============================================================
# STEP 2 - LOAD ENVIRONMENT
# ============================================================

print("\n[2] Loading environment variables...")

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is missing")

print("[2.1] OPENAI_API_KEY found")


# ============================================================
# STEP 3 - LOAD KNOWLEDGE
# ============================================================

print("\n[3] Loading sample.txt...")


with open(
    "sample.txt",
    "r",
    encoding="utf-8"
) as file:

    knowledge = file.read()


print("[3.1] sample.txt loaded")
print(f"[3.2] Knowledge characters: {len(knowledge)}")


# ============================================================
# STEP 4 - CREATE OPENAI LLM
# ============================================================

print("\n[4] Creating OpenAI LLM...")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("[4.1] OpenAI LLM created")


# ============================================================
# STEP 5 - CREATE APPLICATION PROMPT
# ============================================================

print("\n[5] Creating LangChain prompt...")


prompt = ChatPromptTemplate.from_template(
    """
You are a Company Policy Assistant.

Answer the user's question using ONLY the company
knowledge provided below.

If the answer is not available in the knowledge,
say:

"The information is not available in the company knowledge."

Company Knowledge:
------------------
{knowledge}
------------------

User Question:
{question}

Provide a concise and professional answer.
"""
)


print("[5.1] LangChain prompt created")


# ============================================================
# STEP 6 - CREATE LANGCHAIN CHAIN
# ============================================================

print("\n[6] Creating LangChain chain...")


chain = prompt | llm


print("[6.1] LangChain chain created")


# ============================================================
# STEP 7 - LOAD NEMO GUARDRAILS
# ============================================================

print("\n[7] Loading NeMo Guardrails...")

config = RailsConfig.from_path("./config")

print("[7.1] NeMo configuration loaded")


# ============================================================
# STEP 8 - WRAP LANGCHAIN WITH NEMO
# ============================================================

print("\n[8] Creating RunnableRails...")

guardrails = RunnableRails(
    config=config,
    runnable=chain,
    verbose=True
)

print("[8.1] RunnableRails created")
print("[8.2] LangChain chain wrapped with NeMo")


# ============================================================
# STEP 9 - PROCESS USER QUESTION
# ============================================================

async def ask_question(question):

    print("\n")
    print("=" * 70)
    print("[9] PROCESSING QUESTION")
    print("=" * 70)

    print(f"[9.1] User:")
    print(f"      {question}")


    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    print("\n[9.2] Sending question to NeMo")


    try:

        result = await guardrails.ainvoke(
            {
                "question": question,
                "knowledge": knowledge
            }
        )


    except Exception as error:

        print("\n[ERROR] NeMo execution failed")

        print(error)

        traceback.print_exc()

        return


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print("\n[9.3] NeMo returned result")

    print(f"[9.4] Result type: {type(result)}")

    print(f"[9.5] Raw result:")
    print(result)


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    print("\n[9.6] FINAL RESPONSE")

    if isinstance(result, dict):

        output = result.get("output")

        print(output)

    else:

        print(result)


# ============================================================
# STEP 10 - COMMAND LINE
# ============================================================

async def main():

    print("\n")
    print("=" * 70)
    print(" NeMo Guardrails + LangChain Command Line Application")
    print("=" * 70)

    print("\nType your question.")
    print("Type 'exit' to stop.")

    while True:

        print("\n" + "-" * 70)

        question = input("Enter question: ").strip()


        if question.lower() == "exit":

            print("\nApplication stopped.")

            break


        if not question:

            print("Please enter a question.")

            continue


        await ask_question(question)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())