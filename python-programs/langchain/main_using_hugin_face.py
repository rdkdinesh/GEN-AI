from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from pathlib import Path

# 1. Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

# 2. Read the API keys, langsmith from environment variables
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")
langsmith_tracing = os.getenv("LANGSMITH_TRACING")

if not huggingface_api_key:
    raise ValueError("HUGGINGFACE_API_KEY is missing from the project .env file")

# 3. Set the API key for LangSmith, Tracing
os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
os.environ["LANGSMITH_PROJECT"] = langsmith_project
os.environ["LANGSMITH_TRACING"] = langsmith_tracing

print("Token: ", huggingface_api_key)
print("LangSmith Connection Established Successfully!")

# 4. Create a prompt template for generating company names based on a product
prompt = ChatPromptTemplate.from_template("What is a good name for a company that makes {product}?")

# Load the HuggingFace model for chat, specifying the repository ID and model parameters
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=huggingface_api_key,
    max_new_tokens=512,
    temperature=0.7,
)

# 5. Chat model free of cost using HuggingFaceHub
model = ChatHuggingFace(llm=llm)

# 6. Create a chain that combines the prompt and the model
chain = prompt | model | StrOutputParser()

# 7. Output the result of invoking the chain with a specific product
print(chain.invoke({"product": "colorful socks"}))

# 8. Standardize usage metadata
print("Input Token: ", chain.usage_metadata.input_tokens)
print("Output Token: ", chain.usage_metadata.output_tokens)
print("Total Token: ", chain.usage_metadata.total_tokens)