import requests


REGISTRY_URL = "http://127.0.0.1:8000"


def delete_all_agents():
    try:
        response = requests.delete(
            f"{REGISTRY_URL}/agents",
            timeout=5,
        )

        response.raise_for_status()

        print("[+] All registered agents deleted.")

        try:
            print(response.json())
        except ValueError:
            pass

    except requests.RequestException as ex:
        print(f"[-] Failed to delete agents: {ex}")


def main():
    print("Deleting all registered A2A agents...")
    delete_all_agents()


if __name__ == "__main__":
    main()