"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)

Cài đặt:
    pip install rank-bm25
"""

import json
from pathlib import Path
import numpy as np

<<<<<<< HEAD
# Load corpus from chroma_db metadata or data/standardized/
CORPUS: list[dict] = []
=======
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Lazy-built corpus
_corpus: list[dict] = []
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
_bm25_index = None


def _load_corpus() -> list[dict]:
    """Load all markdown files as corpus for BM25."""
    global _corpus
    if _corpus:
        return _corpus

    if not STANDARDIZED_DIR.exists():
        print(f"WARNING: Standardized directory not found: {STANDARDIZED_DIR}")
        return []

    corpus = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if len(content.strip()) < 50:
                continue
            doc_type = "legal" if "legal" in md_file.parts else "news"
            corpus.append({
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "type": doc_type,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR)),
                }
            })
        except Exception as e:
            print(f"  WARNING: Could not read {md_file.name}: {e}")

    _corpus = corpus
    return corpus


def build_bm25_index(corpus: list[dict] = None):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
<<<<<<< HEAD
    from rank_bm25 import BM25Okapi

    global _bm25_index, CORPUS
    CORPUS = corpus

    tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    _bm25_index = BM25Okapi(tokenized_corpus, k1=1.5, b=0.75)
    return _bm25_index
=======
    global _bm25_index, _corpus

    if corpus is None:
        corpus = _load_corpus()

    if not corpus:
        print("WARNING: Empty corpus - run Task 3 first")
        _bm25_index = None
        return

    from rank_bm25 import BM25Okapi

    # Simple tokenizer: lowercase + split
    tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    _bm25_index = BM25Okapi(tokenized_corpus)
    print(f"  OK: BM25 index built: {len(corpus)} documents")
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score - higher is better
            'metadata': dict
        }
        Sorted by score descending.
    """
<<<<<<< HEAD
    if _bm25_index is None or not CORPUS:
=======
    global _bm25_index, _corpus

    # Lazy load
    if _bm25_index is None:
        corpus = _load_corpus()
        build_bm25_index(corpus)

    if _bm25_index is None or not _corpus:
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
        return []

    tokenized_query = query.lower().split()
    scores = _bm25_index.get_scores(tokenized_query)

<<<<<<< HEAD
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "content": CORPUS[idx]["content"],
                "score": float(scores[idx]),
                "metadata": CORPUS[idx]["metadata"]
            })
=======
    # Get indices sorted by score descending
    indexed_scores = list(enumerate(scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in indexed_scores[:top_k]:
        if score <= 0:
            break
        results.append({
            "content": _corpus[idx]["content"],
            "score": round(float(score), 4),
            "metadata": _corpus[idx]["metadata"],
        })

>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
    return results


if __name__ == "__main__":
    print("Lexical Search (BM25) - Task 6")
    print("-" * 40)
    print("Building index...")
    build_bm25_index()

    test_queries = [
        "tuition fee payment",
        "scholarship eligibility requirements",
        "library study room booking guide",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        results = lexical_search(q, top_k=3)
        if not results:
            print("  (No results)")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.1f}] {r['content'][:80]}...")
