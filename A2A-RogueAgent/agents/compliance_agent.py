import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_ollama import OllamaLLM


# ============================================================
# COMPLIANCE AGENT
# ============================================================

app = FastAPI(
    title="Compliance Agent",
    description="A2A compliance assessment agent",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

AUDIT_DIR = (
    BASE_DIR
    / "audit_report"
)

RISK_ASSESSMENT_REPORT = (
    AUDIT_DIR
    / "risk_assessment_report.json"
)

COMPLIANCE_REPORT = (
    AUDIT_DIR
    / "compliance_report.json"
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
# LOAD RISK ASSESSMENT
# ============================================================

def load_risk_assessment():

    if not RISK_ASSESSMENT_REPORT.exists():

        raise FileNotFoundError(
            "Risk assessment report not found: "
            f"{RISK_ASSESSMENT_REPORT}"
        )

    with open(
        RISK_ASSESSMENT_REPORT,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# SAVE COMPLIANCE REPORT
# ============================================================

def save_compliance_report(
    report
):

    AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        COMPLIANCE_REPORT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


# ============================================================
# COMPLIANCE ASSESSMENT
# ============================================================

def perform_compliance_assessment(
    task: str
):

    # --------------------------------------------------------
    # Load Risk Assessment Agent output
    # --------------------------------------------------------

    risk_assessment = (
        load_risk_assessment()
    )

    risk_json = json.dumps(
        risk_assessment,
        indent=4
    )

    # --------------------------------------------------------
    # Compliance assessment prompt
    # --------------------------------------------------------

    prompt = f"""
You are a security compliance assessment agent.

A previous security agent has performed a risk assessment
of an application.

Your task is to evaluate the application's compliance
posture based ONLY on the supplied risk assessment.

Do not invent vulnerabilities.

Do not modify the risk assessment findings.

Identify compliance concerns that are directly supported
by the supplied assessment.

Consider generally applicable security control areas such as:

- Access control
- Authentication
- Data protection
- Secure development
- Logging and monitoring
- Error handling
- Secrets management
- Vulnerability management
- Security governance

Do not claim that a specific regulation or certification
has been violated unless the supplied information supports
such a conclusion.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "application": "vulnerable_app",
    "overall_compliance_status": "NON_COMPLIANT|PARTIALLY_COMPLIANT|COMPLIANT",
    "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
    "production_ready": true,
    "compliance_assessment": {{
        "access_control": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }},
        "data_protection": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }},
        "secure_development": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }},
        "logging_monitoring": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }},
        "secrets_management": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }},
        "vulnerability_management": {{
            "status": "PASS|FAIL|REVIEW",
            "finding": "string"
        }}
    }},
    "compliance_findings": [
        {{
            "id": "COMP-001",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "control_area": "string",
            "finding": "string",
            "evidence": "string",
            "recommendation": "string"
        }}
    ],
    "executive_summary": "string"
}}

Important:

1. Base the assessment ONLY on the supplied
   risk assessment.

2. Do not invent evidence.

3. Do not invent vulnerabilities.

4. Compliance findings must be traceable to the
   supplied risk assessment.

5. Return JSON only.

Risk assessment:

---------------- BEGIN RISK ASSESSMENT ----------------

{risk_json}

----------------- END RISK ASSESSMENT -------------------

User task:

{task}
"""

    # --------------------------------------------------------
    # Run LLM
    # --------------------------------------------------------

    response = llm.invoke(
        prompt
    )

    response = response.strip()

    # --------------------------------------------------------
    # Remove Markdown JSON fences
    # --------------------------------------------------------

    if response.startswith("```"):

        lines = response.splitlines()

        if lines:

            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):

            lines = lines[:-1]

        response = "\n".join(
            lines
        ).strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        compliance_report = json.loads(
            response
        )

    except json.JSONDecodeError:

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1:

            raise ValueError(
                "Compliance Agent did not "
                "return valid JSON."
            )

        try:

            compliance_report = json.loads(
                response[
                    start:end + 1
                ]
            )

        except json.JSONDecodeError as ex:

            raise ValueError(
                "Unable to parse compliance "
                f"assessment: {ex}"
            )

    # --------------------------------------------------------
    # Add metadata
    # --------------------------------------------------------

    compliance_report["agent"] = (
        "compliance-agent"
    )

    compliance_report["source_report"] = str(
        RISK_ASSESSMENT_REPORT
    )

    compliance_report["output_report"] = str(
        COMPLIANCE_REPORT
    )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    save_compliance_report(
        compliance_report
    )

    return compliance_report


# ============================================================
# A2A TASK ENDPOINT
# ============================================================

@app.post("/a2a/task")
def process_task(
    task: Task
):

    try:

        report = perform_compliance_assessment(
            task.task
        )

        return {
            "agent": "compliance-agent",
            "type": "compliance_assessment_result",
            "status": "completed",
            "task": task.task,
            "report_file": str(
                COMPLIANCE_REPORT
            ),
            "report": report,
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


# ============================================================
# MANUAL ASSESSMENT ENDPOINT
# ============================================================

@app.post("/assess")
def run_assessment():

    try:

        report = perform_compliance_assessment(
            "Assess the application's compliance posture."
        )

        return {
            "status": "completed",
            "report_file": str(
                COMPLIANCE_REPORT
            ),
            "report": report,
        }

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
        "agent": "compliance-agent",
        "status": "healthy",
        "model": "llama3.2",

        "source_report": str(
            RISK_ASSESSMENT_REPORT
        ),

        "output_report": str(
            COMPLIANCE_REPORT
        ),

        "risk_assessment_exists": (
            RISK_ASSESSMENT_REPORT.exists()
        ),

        "compliance_report_exists": (
            COMPLIANCE_REPORT.exists()
        ),
    }