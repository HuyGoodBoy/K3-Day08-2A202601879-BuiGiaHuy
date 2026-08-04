"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement — khuyến nghị vì không cần API key

Nếu dùng MMR hoặc RRF, đảm bảo hiểu và giải thích được cơ chế.

Lưu ý quan trọng về RRF (sẽ dùng lại ở Task 9): điểm RRF fused CHỈ phụ thuộc thứ hạng,
không phải độ tương đồng thật. Top-1 sau khi fuse luôn xấp xỉ 1/(k+1) ≈ 0.0164 (k=60),
bất kể nội dung đó có thật sự liên quan đến câu hỏi hay không. Đừng dùng điểm RRF để
quyết định fallback ở Task 9 — xem ghi chú ở đó.
"""

import math
from typing import Optional


def cosine_sim(a: list[float], b: list[float]) -> float:
    """Tính cosine similarity giữa 2 vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates sử dụng cross-encoder model.

    Args:
        query: Câu truy vấn
        candidates: List of {'content': str, 'score': float, 'metadata': dict}
        top_k: Số lượng kết quả sau rerank

    Returns:
        List of top_k candidates, re-scored và sorted by rerank_score descending.
    """
    # Option A: Jina Reranker API
    import os
    import requests

    api_key = os.getenv("JINA_API_KEY") or os.getenv("PAGEINDEX_API_KEY")
    if not api_key:
        print("  WARNING: JINA_API_KEY not set - skipping cross_encoder")
        return candidates[:top_k]

    try:
        response = requests.post(
            "https://api.jina.ai/v1/rerank",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "jina-reranker-v2-base-multilingual",
                "query": query,
                "documents": [c["content"] for c in candidates],
                "top_n": top_k,
            },
            timeout=30,
        )
        response.raise_for_status()
        reranked = response.json()["results"]

        results = []
        for r in reranked:
            idx = r["index"]
            results.append({
                **candidates[idx],
                "score": round(r["relevance_score"], 4),
            })
        return results[:top_k]
    except Exception as e:
        print(f"  WARNING: Cross-encoder error: {e}")
        return candidates[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.

    MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected_docs))

    Args:
        query_embedding: Vector embedding của query
        candidates: List of {'content': str, 'score': float, 'embedding': list, 'metadata': dict}
        top_k: Số lượng kết quả
        lambda_param: Trade-off giữa relevance (1.0) và diversity (0.0)

    Returns:
        List of top_k candidates selected by MMR.
    """
    if not candidates:
        return []

    # Lấy embeddings nếu có, nếu không tạo dummy
    def get_embedding(c: dict) -> list:
        return c.get("embedding", [0.0] * 768)

    selected = []
    remaining_indices = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx = None
        best_score = float("-inf")

        for i in remaining_indices:
            # Relevance to query
            relevance = cosine_sim(query_embedding, get_embedding(candidates[i]))

            # Max similarity to already selected
            max_sim_to_selected = 0.0
            for sel_idx in selected:
                sim = cosine_sim(
                    get_embedding(candidates[i]),
                    get_embedding(candidates[sel_idx])
                )
                max_sim_to_selected = max(max_sim_to_selected, sim)

            # MMR score
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        if best_idx is not None:
            selected.append(best_idx)
            remaining_indices.remove(best_idx)

    return [candidates[i] for i in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.

    RRF(d) = Σ 1 / (k + rank_r(d))

    Args:
        ranked_lists: List of ranked result lists (mỗi list từ 1 ranker)
        top_k: Số lượng kết quả cuối cùng
        k: Smoothing constant (default=60, từ paper Cormack et al. 2009)

    Returns:
        List of top_k candidates sorted by RRF score descending.
    """
<<<<<<< HEAD
<<<<<<< HEAD
    rrf_scores = {}  # content -> score
    content_map = {}  # content -> full dict

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (k + rank)
            content_map[key] = item

=======
=======
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        if not ranked_list:
            continue
        for rank, item in enumerate(ranked_list, 1):
            key = item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
            if key not in content_map:
                content_map[key] = item.copy()

    # Sort by RRF score
<<<<<<< HEAD
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
=======
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for content, score in sorted_items[:top_k]:
        item = content_map[content].copy()
<<<<<<< HEAD
<<<<<<< HEAD
        item["score"] = score
=======
        item["score"] = round(score, 4)
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
=======
        item["score"] = round(score, 4)
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
        results.append(item)

    return results


# =============================================================================
# Main rerank interface
# =============================================================================

def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",  # "cross_encoder" | "mmr" | "rrf"
    query_embedding: Optional[list[float]] = None,
) -> list[dict]:
    """
    Unified reranking interface.

    Args:
        query: Câu truy vấn
        candidates: Danh sách candidates từ retrieval
        top_k: Số lượng kết quả sau rerank
        method: Phương pháp reranking
        query_embedding: Embedding vector của query (cần cho MMR)

    Returns:
        List of top_k reranked candidates.
    """
    if not candidates:
        return []

    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
<<<<<<< HEAD
<<<<<<< HEAD
        raise NotImplementedError("Call rerank_mmr with query_embedding")
    elif method == "rrf":
        return candidates[:top_k]
=======
        if query_embedding is None:
            raise ValueError("query_embedding required for MMR reranking")
        return rerank_mmr(query_embedding, candidates, top_k)
    elif method == "rrf":
        # RRF cần nhiều ranked lists — wrap single list
        return rerank_rrf([candidates], top_k=top_k, k=60)
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
=======
        if query_embedding is None:
            raise ValueError("query_embedding required for MMR reranking")
        return rerank_mmr(query_embedding, candidates, top_k)
    elif method == "rrf":
        # RRF cần nhiều ranked lists — wrap single list
        return rerank_rrf([candidates], top_k=top_k, k=60)
>>>>>>> 30f85021b640403ca93c504135d65cc95be0bd0d
    else:
        return candidates[:top_k]


if __name__ == "__main__":
    # Test with dummy data
    dummy_candidates = [
        {"content": "Tuition fee payment schedule", "score": 0.8, "metadata": {}},
        {"content": "Scholarship eligibility requirements", "score": 0.6, "metadata": {}},
        {"content": "Library study room booking guide", "score": 0.5, "metadata": {}},
        {"content": "Course registration instructions", "score": 0.4, "metadata": {}},
        {"content": "Campus facilities overview", "score": 0.3, "metadata": {}},
    ]

    print("Test RRF Reranking")
    print("-" * 40)
    results = rerank_rrf([dummy_candidates], top_k=3)
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['score']:.3f}] {r['content']}")

    print("\nTest rerank() interface")
    results2 = rerank("scholarship", dummy_candidates, top_k=2)
    for i, r in enumerate(results2, 1):
        print(f"  {i}. [{r['score']:.3f}] {r['content']}")
