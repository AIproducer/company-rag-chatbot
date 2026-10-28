import streamlit as st
from app.rag_pipeline import answer_question

st.set_page_config(
page_title="Company AI Assistant",
page_icon="💬",
layout="centered",
)

st.markdown(
"""
<style>
.main .block-container {
max-width: 850px;
padding-top: 2rem;
padding-bottom: 3rem;
}
.stChatMessage {
border-radius: 12px;
}
</style>
""",
unsafe_allow_html=True,
)

st.title("💬 Company AI Assistant")

st.write(
"Ask questions about our products, guides, "
"and company documentation."
)

st.caption(
"Answers are generated using company documents "
"and include source references when available."
)

def display_sources(sources):
"""Display unique document and page references."""

if not sources:
    st.caption("No source references available.")
    return

unique_sources = []
seen = set()

for source in sources:
    document = source.get("document_name") or "Unknown document"
    page = source.get("page_number")
    key = (document, page)

    if key not in seen:
        seen.add(key)
        unique_sources.append((document, page))

with st.expander("📚 View sources"):
    for document, page in unique_sources:
        page_text = (
            f"Page {page}"
            if page is not None
            else "Page unknown"
        )
        st.markdown(f"- `{document}` — {page_text}")

if "messages" not in st.session_state:
st.session_state.messages = []

Display conversation history

for message in st.session_state.messages:
with st.chat_message(message["role"]):
st.markdown(message["content"])

    if message["role"] == "assistant" and message.get("sources"):
        display_sources(message["sources"])

Handle new questions

question = st.chat_input("Ask a question about our documents...")

if question:
st.session_state.messages.append(
{"role": "user", "content": question}
)

with st.chat_message("user"):
    st.markdown(question)

with st.chat_message("assistant"):
    try:
        with st.spinner("Searching company documents..."):
            result = answer_question(question)

        answer = result.get(
            "answer",
            "I couldn't generate an answer.",
        )
        sources = result.get("sources") or []

        st.markdown(answer)

        if sources:
            display_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

    except Exception:
        st.error(
            "Something went wrong while processing your question. "
            "Please try again."
        )

with st.sidebar:
st.header("About")

st.write(
    "This assistant searches company documentation "
    "to answer questions using available evidence."
)

st.info(
    "The assistant should acknowledge when the "
    "available documents do not contain enough information."
)

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

st.divider()

st.caption("Company RAG Chatbot · Development Version")
