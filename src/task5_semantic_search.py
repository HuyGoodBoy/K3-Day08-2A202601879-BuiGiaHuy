"""
Task 5 — Semantic Search Module.

Tim kiem ngwu ngh~ia (dense retrieval) tren ChromaDB.
Dung OpenAI text-embedding-3-small API.

Yeu cau:
    - Input: query string + top_k
    - Output: danh sach chunks co score, sorted descending
    - Tuong thich voi embedding model va vector store o Task 4
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import chromadb
from openai import OpenAI

# Constants phai khop voi Task 4
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "university_services_docs"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Lazy-loaded instances
_client = None
_collection = None


def _get_client():
    """Lazy load OpenAI client."""
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set in .env")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def _get_collection():
    """Lazy load ChromaDB collection."""
    global _collection
    if _collection is None:
        if not CHROMA_DIR.exists():
            raise RuntimeError(
                f"ChromaDB not found at {CHROMA_DIR}. "
                "Run Task 4 first: python -m src.task4_chunking_indexing"
            )
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(name=COLLECTION_NAME)
    return _collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tim kiem ngwu ngh~ia su dung vector similarity.

    Args:
        query: Cau truy van
        top_k: So luong ket qua toi da

    Returns:
        List of {
            'content': str,
            'score': float,     # Cosine similarity [0, 1], cao hon = tot hon
            'metadata': dict    # source, type, chunk_index
        }
        Sorted by score descending.
    """
    try:
        collection = _get_collection()
    except RuntimeError:
        return []

    client = _get_client()
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        query_vector = response.data[0].embedding
    except Exception as e:
        print(f"  [FAIL] OpenAI embedding error: {e}")
        return []

    try:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        print(f"  [FAIL] ChromaDB query error: {e}")
        return []

    output = []
    if not results or not results.get("documents") or not results["documents"][0]:
        return output

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        score = max(0.0, 1.0 - dist)
        output.append({
            "content": doc,
            "score": round(score, 4),
            "metadata": meta or {},
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    print("Semantic Search — Task 5")
    print("-" * 40)
    test_queries = [
        "What is the tuition fee?",
        "Scholarship eligibility requirements",
        "Library study room booking",
        "How to register for courses?",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        results = semantic_search(q, top_k=3)
        if not results:
            print("  (No results — run Task 4 first)")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.3f}] {r['content'][:80]}...")
