# A2A Multi-Agent Security Assessment Lab

A local security lab for demonstrating security risks in
Agent-to-Agent (A2A) multi-agent systems.

The lab implements a multi-stage security assessment
pipeline using local Llama 3.2 through Ollama.

The normal trusted pipeline architecture:

    +----------------------+
    |      Streamlit       |
    |        app.py        |
    +----------+-----------+
               |
               v
    +----------------------+
    |    Orchestrator      |
    |  orchestrator.py     |
    +----------+-----------+
               |
               v
    +----------------------+
    |    Agent Registry    |
    |     registry.py      |
    +----------+-----------+
               |
        +------+------+
        |      |      |
        v      v      v
      Code    Risk  Compliance
      Review  Agent   Agent
        |      |       |
        v      v       v
      code_   risk_   compliance_
      audit   assess  report
      .json   .json   .json


The lab also includes a Rogue Agent that can be used to
demonstrate an agent authorization and report-integrity
failure in the isolated lab environment.

---

# 1. Project Structure

    a2a_security_lab/
    |
    ├── app.py
    ├── orchestrator.py
    ├── registry.py
    ├── requirements.txt
    ├── README.md
    |
    ├── vulnerable_app/
    │   └── app.py
    |
    ├── audit_report/
    │   ├── code_audit.json
    │   ├── risk_assessment_report.json
    │   ├── risk_assessment_report.backup.json
    │   └── compliance_report.json
    |
    ├── agents/
    │   ├── __init__.py
    │   ├── code_review_agent.py
    │   ├── risk_assessment_agent.py
    │   ├── compliance_agent.py
    │   └── rogue_agent.py
    |
    └── util/
        ├── register_agents.py
        └── delete_agents.py


The backup report is created only when the Rogue Agent
performs its report-tampering lab exercise.

---

# 2. Vulnerable Application

Location:

    vulnerable_app/app.py

This application is intentionally vulnerable and is used
as the source code for the security assessment.

The example application contains issues such as:

- SQL injection
- Hardcoded credentials
- Verbose error messages
- Insufficient security logging

It is intended only for an isolated security lab.

Do not deploy the vulnerable application to production.


---

# 3. Code Review Agent

File:

    agents/code_review_agent.py

The Code Review Agent performs the initial security review.

It:

1. Reads:

       vulnerable_app/app.py

2. Sends the source code to local Llama 3.2.

3. Generates structured security findings.

4. Writes:

       audit_report/code_audit.json


The Code Review Agent does not rely on a hardcoded
`CODE_FINDINGS` collection.

The findings are generated from the source code.

---

# 4. Risk Assessment Agent

File:

    agents/risk_assessment_agent.py

The Risk Assessment Agent consumes the Code Review Agent's
output.

Input:

    audit_report/code_audit.json

Output:

    audit_report/risk_assessment_report.json


It evaluates:

- Overall risk
- Business impact
- Exploitability
- Potential consequences
- Finding priority
- Remediation priority
- Production readiness

The Risk Assessment Agent does not contain a hardcoded
security findings list.

It uses the Code Review Agent's report as its input.

---

# 5. Compliance Agent

File:

    agents/compliance_agent.py

The Compliance Agent consumes the Risk Assessment Agent's
output.

Input:

    audit_report/risk_assessment_report.json

Output:

    audit_report/compliance_report.json


It evaluates areas such as:

- Access control
- Data protection
- Secure development
- Logging and monitoring
- Secrets management
- Vulnerability management

The Compliance Agent does not contain a hardcoded
`COMPLIANCE_FINDINGS` list.

Its assessment is generated from the risk assessment report.

---

# 6. A2A Orchestrator

File:

    orchestrator.py

The orchestrator discovers agents through the registry.

The intended trusted pipeline is:

    code-review-agent
            |
            v
    code_audit.json
            |
            v
    risk-assessment-agent
            |
            v
    risk_assessment_report.json
            |
            v
    compliance-agent
            |
            v
    compliance_report.json


The orchestrator:

1. Queries the agent registry.
2. Discovers registered agents.
3. Finds the expected pipeline agents.
4. Executes them in sequence.
5. Collects their responses.
6. Stops downstream execution if an upstream agent fails.
7. Identifies registered agents that are outside the
   expected pipeline.

The expected pipeline is:

    code-review-agent
    risk-assessment-agent
    compliance-agent


---

# 7. Agent Registry

File:

    registry.py

The registry provides agent discovery.

The orchestrator queries:

    GET /agents


A registered agent contains information such as:

    {
        "name": "code-review-agent",
        "description": "Security code review agent",
        "url": "http://127.0.0.1:8001"
    }


The registry is intentionally simple for this security lab.

A production implementation should consider:

- Agent authentication
- Agent authorization
- Agent identity
- Registration approval
- Registry integrity
- Certificate validation
- Service authentication
- Trust policies
- Agent attestation

