import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_ollama import OllamaLLM


# ============================================================
# CODE REVIEW AGENT
# ============================================================

app = FastAPI(
    title="Code Review Agent",
    description="A2A security code review agent",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
SOURCE_FILE = (
    BASE_DIR
    / "vulnerable_app"
    / "app.py"
)

REPORT_DIR = (
    BASE_DIR
    / "audit_report"
)

REPORT_FILE = (
    REPORT_DIR
    / "code_audit.json"
)


# ============================================================
# LLM
# ============================================================

llm = OllamaLLM(
    model="llama3.2"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class Task(BaseModel):
    task: str


# ============================================================
# READ SOURCE CODE
# ============================================================

def read_source_code():

    if not SOURCE_FILE.exists():

        raise FileNotFoundError(
            f"Source file not found: {SOURCE_FILE}"
        )

    with open(
        SOURCE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


# ============================================================
# EXTRACT JSON FROM LLM RESPONSE
# ============================================================

def extract_json(response: str):

    response = response.strip()

    # Handle markdown JSON blocks such as:
    #
    # ```json
    # {...}
    # ```

    if response.startswith("```"):

        lines = response.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        response = "\n".join(lines).strip()

    try:

        return json.loads(response)

    except json.JSONDecodeError:

        # Try to locate the JSON object in the response.

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "LLM did not return valid JSON."
            )

        try:

            return json.loads(
                response[start:end + 1]
            )

        except json.JSONDecodeError as ex:

            raise ValueError(
                f"Could not parse LLM JSON response: {ex}"
            )


# ============================================================
# SECURITY CODE AUDIT
# ============================================================

def perform_security_audit():

    source_code = read_source_code()

    prompt = f"""
You are an application security code-review agent.

Perform a security audit of the Python source code below.

Identify vulnerabilities and security weaknesses that are
actually supported by the source code.

Focus on:

- Injection vulnerabilities
- Hardcoded credentials or secrets
- Authentication and authorization weaknesses
- Sensitive information disclosure
- Verbose error handling
- Insecure file handling
- Cryptographic weaknesses
- Security logging and monitoring weaknesses
- Unsafe configuration
- Other significant application security issues

Do not invent vulnerabilities.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "application": "vulnerable_app",
    "overall_risk": "CRITICAL|HIGH|MEDIUM|LOW",
    "production_ready": true,
    "findings": [
        {{
            "id": "CR-001",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "category": "string",
            "issue": "short vulnerability name",
            "description": "technical description",
            "evidence": "specific code or behavior supporting the finding",
            "recommendation": "specific remediation",
            "line_reference": "line number or relevant code location"
        }}
    ],
    "summary": {{
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "total": 0
    }}
}}

Important:

1. Only report vulnerabilities supported by the supplied
   source code.

2. Do not report hypothetical vulnerabilities without
   evidence.

3. Set production_ready to false when critical or high
   severity vulnerabilities are present.

4. Ensure the summary counts exactly match the findings.

5. Return JSON only. Do not include markdown.

SOURCE CODE:

---------------- BEGIN SOURCE ----------------

{source_code}

----------------- END SOURCE -----------------
"""

    response = llm.invoke(prompt)

    audit = extract_json(response)

    if not isinstance(audit, dict):

        raise ValueError(
            "Security audit response must be a JSON object."
        )

    findings = audit.get(
        "findings",
        []
    )

    if not isinstance(findings, list):

        raise ValueError(
            "'findings' must be a list."
        )

    # Recalculate summary instead of trusting the LLM's
    # counts.

    critical = sum(
        1
        for finding in findings
        if finding.get("severity") == "CRITICAL"
    )

    high = sum(
        1
        for finding in findings
        if finding.get("severity") == "HIGH"
    )

    medium = sum(
        1
        for finding in findings
        if finding.get("severity") == "MEDIUM"
    )

    low = sum(
        1
        for finding in findings
        if finding.get("severity") == "LOW"
    )

    total = len(findings)

    audit["summary"] = {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "total": total,
    }

    audit["application"] = "vulnerable_app"

    audit["source_file"] = str(
        SOURCE_FILE.relative_to(BASE_DIR)
    )

    audit["production_ready"] = (
        critical == 0 and high == 0
    )

    # Make sure the report directory exists.

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            audit,
            f,
            indent=4
        )

    return audit


# ============================================================
# A2A TASK ENDPOINT
# ============================================================

@app.post("/a2a/task")
def process_task(task: Task):

    try:

        audit = perform_security_audit()

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

    return {
        "agent": "code-review-agent",
        "type": "code_review_result",
        "status": "completed",
        "task": task.task,
        "report_file": str(
            REPORT_FILE.relative_to(BASE_DIR)
        ),
        "audit": audit,
    }


# ============================================================
# MANUAL AUDIT ENDPOINT
# ============================================================

@app.post("/audit")
def run_audit():

    try:

        return perform_security_audit()

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "agent": "code-review-agent",
        "status": "healthy",
        "source_file": str(
            SOURCE_FILE.relative_to(BASE_DIR)
        ),
        "report_file": str(
            REPORT_FILE.relative_to(BASE_DIR)
        ),
        "model": "llama3.2",
    }