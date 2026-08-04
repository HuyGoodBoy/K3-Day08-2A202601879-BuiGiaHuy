"""
Task 4 - Chunking and lightweight local vector indexing.

Pipeline:
    1. Read Markdown files from data/standardized/
    2. Split documents into overlapping chunks
    3. Build deterministic hash embeddings
    4. Persist chunks + embeddings into chroma_db/vector_store.json

This lab-friendly implementation avoids heavyweight model downloads so the next
tasks can run immediately. The interface remains close to a normal RAG pipeline:
chunks contain content, metadata and embedding vectors.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
VECTOR_STORE_PATH = CHROMA_DIR / "vector_store.json"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "local-hashing-embedding"
EMBEDDING_DIM = 384

VECTOR_STORE = "json-vector-store"
COLLECTION_NAME = "university_services_docs"


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def parse_front_matter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content

    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content

    raw_meta = content[4:end].strip()
    body = content[end + len("\n---\n") :]
    metadata: dict[str, str] = {}
    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"')
        metadata[key.strip()] = value
    return metadata, body.strip()


def load_documents() -> list[dict]:
    """Read all Markdown files from data/standardized/."""
    documents: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        if len(content.strip()) < 50:
            continue

        front_meta, body = parse_front_matter(content)
        rel_path = md_file.relative_to(STANDARDIZED_DIR).as_posix()
        doc_type = "legal" if rel_path.startswith("legal/") else "news"

        metadata = {
            "source": md_file.name,
            "path": rel_path,
            "type": front_meta.get("document_type", doc_type),
            "title": front_meta.get("title", md_file.stem),
        }
        for optional_key in ("source_url", "source_file", "year", "published_year"):
            if front_meta.get(optional_key):
                metadata[optional_key] = front_meta[optional_key]

        documents.append({"content": body or content, "metadata": metadata})

    return documents


def split_text_recursive(text: str) -> list[str]:
    """Split text into chunks while preferring paragraph and line boundaries."""
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    chunks: list[str] = []
    start = 0

    while start < len(text):
        hard_end = min(start + CHUNK_SIZE, len(text))
        window = text[start:hard_end]

        if hard_end < len(text):
            candidates = [window.rfind("\n\n"), window.rfind("\n"), window.rfind(". ")]
            cut = max(candidates)
            if cut >= int(CHUNK_SIZE * 0.5):
                hard_end = start + cut + (2 if window[cut : cut + 2] == ". " else 0)

        chunk = text[start:hard_end].strip()
        if chunk:
            chunks.append(chunk)

        if hard_end >= len(text):
            break
        start = max(0, hard_end - CHUNK_OVERLAP)

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Create overlapping text chunks from documents."""
    chunks: list[dict] = []
    for doc in documents:
        splits = split_text_recursive(doc["content"])
        for chunk_index, chunk_text in enumerate(splits):
            chunk_id = f"{doc['metadata']['path']}::chunk-{chunk_index:04d}"
            chunks.append(
                {
                    "id": chunk_id,
                    "content": chunk_text,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_index": chunk_index,
                        "chunk_id": chunk_id,
                    },
                }
            )
    return chunks


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def embed_text(text: str) -> list[float]:
    """Hashing embedding: cheap, deterministic and dependency-free."""
    vector = [0.0] * EMBEDDING_DIM
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "little") % EMBEDDING_DIM
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Add local embedding vectors to each chunk."""
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["content"])
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Persist chunks to a small local JSON vector store."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dim": EMBEDDING_DIM,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "documents": chunks,
    }
    VECTOR_STORE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_vector_store() -> dict:
    if not VECTOR_STORE_PATH.exists():
        run_pipeline()
    return json.loads(VECTOR_STORE_PATH.read_text(encoding="utf-8"))


def run_pipeline() -> list[dict]:
    """Run load -> chunk -> embed -> index."""
    configure_console()
    print("=" * 50)
    print("Task 4: Chunking and Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} size={CHUNK_SIZE} overlap={CHUNK_OVERLAP}")
    print(f"  Embedding: {EMBEDDING_MODEL} dim={EMBEDDING_DIM}")
    print(f"  Vector store: {VECTOR_STORE_PATH}")
    print("=" * 50)

    docs = load_documents()
    print(f"Loaded documents: {len(docs)}")

    chunks = chunk_documents(docs)
    print(f"Created chunks: {len(chunks)}")

    chunks = embed_chunks(chunks)
    print(f"Embedded chunks: {len(chunks)}")

    index_to_vectorstore(chunks)
    print("Indexed to local vector store")
    return chunks


if __name__ == "__main__":
    run_pipeline()
