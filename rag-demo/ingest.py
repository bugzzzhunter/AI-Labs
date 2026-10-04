from pathlib import Path
import hashlib

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def read_text_file(path: Path) -> str:
    """Read a UTF-8 text file."""

    return path.read_text(
        encoding="utf-8"
    )


def calculate_file_hash(path: Path) -> str:
    """Calculate SHA-256 hash of a file."""

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:

        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_chunks(
    text: str,
    source: str,
    is_seed: bool,
    file_hash: str,
):
    """
    Convert a document into chunks.

    Metadata is deliberately retained so the security
    lab can demonstrate document provenance.
    """

    document = Document(
        page_content=text,
        metadata={
            "source": source,
            "is_seed": is_seed,
            "file_hash": file_hash,
        },
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(
        [document]
    )


def ingest_file(
    path: Path,
    vectorstore: Chroma,
    is_seed: bool = False,
) -> int:
    """
    Read, chunk and add a file to the vector database.

    Returns the number of chunks created.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if path.suffix.lower() != ".txt":

        raise ValueError(
            "Only .txt files are supported."
        )

    text = read_text_file(path)

    if not text.strip():

        raise ValueError(
            f"{path.name} is empty."
        )

    file_hash = calculate_file_hash(
        path
    )

    chunks = create_chunks(
        text=text,
        source=path.name,
        is_seed=is_seed,
        file_hash=file_hash,
    )

    ids = []

    for index, chunk in enumerate(chunks):

        chunk.metadata[
            "chunk_index"
        ] = index

        document_id = (
            f"{path.name}:"
            f"{file_hash}:"
            f"{index}"
        )

        ids.append(
            document_id
        )

    vectorstore.add_documents(
        documents=chunks,
        ids=ids,
    )

    return len(chunks)

