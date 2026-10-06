import requests


REGISTRY_URL = "http://127.0.0.1:8000"


AGENTS = [
    {
        "name": "code-review-agent",
        "description": (
            "Reviews application source code for "
            "security issues"
        ),
        "url": "http://127.0.0.1:8001",
    },
    {
        "name": "risk-assessment-agent",
        "description": (
            "Performs application risk assessment"
        ),
        "url": "http://127.0.0.1:8002",
    },
    {
        "name": "compliance-agent",
        "description": (
            "Reviews compliance requirements"
        ),
        "url": "http://127.0.0.1:8003",
    },
]


def register_agent(agent):

    response = requests.post(
        f"{REGISTRY_URL}/agents/register",
        json=agent,
        timeout=5,
    )

    response.raise_for_status()

    result = response.json()

    print(
        f"[+] Registered: {agent['name']}"
    )

    return result


def main():

    print("Registering legitimate A2A agents...")
    print()

    for agent in AGENTS:

        try:

            register_agent(agent)

        except requests.RequestException as ex:

            print(
                f"[-] Failed to register "
                f"{agent['name']}: {ex}"
            )

    print()
    print("Current registry:")

    try:

        response = requests.get(
            f"{REGISTRY_URL}/agents",
            timeout=5,
        )

        response.raise_for_status()

        agents = response.json().get(
            "agents",
            [],
        )

        for agent in agents:

            print(
                f"  - {agent['name']} "
                f"({agent['url']})"
            )

    except requests.RequestException as ex:

        print(
            f"[-] Could not retrieve registry: {ex}"
        )


if __name__ == "__main__":
    main()