import os
from pathlib import Path


SEED_DIR = Path("seed")


def read_file(filename: str) -> str:
    """
    Read a knowledge-base file.

    INTENTIONALLY VULNERABLE:
    The filename comes from the AI/tool caller and is directly
    combined with SEED_DIR.

    There is NO check that the resulting path remains inside
    SEED_DIR.

    This is intentionally vulnerable for the security lab.
    """

    file_path = os.path.join(
        str(SEED_DIR),
        filename,
    )

    print(
        "[TOOL] read_file requested:",
        filename,
    )

    print(
        "[TOOL] resolved path:",
        os.path.abspath(file_path),
    )

    if not os.path.exists(file_path):

        return (
            f"File not found: {filename}"
        )

    if not os.path.isfile(file_path):

        return (
            f"Not a file: {filename}"
        )

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:

            return f.read()

    except Exception as ex:

        return (
            "Error reading file: "
            + str(ex)
        )