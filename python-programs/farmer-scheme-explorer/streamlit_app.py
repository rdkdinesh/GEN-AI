import streamlit as st

from app.rag_chain import ask_question


st.set_page_config(
    page_title="Tamil Nadu Farmer Scheme Assistant",
    page_icon="🌾",
    layout="wide",
)


st.title("🌾 Tamil Nadu Farmer Scheme Assistant")

st.caption(
    "Ask questions about farmer schemes "
    "available in the scheme database."
)


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask about farmer schemes..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching farmer schemes..."
        ):

            try:

                result = ask_question(
                    question
                )

                answer = result["answer"]

                st.markdown(answer)

                sources = result.get(
                    "sources",
                    [],
                )

                if sources:

                    with st.expander(
                        "Retrieved Schemes"
                    ):

                        for source in sources:

                            st.markdown(
                                f"""
**Scheme:** {source.get("scheme", "")}

**Department:** {source.get("department", "")}

**S.No:** {source.get("sno", "")}

---
"""
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as exc:

                error_message = (
                    "Sorry, I could not process "
                    f"your question.\n\nError: {exc}"
                )

                st.error(
                    error_message
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )