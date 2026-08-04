# PROMPT CHO THÀNH VIÊN 3 — Lexical Search & RRF Reranking
## Vai trò: Sparse Retrieval (BM25) → Gộp thứ hạng đa nguồn

**Bạn là thành viên phụ trách tìm kiếm theo từ khóa và gộp kết quả từ nhiều nguồn.**
**Các task của bạn: Task 6 → Task 7 (chính).**
**File này hướng dẫn bạn dùng AI để hoàn thành từng bước.**

---

## Nhiệm vụ 1: Task 6 — Lexical Search (BM25) (phút 35–60)

### Mục tiêu
Hoàn thiện `lexical_search(query, top_k=10)` dùng BM25 để tìm chunks chứa từ khóa chính xác.

### Điều kiện bắt đầu
Task 3 phải hoàn thành (file `.md` tồn tại trong `data/standardized/`).

### Cách làm
1. Mở file `src/task6_lexical_search.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task6_lexical_search.py với các yêu cầu:

THƯ VIỆN: pip install rank-bm25

HÀM 1: build_bm25_index(corpus: list[dict])
- Đọc tất cả .md từ data/standardized/legal/ và data/standardized/news/
- Tokenize mỗi document (dùng .split() hoặc underthesea cho tiếng Việt)
- Xây dựng BM25 index bằng BM25Okapi
- Lưu corpus gốc vào biến toàn cục CORPUS: list[dict]
  Format: [{"content": "...", "metadata": {...}}, ...]

HÀM 2: lexical_search(query: str, top_k: int = 10) -> list[dict]
- Gọi build_bm25_index() nếu chưa có (lazy initialization)
- Tokenize query
- Tính BM25 scores cho tất cả documents
- Sắp xếp giảm dần theo score
- Trả về top_k kết quả theo format BẮT BUỘC:
  [
    {
      "content": "Nội dung chunk...",
      "score": 12.5,       # BM25 score, cao hơn = tốt hơn
      "metadata": {
        "source": "tên file gốc",
        "chunk_index": 3,
        "source_path": "data/standardized/legal/tuition-fees.md"
      }
    },
    ...
  ]

QUAN TRỌNG:
- Output format PHẢI khớp với Task 5 (semantic_search):
  cả hai phải trả về [{content, score, metadata}]
- BM25 score KHÔNG giới hạn [0,1], có thể là số thực dương bất kỳ
- Dùng simple tokenizer (.split()) hoặc underthesea cho tiếng Việt
  - pip install underthesea  # cho tiếng Việt
- Nếu corpus rỗng: trả về list rỗng [], KHÔNG raise lỗi
- Hàm phải gọi được nhiều lần (stateless sau khi build index)
```

### Bonus (nếu thời gian cho phép)
```
Thêm TF-IDF làm alternative:
1. Viết hàm build_tfidf_index(corpus)
2. Viết hàm tfidf_search(query, top_k)
3. Giải thích sự khác nhau giữa BM25 và TF-IDF trong code comment
→ +5 điểm bonus nếu trình bày trong demo
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask6 -v
```

---

## Nhiệm vụ 2: Task 7 — RRF Reranking (phút 60–85)

### Mục tiêu
Hoàn thiện `rerank_rrf()` và `rerank()` để gộp kết quả từ Task 5 (semantic) và Task 6 (BM25).

### Điều kiện bắt đầu
Task 5 (M2) và Task 6 (bạn) phải hoàn thành.

