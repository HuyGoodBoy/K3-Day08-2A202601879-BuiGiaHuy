"""
Task 5 - Semantic search over the local vector store from Task 4.

Input:
    query string + top_k

Output:
    list of chunks with content, score and metadata, sorted by score descending.
"""

from __future__ import annotations

import math
import sys

from .task4_chunking_indexing import embed_text, load_vector_store


def configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Search chunks by cosine similarity.

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict
        }
    """
    if not query.strip() or top_k <= 0:
        return []

    store = load_vector_store()
    documents = store.get("documents", [])
    if not documents:
        return []

    query_embedding = embed_text(query)
    results: list[dict] = []

    for item in documents:
        score = cosine_similarity(query_embedding, item.get("embedding", []))
        if score <= 0:
            continue
        results.append(
            {
                "content": item["content"],
                "score": round(float(score), 4),
                "metadata": item.get("metadata", {}),
            }
        )

    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    configure_console()
    for result in semantic_search("what is the tuition fee", top_k=5):
        print(f"[{result['score']:.3f}] {result['metadata'].get('source')} - {result['content'][:100]}...")
