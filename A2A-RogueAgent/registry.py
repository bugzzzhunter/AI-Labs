from fastapi import FastAPI
from pydantic import BaseModel


# ============================================================
# A2A AGENT REGISTRY
# ============================================================
#
# This registry is intentionally vulnerable for the lab.
#
# Security weaknesses demonstrated:
#
# 1. No authentication
# 2. No agent identity verification
# 3. No registration approval
# 4. No authorization checks
# 5. No capability validation
# 6. No endpoint verification
#
# Therefore:
#
#     Registration == Participation
#
# This is the vulnerability the learner is expected to
# discover and exploit in the lab environment.
# ============================================================


app = FastAPI(
    title="A2A Agent Registry",
    description="Intentionally vulnerable A2A agent registry",
)


# ============================================================
# DATA MODEL
# ============================================================

class AgentRegistration(BaseModel):

    name: str

    description: str

    url: str


# ============================================================
# IN-MEMORY REGISTRY
# ============================================================
#
# Example:
#
# [
#     {
#         "name": "code-review-agent",
#         "description": "Reviews application source code",
#         "url": "http://127.0.0.1:8001"
#     }
# ]
#
# ============================================================

agents = []


# ============================================================
# LIST REGISTERED AGENTS
# ============================================================

@app.get("/agents")
def list_agents():

    return {
        "agents": agents
    }


# ============================================================
# REGISTER AGENT
# ============================================================

@app.post("/agents/register")
def register_agent(
    registration: AgentRegistration,
):

    agent = {
        "name": registration.name,
        "description": registration.description,
        "url": registration.url,
    }

    agents.append(agent)

    return {
        "status": "registered",
        "message": (
            "Agent registered successfully."
        ),
        "agent": agent,
    }


# ============================================================
# REMOVE AGENT
# ============================================================

@app.delete("/agents/{agent_name}")
def remove_agent(
    agent_name: str,
):

    global agents

    original_count = len(agents)

    agents = [
        agent
        for agent in agents
        if agent["name"] != agent_name
    ]

    if len(agents) == original_count:

        return {
            "status": "not_found",
            "message": (
                f"Agent '{agent_name}' was not found."
            ),
        }

    return {
        "status": "removed",
        "message": (
            f"Agent '{agent_name}' removed."
        ),
    }


# ============================================================
# RESET REGISTRY
# ============================================================

@app.delete("/agents")
def reset_registry():

    global agents

    count = len(agents)

    agents = []

    return {
        "status": "reset",
        "removed_agents": count,
    }