### Cách làm
1. Mở file `src/task7_reranking.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task7_reranking.py với các yêu cầu:

CÔNG THỨC RRF (Reciprocal Rank Fusion):
RRF(d) = Σ 1 / (k + r(d))

Trong đó:
- d = document/chunk
- r(d) = thứ hạng của d trong list kết quả (1 = cao nhất)
- k = 60 (hằng số, không đổi)

HÀM 1: rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]
- ranked_lists: list chứa các list kết quả từ nhiều ranker
  Ví dụ: [semantic_results, lexical_results]
- Mỗi ranked_list có format: [{content, score, metadata}, ...]
- Gộp tất cả documents từ các ranked_lists
- Tính RRF score cho mỗi document: sum(1/(k + rank_in_each_list))
- Loại bỏ documents trùng lặp (so sánh content)
- Sắp xếp theo RRF score giảm dần
- Trả về top_k kết quả

HÀM 2: rerank(query: str, candidates: list[dict], top_k: int = 5, method: str = "rrf") -> list[dict]
- candidates: list kết quả từ semantic_search hoặc lexical_search
- method: "rrf", "cross_encoder", hoặc "mmr"
- Nếu method="rrf": gọi rerank_rrf
- Nếu method="mmr": gọi rerank_mmr
- Nếu method="cross_encoder": gọi rerank_cross_encoder (nếu có API key)

HÀM 3: rerank_mmr(query_embedding, candidates, top_k=5, lambda_param=0.7)
- Maximal Marginal Relevance: cân bằng relevance và diversity
- MMR_score = λ * similarity(query, doc) - (1-λ) * max_similarity(doc, selected)
- Chọn docs có MMR score cao nhất

HÀM 4: rerank_cross_encoder(query, candidates, top_k=5)
- Gọi Jina Reranker API hoặc dùng cross-encoder model local
- pip install requests  # cho API
- Trả về documents đã re-scored

OUTPUT FORMAT (phải khớp với Task 5 và Task 6):
[
  {
    "content": "Nội dung chunk...",
    "score": 0.15,       # RRF score (sau khi fuse)
    "metadata": {...},
    "source": "hybrid"   # "hybrid" hoặc "semantic" hoặc "lexical"
  },
  ...
]

QUAN TRỌNG:
- RRF chỉ dùng THỨ HẠNG (rank), không dùng raw score
- k=60 là BẮT BUỘC, không thay đổi
- Điểm RRF chỉ dùng để SẮP XẾP, KHÔNG dùng để so sánh ngưỡng
- Loại trùng bằng content (text) chứ không phải metadata
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask7 -v
```

---

## Mốc chốt cho Thành viên 3

| Thời gian | Mốc | Kiểm tra |
|:---|:---|:---|
| 1:00 | Task 6 xong (chờ Task 3 từ M4) | `pytest TestTask6 -v` |
| 1:20 | Task 7 xong (chờ Task 5 từ M2) | `pytest TestTask7 -v` |
| **1:25** | **Task 6 + Task 7 chạy được** | `pytest TestTask6 TestTask7 -v` |

## Giao tiếp với team

1. **Task 6 cần Task 3**: Nếu M4 chưa xong Task 3, bạn vẫn viết được khung BM25. Khi data có, chỉ cần gọi lại `build_bm25_index()`.
2. **Task 7 cần Task 5 + Task 6**: Sau khi Task 6 xong, nhắn M2 (semantic) kiểm tra output format khớp nhau.
3. **Phối hợp với M2 về output format**: Cả Task 5 và Task 6 phải trả về `{content, score, metadata}`. Metadata keys phải nhất quán.
4. **Task 9 của M4**: Sau khi Task 7 xong, nhắn M4 để kết nối vào `task9_retrieval_pipeline.py`.
5. **Commit sau mỗi task**: `git add . && git commit -m "feat(task6-7): mô tả"`.

## So sánh BM25 vs Semantic Search

Khi demo, bạn cần giải thích sự khác biệt:

| Khía cạnh | BM25 (Lexical) | Semantic (Dense) |
|:---|:---|:---|
| **Cơ chế** | Đếm từ, TF-IDF | Vector embedding |
| **Tìm kiếm** | Từ khóa chính xác | Ngữ nghĩa tương tự |
| **Mạnh với** | Số hiệu, tên riêng, mã văn bản | Câu hỏi diễn đạt khác tài liệu |
| **Yếu với** | Từ đồng nghĩa, paraphrase | Từ khóa đặc biệt |

**Kết hợp cả hai = Hybrid Retrieval**: bù đắp điểm yếu cho nhau.
