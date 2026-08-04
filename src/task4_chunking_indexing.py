"""
Task 4 — Chunking & Indexing vao Vector Store.

Dung OpenAI text-embedding-3-small (1536 dim) - nhanh, API-based.
Khong can tai model locally.

Luu y: Neu thay doi data/standardized/, phai xoa chroma_db/ cu truoc khi re-index.
"""

import shutil
import os
from pathlib import Path

# === Load .env ===
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# === CONFIG ===
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
COLLECTION_NAME = "university_services_docs"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# =============================================================================
# OpenAI Embedding
# =============================================================================

def get_openai_embedding(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Lay embedding qua OpenAI API."""
    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY not set. Please add to .env file:\n"
            "  OPENAI_API_KEY=sk-proj-...\n"
            "Get key at: https://platform.openai.com/api-keys"
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        for item in response.data:
            embeddings.append(item.embedding)

    return embeddings


# =============================================================================
# Pipeline
# =============================================================================

def load_documents() -> list[dict]:
    """Doc toan bo markdown files."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        print(f"[WARN] Directory not found: {STANDARDIZED_DIR}")
        return documents

    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if len(content.strip()) < 50:
                continue
            doc_type = "legal" if "legal" in md_file.parts else "news"
            documents.append({
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "type": doc_type,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR)),
                }
            })
        except Exception as e:
            print(f"  [WARN] Error reading {md_file.name}: {e}")

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk documents bang RecursiveCharacterTextSplitter."""
    if not documents:
        return []

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    for doc in documents:
        try:
            splits = splitter.split_text(doc["content"])
            for i, chunk_text in enumerate(splits):
                if len(chunk_text.strip()) < 50:
                    continue
                chunks.append({
                    "content": chunk_text,
                    "metadata": {**doc["metadata"], "chunk_index": i}
                })
        except Exception as e:
            print(f"  [WARN] Error chunking {doc['metadata']['source']}: {e}")

    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Embed chunks qua OpenAI API."""
    if not chunks:
        return chunks

    print(f"  Embedding {len(chunks)} chunks via OpenAI {EMBEDDING_MODEL}...")
    texts = [c["content"] for c in chunks]
    embeddings = get_openai_embedding(texts)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb
    print(f"  [OK] Embedding complete ({len(embeddings)} vectors, dim={EMBEDDING_DIM})")
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """Luu chunks vao ChromaDB."""
    if not chunks:
        print("  [WARN] No chunks to index")
        return

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        print(f"  [OK] Removed old chroma_db")

    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [
        f"{c['metadata']['source']}_chunk_{c['metadata']['chunk_index']}"
        for c in chunks
    ]
    texts = [c["content"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    metadatas = [
        {k: v for k, v in c["metadata"].items() if k != "embedding"}
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"  [OK] Indexed {len(chunks)} chunks to ChromaDB")


def run_pipeline():
    """Chay load -> chunk -> embed -> index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: ChromaDB")
    print("=" * 50)

    docs = load_documents()
    if not docs:
        print("\n[WARN] No documents. Run Task 1->3 first.")
        return
    print(f"\n[OK] Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    if not chunks:
        print("\n[WARN] No chunks created.")
        return
    print(f"[OK] Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    index_to_vectorstore(chunks)
    print("[OK] Done!")


if __name__ == "__main__":
    run_pipeline()
