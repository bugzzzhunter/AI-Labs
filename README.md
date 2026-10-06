# AI Labs

This repository contains a small collection of interactive AI security and prompt-injection labs built with Python, Streamlit, and LangChain. Each demo is designed for hands-on experimentation with unsafe AI behaviors in a controlled environment.

The project includes:

- a multi-agent indirect prompt injection lab
- a retrieval-augmented generation (RAG) security lab
- a tool-injection / path traversal demo

> These applications are intentionally designed to demonstrate insecure patterns for educational and research purposes. They should only be used in isolated lab environments.

## Project Structure

```text
AI Labs/
├── README.md
├── requirements.txt
├── multi-agent-indirect-prompt-injection/
│   ├── agents.py
│   ├── app.py
│   ├── requirements.txt
│   ├── SampleAttackFile.txt
│   ├── summarized/
│   └── uploads/
├── rag-demo/
│   ├── app.py
│   ├── ingest.py
│   ├── rag.py
│   ├── requirements.txt
│   ├── chroma_db/
│   ├── seed_data/
│   └── uploads/
└── tool-injection/
    ├── agent.py
    ├── app.py
    ├── requirements.txt
    ├── tools.py
    ├── lab_files/
    └── seed/
```
*Refer A2A-RogueAgent README.md for it's project stucture.

## Applications

### 1) Multi-Agent Indirect Prompt Injection

Location: `multi-agent-indirect-prompt-injection/`

This app simulates a document summarization workflow across two agents:

1. a summarizer agent reads uploaded content
2. an extractor agent processes the summary

The lab is meant to test whether attacker-controlled document content can influence agent behavior and lead to leakage of secret values. The app includes intentionally fake lab-only API keys for demonstration. There are 2 agents summarizer and extraction. Both the agents have a secret API key for you to extract.

Run it with:

```bash
streamlit run multi-agent-indirect-prompt-injection/app.py
```

### 2) RAG Security Lab

Location: `rag-demo/`

This project implements a minimal RAG workflow. It initializes a local vector store, ingests seed documents, lets the user upload additional text files, and answers questions against the indexed knowledge base.

The goal is to explore how retrieval systems behave when documents are added or manipulated and how this can affect response quality and security.

Run it with:

```bash
streamlit run rag-demo/app.py
```

### 3) Tool Abuse / Path Traversal Lab

Location: `tool-abuse/`

This app demonstrates a vulnerable AI file-reading tool. The agent is expected to read files from a safe knowledge base, but the tool implementation permits unrestricted filename input, which can allow path traversal into files outside the allowed set.

Run it with:

```bash
streamlit run tool-abuse/app.py
```

### 4) A2A-RogueAgent

Location: `A2A-RogueAgent/`

This app demonstrates a vulnerable A2A implementation for multi-agent architecture. It is possible to register a rogue agent and modify any data the agent has access to.   

Refer to A2A-RogueAgent/README.md for more details.

## Setup

### Prerequisites

- Python 3.10+
- pip
- Ollama installed locally
- the `llama3.2` model pulled in Ollama

Install the model with:

```bash
ollama pull llama3.2
```

### Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

Install the shared project dependencies:

```bash
pip install -r requirements.txt
```

Or install the dependencies for a specific lab:

```bash
pip install -r multi-agent-indirect-prompt-injection/requirements.txt
pip install -r rag-demo/requirements.txt
pip install -r tool-injection/requirements.txt
```

## Typical Workflow

1. Activate the virtual environment.
2. Install dependencies.
3. Start Ollama and ensure the required model is available.
4. Run the target Streamlit app.
5. Upload files, test prompts, and explore the behavior in the app UI.


