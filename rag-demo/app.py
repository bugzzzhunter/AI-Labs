from pathlib import Path

import streamlit as st

from rag import (
    get_vectorstore,
    initialize_seed_data,
    retrieve_documents,
    answer_question,
    reset_knowledge_base,
    get_chunk_count,
)

from ingest import ingest_file


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).parent

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    exist_ok=True
)


st.set_page_config(
    page_title="RAG Security Lab",
    page_icon="🔐",
    layout="wide",
)


# ============================================================
# INITIALIZATION
# ============================================================

try:

    initialize_seed_data()

except Exception as ex:

    st.error(
        f"Could not initialize knowledge base: {ex}"
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "🔐 RAG Security Lab"
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    st.subheader(
        "Upload Document"
    )

    uploaded_file = st.file_uploader(
        "Upload a TXT file",
        type=["txt"],
    )

    if uploaded_file:

        if st.button(
            "Index Document",
            use_container_width=True,
        ):

            try:

                filename = Path(
                    uploaded_file.name
                ).name

                destination = (
                    UPLOAD_DIR / filename
                )

                with open(
                    destination,
                    "wb"
                ) as f:

                    f.write(
                        uploaded_file.getbuffer()
                    )

                vectorstore = get_vectorstore()

                chunks = ingest_file(
                    path=destination,
                    vectorstore=vectorstore,
                    is_seed=False,
                )

                st.success(
                    f"{filename} indexed "
                    f"({chunks} chunks)."
                )

            except Exception as ex:

                st.error(
                    f"Upload failed: {ex}"
                )

    st.divider()

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    st.subheader(
        "Knowledge Base"
    )

    chunk_count = get_chunk_count()

    st.metric(
        "Indexed chunks",
        chunk_count,
    )

    st.divider()

    # --------------------------------------------------------
    # UPLOADED FILES
    # --------------------------------------------------------

    st.subheader(
        "User Documents"
    )

    uploaded_files = list(
        UPLOAD_DIR.glob("*.txt")
    )

    if uploaded_files:

        for file in uploaded_files:

            st.write(
                f"📄 {file.name}"
            )

    else:

        st.caption(
            "No user documents."
        )

    st.divider()

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if st.button(
        "♻️ Reset Knowledge Base",
        type="primary",
        use_container_width=True,
    ):

        try:

            reset_knowledge_base()

            st.session_state.messages = []

            st.success(
                "Knowledge base reset. "
                "Only seed data remains."
            )

            st.rerun()

        except Exception as ex:

            st.error(
                f"Reset failed: {ex}"
            )

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN
# ============================================================

st.title(
    "🔐 RAG Security Laboratory"
)

st.markdown(
    """
This application provides a deliberately simple RAG
environment for security testing and training.

### Lab workflow

1. Start with the trusted seed document.
2. Ask questions about the company.
3. Upload a TXT document.
4. Ask questions again.
5. Inspect the retrieved context.
6. Experiment with conflicting or malicious content.
7. Reset the knowledge base to restore the trusted seed.
"""
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and "context" in message
        ):

            with st.expander(
                "🔎 Retrieved Context"
            ):

                st.text(
                    message["context"]
                )


# ============================================================
# CHAT
# ============================================================

question = st.chat_input(
    "Ask a question about the knowledge base..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    try:

        documents = retrieve_documents(
            question
        )

        answer, context = answer_question(
            question,
            documents,
        )

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )

            with st.expander(
                "🔎 Retrieved Context"
            ):

                st.text(
                    context
                )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "context": context,
            }
        )

    except Exception as ex:

        st.error(
            f"RAG error: {ex}"
        )
