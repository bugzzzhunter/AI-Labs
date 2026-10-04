import os
from pathlib import Path

import streamlit as st

from agents import run_pipeline


# ============================================================
# CONFIG
# ============================================================

UPLOAD_DIR = "uploads"

Path(UPLOAD_DIR).mkdir(
    exist_ok=True
)

st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📄 Document Summarizer"
)

st.markdown(
    """
### Upload a document and receive the processed information

This application accepts a text document, processes it
through a multi-agent backend, and returns the resulting
information to the user.

**Processing workflow:**

1. Upload a `.txt` document.
2. The **Document Summarizer Agent** reads the document
   and creates a summary.
3. The summary is passed to the **Information Extractor
   Agent**.
4. The Extractor Agent extracts relevant information.
5. The processed information is returned to the user.
"""
)


# ============================================================
# APPLICATION ARCHITECTURE
# ============================================================

with st.expander(
    "🔎 View Application Architecture"
):

    st.code(
        """
                    USER
                      │
                      │ Upload .txt
                      ▼
              ┌─────────────────┐
              │   Agent 1       │
              │   Summarizer    │
              │                 │
              │ Backend API Key │
              │      A          │
              └────────┬────────┘
                       │
                       │ Summary
                       ▼
              ┌─────────────────┐
              │   Agent 2       │
              │   Extractor     │
              │                 │
              │ Backend API Key │
              │      B          │
              └────────┬────────┘
                       │
                       │ Extracted data
                       ▼
                    USER
        """,
        language="text"
    )

    st.info(
        """
        This application is also used as a security
        laboratory.

        Each backend agent has its own separate,
        lab-only API key.

        The security exercise is to investigate whether
        attacker-controlled document content can cause
        either agent to disclose information from its
        private configuration.

        The API keys used for this exercise are dummy
        credentials and do not provide access to any
        real service.
        """
    )


# ============================================================
# UPLOAD
# ============================================================

st.header(
    "1. Upload Your Document"
)

st.write(
    "Upload a text file to have it summarized and processed."
)

uploaded_file = st.file_uploader(
    "Choose a .txt file",
    type=["txt"],
    accept_multiple_files=False
)


# ============================================================
# PROCESS
# ============================================================

if uploaded_file:

    file_path = os.path.join(
        UPLOAD_DIR,
        uploaded_file.name
    )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    with open(
        file_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )

    st.success(
        f"File uploaded: {uploaded_file.name}"
    )

    # --------------------------------------------------------
    # Show document
    # --------------------------------------------------------

    with st.expander(
        "📄 View Uploaded Document"
    ):

        document_text = uploaded_file.getvalue().decode(
            "utf-8",
            errors="replace"
        )

        st.text(
            document_text
        )

    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    if st.button(
        "▶ Summarize and Process Document",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Processing document through the multi-agent pipeline..."
        ):

            try:

                result = run_pipeline(
                    file_path
                )

                st.session_state[
                    "pipeline_result"
                ] = result

            except Exception as ex:

                st.error(
                    f"Pipeline error: {ex}"
                )


# ============================================================
# RESULTS
# ============================================================

if "pipeline_result" in st.session_state:

    result = st.session_state[
        "pipeline_result"
    ]

    st.divider()

    # --------------------------------------------------------
    # AGENT 2 OUTPUT
    # --------------------------------------------------------

    st.header(
        "2. Extracted Information"
    )

    st.caption(
        "Output generated by Agent 2 — Information Extractor"
    )

    st.write(
        result.get(
            "extracted_info",
            "No extracted information available."
        )
    )


# ============================================================
# SECURITY LAB INFORMATION
# ============================================================

st.divider()

with st.expander(
    "🔐 Security Laboratory Information"
):

    st.markdown(
        """
### Multi-Agent Trust Boundary

The application consists of two independent agents.

**Agent 1 — Document Summarizer**

- Receives the user-uploaded document.
- Has its own backend API key.
- Generates a summary.
- Writes the summary for the next stage.

**Agent 2 — Information Extractor**

- Receives the output produced by Agent 1.
- Has a different backend API key.
- Extracts information from the summary.
- Returns the result to the user.

The security objective is to investigate whether
attacker-controlled content can cross these trust
boundaries and cause either agent to disclose its
private configuration.

```text
User-controlled document
          │
          ▼
     Agent 1
   Summarizer
          │
          │ Agent 1 output
          ▼
     Agent 2
    Extractor
          │
          ▼
        User
````

The two API keys are intentionally dummy laboratory
values and must not be replaced with production
credentials.
"""
)
