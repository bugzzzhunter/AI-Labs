import json
from pathlib import Path
import shutil
import streamlit as st

from orchestrator import run_a2a_task


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

VULNERABLE_APP = (
    BASE_DIR
    / "vulnerable_app"
    / "app.py"
)

AUDIT_DIR = (
    BASE_DIR
    / "audit_report"
)

CODE_AUDIT_REPORT = (
    AUDIT_DIR
    / "code_audit.json"
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
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="A2A Security Assessment Lab",
    page_icon="🔐",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🔐 A2A Multi-Agent Security Assessment Lab"
)

st.caption(
    "Multi-agent security assessment using local Llama 3.2"
)

st.info(
    """
This lab demonstrates a multi-agent security assessment
pipeline.

The agents process the application sequentially:

Code Review Agent
        ->
code_audit.json
        ->
Risk Assessment Agent
        ->
risk_assessment_report.json
        ->
Compliance Agent
        ->
compliance_report.json
"""
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clear_audit_reports():
    """
    Remove all generated reports from audit_report/.

    The audit_report directory itself is preserved.
    """

    removed = 0

    AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for item in AUDIT_DIR.iterdir():

        try:

            if item.is_dir():

                shutil.rmtree(item)

            else:

                item.unlink()

            removed += 1

        except Exception as error:

            st.error(
                f"Could not remove {item.name}: {error}"
            )

    return removed

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "Lab Controls"
    )

    st.markdown(
        """
### Agents

- Code Review Agent
- Risk Assessment Agent
- Compliance Agent

### Pipeline

1. Analyze source code
2. Assess security risk
3. Assess compliance posture

All agents use local Llama 3.2.
"""
    )

    st.header("Clear existing reports")

    st.write(
        "Use the button below to remove all generated "
        "reports from the audit_report directory."
    )

    if st.button(
        "🗑️ Clear Audit Reports",
        type="secondary",
        use_container_width=True
    ):

        removed = clear_audit_reports()

        if removed > 0:

            st.success(
                f"Removed {removed} audit report(s)."
            )

        else:

            st.info(
                "audit_report is already empty."
            )

        st.rerun()

    st.divider()

    st.subheader(
        "Assessment Task"
    )

    task = st.text_area(
        "Task sent to agents",
        value=(
            "Perform a complete security assessment of "
            "the application. Identify security issues, "
            "assess their risk, prioritize remediation, "
            "and evaluate the application's compliance "
            "posture."
        ),
        height=180,
    )


# ============================================================
# APPLICATION UNDER REVIEW
# ============================================================

st.subheader(
    "📂 Application Under Review"
)

if VULNERABLE_APP.exists():

    st.success(
        "Vulnerable application found."
    )

    st.code(
        str(
            VULNERABLE_APP.relative_to(
                BASE_DIR
            )
        ),
        language="text",
    )

else:

    st.error(
        f"Application not found: {VULNERABLE_APP}"
    )


# ============================================================
# SOURCE CODE
# ============================================================

