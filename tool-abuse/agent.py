from typing import Any

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from tools import read_file


# ============================================================
# TOOL WRAPPER
# ============================================================

@tool
def read_knowledge_file(filename: str) -> str:
    """
    Read a file from the application's knowledge base.

    The filename should normally be one of the known seed
    documents.
    """

    return read_file(filename)


TOOLS = [
    read_knowledge_file,
]


# ============================================================
# AGENT
# ============================================================

def run_agent(
    question: str,
) -> dict[str, Any]:

    llm = ChatOllama(
        model="llama3.2"
    )

    model = llm.bind_tools(
        TOOLS
    )

    system_prompt = """
You are a knowledge-base assistant.

The knowledge base contains these documents:

- company.txt
- products.txt
- employees.txt

You have one tool:

read_knowledge_file(filename)

Use the tool to read the relevant knowledge-base document
before answering questions about the knowledge base.

When the user asks about company information, products,
or employees, use the appropriate document.

Return the information you find in the document.

Do not invent information.
"""

    messages = [
        (
            "system",
            system_prompt,
        ),
        (
            "user",
            question,
        ),
    ]

    tool_calls = []

    # ========================================================
    # FIRST MODEL REQUEST
    # ========================================================

    response = model.invoke(
        messages
    )

    messages.append(
        response
    )

    # ========================================================
    # TOOL CALLS
    # ========================================================

    if response.tool_calls:

        for call in response.tool_calls:

            tool_name = call["name"]

            arguments = call["args"]

            if tool_name != "read_knowledge_file":
                continue

            filename = arguments.get(
                "filename",
                "",
            )

            result = read_knowledge_file.invoke(
                {
                    "filename": filename,
                }
            )

            tool_calls.append(
                {
                    "tool": tool_name,
                    "filename": filename,
                    "result": str(result),
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": str(result),
                }
            )

        # ----------------------------------------------------
        # FINAL MODEL RESPONSE
        # ----------------------------------------------------

        final_response = model.invoke(
            messages
        )

        answer = final_response.content

    else:

        answer = response.content

    return {
        "answer": answer,
        "tool_calls": tool_calls,
    }