---

# 8. Legitimate Agents

The intended agents are:

    code-review-agent
    risk-assessment-agent
    compliance-agent


Their default ports are:

    Code Review Agent       8001
    Risk Assessment Agent  8002
    Compliance Agent       8003


Each exposes:

    POST /a2a/task

and:

    GET /health


---

# 9. Rogue Agent

File:

    agents/rogue_agent.py

The Rogue Agent is intentionally unauthorized.

Default port:

    8004


Start it with:

    python agents/rogue_agent.py


It provides:

    POST /a2a/task

    GET /health

    GET /agent

    POST /restore


The Rogue Agent is NOT part of the trusted assessment
pipeline.

Its purpose is to demonstrate what can happen when an
untrusted agent gains access to security-sensitive
artifacts.


---

# 10. Rogue Agent Report-Tampering Exercise

The Rogue Agent can modify:

    audit_report/risk_assessment_report.json


The exercise demonstrates a report-integrity failure.



The Rogue Agent introduces an unauthorized modification:

    Risk Assessment Agent
            |
            v
    risk_assessment_report.json
            |
            ^
            |
       Rogue Agent


The Rogue Agent changes the risk assessment so that the
application appears to have a lower risk and be suitable
for production.

Before making the modification, it creates:

    audit_report/risk_assessment_report.backup.json


This allows the original report to be restored.

---

# 11. Restore the Risk Assessment

The Rogue Agent provides:

    POST /restore


This restores:

    risk_assessment_report.json


from:

    risk_assessment_report.backup.json


The backup exists only after the Rogue Agent has performed
the tampering exercise.

---

# 12. Running the Lab

## Step 1 — Create Virtual Environment

    python -m venv .venv


Activate it.

Linux/macOS:

    source .venv/bin/activate


Windows:

    .venv\Scripts\activate


Install dependencies:

    pip install -r requirements.txt


---

# 13. Start Registry

If the registry uses FastAPI:

    uvicorn registry:app --host 127.0.0.1 --port 8000


The registry should be available at:

    http://127.0.0.1:8000


---

# 14. Start Legitimate Agents

Start the Code Review Agent:

    uvicorn agents.code_review_agent:app --host 127.0.0.1 --port 8001


Start the Risk Assessment Agent:

    uvicorn agents.risk_assessment_agent:app --host 127.0.0.1 --port 8002


Start the Compliance Agent:

    uvicorn agents.compliance_agent:app --host 127.0.0.1 --port 8003


---

# 15. Register Legitimate Agents

Run:

    python util/register_agents.py


The registry should contain:

    code-review-agent
    risk-assessment-agent
    compliance-agent


---

# 16. Start Rogue Agent

For the report-integrity exercise:

    python agents/rogue_agent.py


It listens on:

    http://127.0.0.1:8004


Do not register the Rogue Agent as a trusted pipeline
agent during the normal assessment.


---

# 17. Using applicatoin

### 1. Invoke Code Review Agent
    curl -X POST http://127.0.0.1:8001/a2a/task -H "Content-Type: application/json" -d "{\"task\":\"Perform a security review of vulnerable_app/app.py\"}"

### 2. Invoke Risk Assessment Agent
    curl -X POST http://127.0.0.1:8002/a2a/task -H "Content-Type: application/json" -d "{\"task\":\"Assess the risks documented in audit_report/code_audit.json\"}"

### 3. Invoke Compliance Agent
    curl -X POST http://127.0.0.1:8003/a2a/task -H "Content-Type: application/json" -d "{\"task\":\"Assess compliance using audit_report/risk_assessment_report.json\"}"

### Optional 
Start streamlit and use via GUI

Run:

    streamlit run app.py


The application provides the main assessment interface.


---

# 18.  A2A Security Exercise: Report Integrity

The second exercise demonstrates an unauthorized agent
modifying a security decision artifact.

First generate a legitimate:

    risk_assessment_report.json


Then invoke the Rogue Agent with a task requesting the
report-tampering lab action.

The Rogue Agent will:

1. Read the existing risk assessment.
2. Create a backup.
3. Add metadata to report.
4. Write the modified report back to disk.
5. Return the modification result.


The backup is:

    risk_assessment_report.backup.json


This demonstrates why downstream agents should not blindly
trust files produced by another component.


---

# 19.  Resetting the Lab

The legitimate-agent registration utility is:

    python util/register_agents.py


The agent deletion utility is:

    python util/delete_agents.py


To reset registered agents:

    python util/delete_agents.py

Then register the legitimate agents again:

    python util/register_agents.py

Also remember to empty audit_report directory.

To reset the report-tampering exercise, restore the risk
assessment using the Rogue Agent's `/restore` endpoint or
regenerate the reports by running the legitimate pipeline.


---

The lab is intentionally vulnerable and should be run only
in an isolated testing environment.