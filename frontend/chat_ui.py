
import os
import requests
import streamlit as st


API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_ENDPOINT = f"{API_URL}/chat"

st.set_page_config(
    page_title="Company AI Assistant",
    page_icon="💬",
    layout="centered",
)

# -----------------------------
# Page styling
# -----------------------------

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

        .source-box {
            padding: 12px;
            border-radius: 8px;
            margin-top: 8px;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------

st.title("💬 Company AI Assistant")

st.write(
    "Ask questions about our products, guides, "
    "and company documentation."
)

st.caption(
    "Answers are generated using company documents "
    "and include source references when available."
)


# -----------------------------
# Helper: display unique sources
# -----------------------------

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
            # Use plain text rather than Markdown so filenames
            # containing underscores display correctly.
            page_text = f"Page {page}" if page is not None else "Page unknown"
            st.markdown(f"- `{document}` — {page_text}")


# -----------------------------
# Session state
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Display conversation history
# -----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            display_sources(message["sources"])


# -----------------------------
# Chat input
# -----------------------------

question = st.chat_input("Ask a question about our documents...")


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
        try:
            with st.spinner("Searching company documents..."):
                response = requests.post(
                    CHAT_ENDPOINT,
                    json={"question": question},
                    timeout=90,
                )

                response.raise_for_status()
                result = response.json()

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

        except requests.exceptions.Timeout:
            st.error(
                "The request took too long. Please try again."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the chatbot API. "
                "Check that FastAPI is running at "
                "http://127.0.0.1:8000."
            )

        except requests.exceptions.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else "unknown"
            )

            st.error(
                f"The chatbot API returned HTTP {status_code}. "
                "Please try again."
            )

        except (ValueError, requests.exceptions.RequestException):
            st.error(
                "An unexpected API response occurred. "
                "Please try again."
            )

        except Exception:
            st.error(
                "Something went wrong while processing your question."
            )


# -----------------------------
# Sidebar
# -----------------------------

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