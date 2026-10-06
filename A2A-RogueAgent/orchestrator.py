import requests


# ============================================================
# CONFIGURATION
# ============================================================

REGISTRY_URL = "http://127.0.0.1:8000"

REQUEST_TIMEOUT = 300


# ============================================================
# AGENT DISCOVERY
# ============================================================

def get_registered_agents():

    response = requests.get(
        f"{REGISTRY_URL}/agents",
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, list):

        return data

    if isinstance(data, dict):

        agents = data.get(
            "agents",
            []
        )

        if isinstance(
            agents,
            list
        ):

            return agents

    raise ValueError(
        "Unexpected response from agent registry."
    )


# ============================================================
# FIND AGENT
# ============================================================

def find_agent(
    agents,
    agent_name
):

    for agent in agents:

        if agent.get("name") == agent_name:

            return agent

    return None


# ============================================================
# INVOKE AGENT
# ============================================================

def invoke_agent(
    agent,
    task
):

    agent_name = agent.get(
        "name",
        "unknown-agent"
    )

    agent_url = agent.get(
        "url"
    )

    if not agent_url:

        return {
            "agent": agent_name,
            "status": "error",
            "error": "Agent has no URL.",
        }

    endpoint = (
        agent_url.rstrip("/")
        + "/a2a/task"
    )

    try:

        response = requests.post(
            endpoint,
            json={
                "task": task
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        try:

            result = response.json()

        except ValueError:

            result = {
                "agent": agent_name,
                "status": "completed",
                "response": response.text,
            }

        return result

    except requests.RequestException as ex:

        return {
            "agent": agent_name,
            "status": "error",
            "error": str(ex),
        }


# ============================================================
# RUN A2A PIPELINE
# ============================================================

def run_a2a_task(
    task
):

    if not task or not task.strip():

        raise ValueError(
            "A task must be provided."
        )

    # --------------------------------------------------------
    # Discover agents
    # --------------------------------------------------------

    agents = get_registered_agents()

    if not agents:

        return {
            "status": "completed",
            "message": "No agents are registered.",
            "agents": [],
            "responses": {},
        }

    # --------------------------------------------------------
    # Expected pipeline
    #
    # Code Review
    #       ↓
    # code_audit.json
    #       ↓
    # Risk Assessment
    #       ↓
    # risk_assessment_report.json
    #       ↓
    # Compliance
    #       ↓
    # compliance_report.json
    # --------------------------------------------------------

    pipeline = [
        "code-review-agent",
        "risk-assessment-agent",
        "compliance-agent",
    ]

    responses = {}

    agent_metadata = []

    # --------------------------------------------------------
    # Execute agents in pipeline order
    # --------------------------------------------------------

    for agent_name in pipeline:

        agent = find_agent(
            agents,
            agent_name
        )

        if agent is None:

            responses[agent_name] = {
                "agent": agent_name,
                "status": "error",
                "error": (
                    "Agent is not registered."
                ),
            }

            continue

        agent_metadata.append(
            {
                "name": agent_name,
                "description": agent.get(
                    "description",
                    ""
                ),
                "url": agent.get(
                    "url",
                    ""
                ),
            }
        )

        result = invoke_agent(
            agent,
            task
        )

        responses[agent_name] = result

        # ----------------------------------------------------
        # Stop the pipeline if an upstream agent failed.
        #
        # Risk Assessment depends on code_audit.json.
        # Compliance depends on risk_assessment_report.json.
        # ----------------------------------------------------

        if isinstance(
            result,
            dict
        ):

            status = result.get(
                "status"
            )

            if status == "error":

                break

    # --------------------------------------------------------
    # Detect registered agents not part of the trusted
    # pipeline.
    #
    # This is intentionally exposed for the A2A security lab.
    # --------------------------------------------------------

    pipeline_names = set(
        pipeline
    )

    unrecognized_agents = []

    for agent in agents:

        name = agent.get(
            "name",
            "unknown-agent"
        )

        if name not in pipeline_names:

            unrecognized_agents.append(
                {
                    "name": name,
                    "description": agent.get(
                        "description",
                        ""
                    ),
                    "url": agent.get(
                        "url",
                        ""
                    ),
                }
            )

    # --------------------------------------------------------
    # Return aggregated result
    # --------------------------------------------------------

    return {
        "status": "completed",

        "task": task,

        "pipeline": pipeline,

        "agent_count": len(
            agents
        ),

        "agents": agent_metadata,

        "responses": responses,

        "unrecognized_agents": (
            unrecognized_agents
        ),
    }


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    task = (
        "Perform a complete security assessment of "
        "the application. Identify security issues, "
        "assess their risk, prioritize remediation, "
        "and evaluate the application's compliance "
        "posture."
    )

    try:

        import json

        result = run_a2a_task(
            task
        )

        print(
            json.dumps(
                result,
                indent=4
            )
        )

    except Exception as ex:

        print(
            f"Orchestrator error: {ex}"
        )