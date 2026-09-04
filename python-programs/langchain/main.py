from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

# 1. Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Read the API keys from environment variables
openai_api_key = os.getenv("OPEN_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")
langsmith_tracing = os.getenv("LANGSMITH_TRACING")

# 2. Set the API key for OpenAI, LangChain, and LangSmith, Tracing
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
os.environ["LANGSMITH_PROJECT"] = langsmith_project
os.environ["LANGSMITH_TRACING"] = langsmith_tracing

print("LangSmith Connection Established Successfully!")

prompt = ChatPromptTemplate.from_template("What is a good name for a company that makes {product}?")
model = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | model | StrOutputParser()

#This is run automatically when the script is executed
print(chain.invoke({"product": "colorful socks"}))