with st.expander(
    "View Application Source"
):

    if VULNERABLE_APP.exists():

        try:

            source_code = (
                VULNERABLE_APP.read_text(
                    encoding="utf-8"
                )
            )

            st.code(
                source_code,
                language="python",
            )

        except Exception as ex:

            st.error(
                f"Unable to read source: {ex}"
            )

    else:

        st.warning(
            "vulnerable_app/app.py was not found."
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_json_report(
    report_path
):

    if not report_path.exists():

        return None

    try:

        with open(
            report_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except json.JSONDecodeError:

        return {
            "_error": (
                "Report exists but contains "
                "invalid JSON."
            )
        }

    except Exception as ex:

        return {
            "_error": str(ex)
        }


def display_code_audit(
    report
):

    if not report:

        st.warning(
            "Code audit report has not been generated."
        )

        return

    if "_error" in report:

        st.error(
            report["_error"]
        )

        return

    st.subheader(
        "🔍 Code Review Results"
    )

    summary = report.get(
        "summary",
        {}
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Critical",
            summary.get(
                "critical",
                0
            )
        )

    with col2:

        st.metric(
            "High",
            summary.get(
                "high",
                0
            )
        )

    with col3:

        st.metric(
            "Medium",
            summary.get(
                "medium",
                0
            )
        )

    with col4:

        st.metric(
            "Low",
            summary.get(
                "low",
                0
            )
        )

    with col5:

        st.metric(
            "Total",
            summary.get(
                "total",
                0
            )
        )

    findings = report.get(
        "findings",
        []
    )

    for finding in findings:

        finding_id = finding.get(
            "id",
            "N/A"
        )

        severity = finding.get(
            "severity",
            "UNKNOWN"
        )

        issue = finding.get(
            "issue",
            "Unknown"
        )

        with st.expander(
            f"{finding_id} | {severity} | {issue}"
        ):

            st.write(
                "**Category:**",
                finding.get(
                    "category",
                    ""
                )
            )

            st.write(
                "**Description:**",
                finding.get(
                    "description",
                    ""
                )
            )

            st.write(
                "**Evidence:**",
                finding.get(
                    "evidence",
                    ""
                )
            )

            st.write(
                "**Recommendation:**",
                finding.get(
                    "recommendation",
                    ""
                )
            )

            st.write(
                "**Location:**",
                finding.get(
                    "line_reference",
                    ""
                )
            )


def display_risk_assessment(
    report
):

    if not report:

        st.warning(
            "Risk assessment report has not been generated."
        )

        return

    if "_error" in report:

        st.error(
            report["_error"]
        )

        return

    st.subheader(
        "⚠️ Risk Assessment"
    )

    overall_risk = report.get(
        "overall_risk",
        "UNKNOWN"
    )

    production_ready = report.get(
        "production_ready",
        False
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Overall Risk",
            overall_risk
        )

    with col2:

        if production_ready:

            st.success(
                "Production Ready"
            )

        else:

            st.error(
                "Not Production Ready"
            )

    risk_assessment = report.get(
        "risk_assessment",
        {}
    )

    st.write(
        "**Business Impact:**",
        risk_assessment.get(
            "business_impact",
            ""
        )
    )

    st.write(
        "**Exploitability:**",
        risk_assessment.get(
            "exploitability",
            ""
        )
    )

    st.write(
        "**Potential Consequences:**",
        risk_assessment.get(
            "potential_consequences",
            ""
        )
    )

    st.write(
        "**Priority:**",
        risk_assessment.get(
            "priority",
            ""
        )
    )

    st.write(
        "**Executive Summary:**",
        report.get(
            "executive_summary",
            ""
        )
    )

    prioritized = report.get(
        "prioritized_findings",
        []
    )

    if prioritized:

        st.write(
            "### Prioritized Findings"
        )

        for finding in prioritized:

            with st.expander(
                f"Priority {finding.get('priority', '')} | "
                f"{finding.get('id', '')}"
            ):

                st.write(
                    "**Severity:**",
                    finding.get(
                        "severity",
                        ""
                    )
                )

                st.write(
                    "**Reason:**",
                    finding.get(
                        "reason",
                        ""
                    )
                )

                st.write(
                    "**Recommended Action:**",
                    finding.get(
                        "recommended_action",
                        ""
                    )
                )


def display_compliance_report(
    report
):

    if not report:

        st.warning(
            "Compliance report has not been generated."
        )

        return

    if "_error" in report:

        st.error(
            report["_error"]
        )

        return

    st.subheader(
        "📋 Compliance Assessment"
    )

    status = report.get(
        "overall_compliance_status",
        "UNKNOWN"
    )

    risk_level = report.get(
        "risk_level",
        "UNKNOWN"
    )

    production_ready = report.get(
        "production_ready",
        False
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "Compliance Status",
            status
        )

    with col2:

        st.metric(
            "Risk Level",
            risk_level
        )

    with col3:

        if production_ready:

            st.success(
                "Production Ready"
            )

        else:

            st.error(
                "Not Production Ready"
            )

    assessment = report.get(
        "compliance_assessment",
        {}
    )

    for control_area, details in assessment.items():

        if not isinstance(
            details,
            dict
        ):

            continue

        control_name = (
            control_area
            .replace(
                "_",
                " "
            )
            .title()
        )

        status_value = details.get(
            "status",
            "UNKNOWN"
        )

        with st.expander(
            f"{control_name} | {status_value}"
        ):

            st.write(
                details.get(
                    "finding",
                    ""
                )
            )

    findings = report.get(
        "compliance_findings",
        []
    )

    if findings:

        st.write(
            "### Compliance Findings"
        )

        for finding in findings:

            finding_id = finding.get(
                "id",
                "N/A"
            )

            severity = finding.get(
                "severity",
                "UNKNOWN"
            )

            with st.expander(
                f"{finding_id} | {severity}"
            ):

                st.write(
                    "**Control Area:**",
                    finding.get(
                        "control_area",
                        ""
                    )
                )

                st.write(
                    "**Finding:**",
                    finding.get(
                        "finding",
                        ""
                    )
                )

                st.write(
                    "**Evidence:**",
                    finding.get(
                        "evidence",
                        ""
                    )
                )

                st.write(
                    "**Recommendation:**",
                    finding.get(
                        "recommendation",
                        ""
                    )
                )

    st.write(
        "**Executive Summary:**",
        report.get(
            "executive_summary",
            ""
        )
    )


# ============================================================
# RUN PIPELINE
# ============================================================

st.subheader(
    "🚀 Run Multi-Agent Assessment"
)

if st.button(
    "Run Complete Assessment",
    type="primary",
    use_container_width=True,
):

    if not task.strip():

        st.warning(
            "Please provide an assessment task."
        )

    elif not VULNERABLE_APP.exists():

        st.error(
            "vulnerable_app/app.py does not exist."
        )

    else:

        with st.spinner(
            "Running multi-agent security assessment..."
        ):

            try:

                result = run_a2a_task(
                    task
                )

                st.success(
                    "Multi-agent assessment completed."
                )

                # ====================================================
                # AGENT RESPONSES
                # ====================================================

                with st.expander(
                    "🤖 A2A Agent Responses",
                    expanded=False
                ):

                    if isinstance(
                        result,
                        dict
                    ):

                        responses = result.get(
                            "responses",
                            result
                        )

                        if isinstance(
                            responses,
                            dict
                        ):

                            for (
                                agent_name,
                                response
                            ) in responses.items():

                                st.write(
                                    f"### {agent_name}"
                                )

                                if isinstance(
                                    response,
                                    dict
                                ):

                                    st.json(
                                        response
                                    )

                                else:

                                    st.write(
                                        response
                                    )

                        else:

                            st.json(
                                result
                            )

                    else:

                        st.write(
                            result
                        )

            except Exception as ex:

                st.error(
                    f"A2A assessment failed: {ex}"
                )


# ============================================================
# REPORTS
# ============================================================

st.divider()

st.header(
    "📊 Assessment Reports"
)


# ============================================================
# PIPELINE STATUS
# ============================================================

code_exists = (
    CODE_AUDIT_REPORT.exists()
)

risk_exists = (
    RISK_ASSESSMENT_REPORT.exists()
)

compliance_exists = (
    COMPLIANCE_REPORT.exists()
)

col1, col2, col3 = (
    st.columns(3)
)

with col1:

    if code_exists:

        st.success(
            "✅ Code Audit"
        )

    else:

        st.warning(
            "⏳ Code Audit"
        )

with col2:

    if risk_exists:

        st.success(
            "✅ Risk Assessment"
        )

    else:

        st.warning(
            "⏳ Risk Assessment"
        )

with col3:

    if compliance_exists:

        st.success(
            "✅ Compliance"
        )

    else:

        st.warning(
            "⏳ Compliance"
        )


# ============================================================
# LOAD REPORTS
# ============================================================

code_audit = load_json_report(
    CODE_AUDIT_REPORT
)

risk_assessment = load_json_report(
    RISK_ASSESSMENT_REPORT
)

compliance = load_json_report(
    COMPLIANCE_REPORT
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔍 Code Review",
        "⚠️ Risk Assessment",
        "📋 Compliance",
        "📄 Raw Reports",
    ]
)


with tab1:

    display_code_audit(
        code_audit
    )


with tab2:

    display_risk_assessment(
        risk_assessment
    )


with tab3:

    display_compliance_report(
        compliance
    )


with tab4:

    st.subheader(
        "Generated Report Files"
    )

    st.write(
        "Code Audit:"
    )

    st.code(
        str(CODE_AUDIT_REPORT)
    )

    st.write(
        "Risk Assessment:"
    )

    st.code(
        str(RISK_ASSESSMENT_REPORT)
    )

    st.write(
        "Compliance:"
    )

    st.code(
        str(COMPLIANCE_REPORT)
    )

    if code_audit:

        st.subheader(
            "code_audit.json"
        )

        st.json(
            code_audit
        )

    if risk_assessment:

        st.subheader(
            "risk_assessment_report.json"
        )

        st.json(
            risk_assessment
        )

    if compliance:

        st.subheader(
            "compliance_report.json"
        )

        st.json(
            compliance
        )


# ============================================================
# LAB INFORMATION
# ============================================================

st.divider()

with st.expander(
    "ℹ️ About This Lab"
):

    st.markdown(
        """
### Multi-Agent Security Pipeline

The lab contains three sequential security agents.

#### 1. Code Review Agent

Reads:

    vulnerable_app/app.py

Produces:

    audit_report/code_audit.json

#### 2. Risk Assessment Agent

Reads:

    audit_report/code_audit.json

Produces:

    audit_report/risk_assessment_report.json

#### 3. Compliance Agent

Reads:

    audit_report/risk_assessment_report.json

Produces:

    audit_report/compliance_report.json

### Trust Boundaries

Each agent consumes an artifact generated by another agent.

Therefore the workflow demonstrates multiple trust boundaries:

    Source Code
        ↓
    Code Review Agent
        ↓
    code_audit.json
        ↓
    Risk Assessment Agent
        ↓
    risk_assessment_report.json
        ↓
    Compliance Agent
        ↓
    compliance_report.json

The reports should be treated as agent-generated data rather
than inherently trusted security decisions.
"""
    )