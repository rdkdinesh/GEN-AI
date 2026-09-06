import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Load environment variables (.env file)
load_dotenv()

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="GenAI Tech Explainer", 
    page_icon="💡", 
    layout="centered"
)

st.title("💡 Tech Explainer AI")
st.subheader("Understand complex technical concepts with custom analogies")

# --- User Inputs ---
topic = st.text_input(
    "Enter a Technical Concept:", 
    placeholder="e.g., Vector Databases, RAG, Kubernetes, Attention Mechanism"
)

style = st.selectbox(
    "Choose Explanation Style:",
    [
        "Simple, metaphor-heavy 10-year-old friendly",
        "Funny kitchen/cooking analogy",
        "Pirate speaking in sea terms",
        "Executive summary for busy CEOs",
        "Sci-Fi / Superhero comic book style"
    ]
)

# --- Generate Button ---
if st.button("Explain It!"):
    if not topic.strip():
        st.warning("Please enter a topic first!")
    else:
        # Show a spinner while waiting for the LLM response
        with st.spinner("Crafting your explanation..."):
            # 1. Prompt
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are an expert tech educator. Explain {topic} in a {style} style."),
                ("human", "Explain {topic} to me.")
            ])

            # 2. Model
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

            # 3. Output Parser
            output_parser = StrOutputParser()

            # 4. LCEL Chain
            chain = prompt_template | model | output_parser

            # 5. Execute Chain
            response = chain.invoke({
                "topic": topic,
                "style": style
            })

            # Display Output in a nice UI card
            st.markdown("### Explanation:")
            st.success(response)