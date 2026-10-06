import streamlit as st

from agent import run_agent


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Tool Injection Lab",
    page_icon="🧪",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🧪 AI Tool Injection / Path Traversal Lab"
)

st.markdown(
    """
This application demonstrates a vulnerable AI file-reading
tool.

The intended workflow is:

```text
User
  |
  v
AI Agent
  |
  v
read_knowledge_file()
  |
  v
Seed documents
  |
  v
AI response
The read_knowledge_file() implementation intentionally
fails to validate the requested filename.

This allows a security engineer to investigate what happens
when a tool receives a path containing traversal components.
"""
)

#============================================================
#KNOWLEDGE BASE
#============================================================

st.header(
"Knowledge Base"
)

st.markdown(
"""
The agent is expected to use these three seed documents:

company.txt
products.txt
employees.txt
"""
)
#============================================================
#USER QUESTION
#============================================================

st.header(
"Ask the Agent"
)

question = st.text_area(
"Question",
placeholder=(
"Example: Who is the CEO of the company?"
),
height=120,
)

if st.button(
"Ask Agent",
type="primary",
use_container_width=True,
):

    if not question.strip():

        st.warning(
            "Enter a question first."
        )

    else:

        with st.spinner(
            "Agent is processing the request..."
        ):

            try:

                result = run_agent(
                    question
                )

                st.session_state[
                    "agent_result"
                ] = result

            except Exception as ex:

                st.error(
                    "Agent error: "
                    + str(ex)
                )
#============================================================
#RESULT
#============================================================

if "agent_result" in st.session_state:

    result = st.session_state[
        "agent_result"
    ]

    st.divider()

    st.header(
        "Agent Response"
    )

    st.write(
        result["answer"]
    )

    st.header(
        "Tool Activity"
    )

    if result["tool_calls"]:

        for index, call in enumerate(
            result["tool_calls"],
            start=1,
        ):

            with st.expander(
                "Tool Call "
                + str(index)
            ):

                st.write(
                    "**Tool:** "
                    + call["tool"]
                )

                st.write(
                    "**Requested filename:**"
                )

                st.code(
                    call["filename"]
                )

                st.write(
                    "**Tool result:**"
                )

                st.code(
                    call["result"],
                    language="text",
                )

    else:

        st.info(
            "The agent did not call the file-reading tool."
        )
#============================================================
#SECURITY INFORMATION
#============================================================

st.divider()

with st.expander(
"Security Architecture"
):

    st.markdown(
        """
    Intended design
                        User
                        |
                        v
                        LLM
                        |
                        v
                read_knowledge_file
                        |
                        v
                    seed/*.txt
    Vulnerable implementation
    filename
        |
        v
    os.path.join("seed", filename)
        |
        v
    open(path)

    There is no authorization check between the filename
    supplied by the agent and the filesystem operation.

    A secure implementation would resolve the requested path
    and verify that the resulting canonical path remains inside
    the approved knowledge-base directory.

    Security lesson

    The LLM should not be considered a filesystem authorization
    boundary.

    Even if the system prompt says:

    "Only read the three knowledge-base files"

    the application itself must enforce that restriction.
    """
    )