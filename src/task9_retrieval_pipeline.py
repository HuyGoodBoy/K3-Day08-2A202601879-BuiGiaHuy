"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.

Kết hợp semantic search + lexical search + reranking + PageIndex fallback
thành một pipeline thống nhất.

Logic:
    1. Chạy semantic_search + lexical_search song song
    2. Merge kết quả (RRF hoặc weighted fusion)
    3. Rerank
    4. Nếu top result score < threshold → fallback sang PageIndex
    5. Return top_k results

⚠ BẪY THƯỜNG GẶP — đọc kỹ trước khi code:
    Nếu bạn dùng điểm RRF đã fuse (Task 7) để so với score_threshold, bạn sẽ gặp bug
    thật: RRF max score luôn ≈ 1/(k+1) ≈ 0.0164 (k=60) BẤT KỂ nội dung có liên quan
    hay không. Nếu đặt threshold thấp (như 0.005) để "hợp" với thang điểm RRF, thực
    chất KHÔNG câu hỏi nào đủ thấp để trigger fallback nữa — kể cả query hoàn toàn vô
    nghĩa vẫn trả về kết quả "hybrid" (rác) thay vì fallback đúng như thiết kế.

    Cách sửa đúng: giữ điểm cosine similarity GỐC của semantic_search (trước khi qua
    RRF) làm căn cứ quyết định fallback, tách biệt khỏi điểm RRF dùng để sắp xếp kết
    quả cuối cùng. Calibrate threshold bằng cách tự đo: chạy vài câu hỏi chắc chắn
    liên quan và vài câu chắc chắn lạc đề/rác qua semantic_search, xem khoảng cách
    điểm số giữa hai nhóm rồi chọn ngưỡng nằm giữa.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


# =============================================================================
# CONFIGURATION
# =============================================================================

# Calibrate threshold này bằng cách tự đo điểm cosine của semantic_search
# cho câu hỏi liên quan vs câu hỏi lạc đề. Điểm cosine ∈ [0, 1].
# Ngưỡng 0.48 là điểm giữa: queries liên quan thường đạt 0.5-0.8,
# queries lạc đề thường 0.3-0.45.
SCORE_THRESHOLD = 0.48
DEFAULT_TOP_K = 5
RERANK_K = 60


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieval pipeline hoàn chỉnh với fallback logic.

    Pipeline:
        Query
          ├→ Semantic Search → dense_results (giữ điểm cosine gốc)
          ├→ Lexical Search  → sparse_results
          │
          ├→ Merge (RRF) → merged_results
          ├→ Rerank → reranked_results
          │
          └→ If dense_results[0]["score"] < threshold:
                └→ PageIndex Vectorless → fallback_results

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả cuối cùng
        score_threshold: Ngưỡng điểm cosine gốc tối thiểu
        use_reranking: Có áp dụng reranking hay không

    Returns:
        List of {
            'content': str,
            'score': float,     # cosine score gốc (từ semantic search)
            'metadata': dict,
            'source': str        # 'hybrid' hoặc 'pageindex'
        }
    """
    # Step 1: Song song chạy semantic + lexical
    dense_results = semantic_search(query, top_k=top_k * 2)
    sparse_results = lexical_search(query, top_k=top_k * 2)

    # Step 2: Merge bằng RRF
    ranked_lists = []
    if dense_results:
        ranked_lists.append(dense_results)
    if sparse_results:
        ranked_lists.append(sparse_results)

    if not ranked_lists:
        # Không có kết quả nào → fallback
        return pageindex_search(query, top_k=top_k)

    merged = rerank_rrf(ranked_lists, top_k=top_k * 2, k=RERANK_K)

    # Thêm source marker cho tất cả items (trước khi dedup)
    for item in merged:
        item["source"] = "hybrid"

    # Deduplication bằng content key (giữ thứ tự, bỏ trùng)
    seen = set()
    deduped = []
    for item in merged:
        key = item["content"][:100]
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    # Step 3: Rerank (optional)
    if use_reranking and deduped:
        final_results = deduped[:top_k]
    else:
        final_results = deduped[:top_k]

    # Step 4: Kiểm tra FALLBACK
    # Dùng ĐIỂM COSINE GỐC (dense_results), KHÔNG PHẢI điểm RRF
    best_cosine = dense_results[0]["score"] if dense_results else 0.0

    if best_cosine < score_threshold:
        print(f"  ⚠ Best cosine ({best_cosine:.3f}) < threshold ({score_threshold})")
        print(f"     → Triggering PageIndex fallback")
        fallback = pageindex_search(query, top_k=top_k)
        if fallback:
            return fallback

    return final_results[:top_k]


if __name__ == "__main__":
    test_queries = [
        "What is the tuition fee at RMIT Vietnam?",
        "How do I book a library study room?",
        "What scholarships are available for international students?",
        "xyzabc123nonsense query that should trigger fallback",  # Test fallback
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        try:
            results = retrieve(q, top_k=3)
            if not results:
                print("  (No results)")
            for i, r in enumerate(results, 1):
                print(f"  {i}. [{r['score']:.3f}] [{r.get('source', '?')}] {r['content'][:80]}...")
        except Exception as e:
            print(f"  ⚠ Error: {e}")
