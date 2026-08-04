# PROMPT CHO THÀNH VIÊN 2 — Semantic Search & Generation
## Vai trò: Dense Retrieval → Document Reordering → LLM Generation có Citation

**Bạn là thành viên phụ trách tìm kiếm ngữ nghĩa và sinh câu trả lời.**
**Các task của bạn: Task 5 → Task 7 (hỗ trợ) → Task 10.**
**File này hướng dẫn bạn dùng AI để hoàn thành từng bước.**

---

## Nhiệm vụ 1: Task 5 — Semantic Search Module (phút 35–60)

### Mục tiêu
Hoàn thiện `semantic_search(query, top_k=10)` trả về chunks được xếp theo cosine similarity giảm dần.

### Điều kiện bắt đầu
Task 4 (của M1) phải hoàn thành → `chroma_db/` có data.

### Cách làm
1. Mở file `src/task5_semantic_search.py` — đọc cấu trúc hiện tại.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task5_semantic_search.py với các yêu cầu:

HÀM CHÍNH: semantic_search(query: str, top_k: int = 10) -> list[dict]

1. Load ChromaDB từ thư mục chroma_db/
   - Collection: "university_services_docs"
   - pip install chromadb sentence-transformers

2. Tạo embedding cho query bằng model "BAAI/bge-m3"
   - Dùng sentence_transformers.SentenceTransformer

3. Query ChromaDB với n_neighbors=top_k
   - ChromaDB hỗ trợ query trực tiếp với include=["documents", "metadatas", "distances"]
   - Điểm distance cần convert sang similarity: score = 1 - distance (vì ChromaDB dùng L2 distance)

4. Trả về list[dict] theo format BẮT BUỘC:
   [
     {
       "content": "Nội dung chunk...",
       "score": 0.85,         # similarity score [0, 1], cao hơn = tốt hơn
       "metadata": {
         "source": "tên file gốc",
         "chunk_index": 3,
         "source_path": "data/standardized/legal/tuition-fees.md"
       }
     },
     ...
   ]

5. Sắp xếp theo score giảm dần (cao nhất lên đầu)

QUAN TRỌNG:
- Dùng ĐÚNG model "BAAI/bge-m3" (phải khớp với Task 4)
- Điểm score phải là cosine similarity [0, 1], KHÔNG phải L2 distance
- Hàm phải trả về top_k kết quả tốt nhất
- Nếu ChromaDB chưa có data: trả về list rỗng [], KHÔNG raise lỗi
```

### Bonus (nếu thời gian cho phép)
```
Thêm module HyDE (Hypothetical Document Embeddings):
1. Gọi LLM sinh một đoạn trả lời giả định cho query
2. Embed đoạn giả định đó thay vì query gốc
3. Dùng kết quả để query ChromaDB
→ Giúp tìm được các chunk có ngữ cảnh tương tự câu trả lời, không chỉ query
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask5 -v
```

---

## Nhiệm vụ 2: Task 7 — Hỗ trợ RRF Reranking (phút 60–80, phối hợp với M3)

### Mục tiêu
Đảm bảo output của Task 5 và Task 6 có cùng format để Task 7 (do M3 viết) gộp được.

### Cách làm
1. Phối hợp với M3 để thống nhất output format.
2. Format bắt buộc (đã nêu ở trên): `{content, score, metadata}`.
3. M3 sẽ viết hàm `rerank_rrf()`, bạn chỉ cần đảm bảo Task 5 trả về đúng format.

### Nếu M3 chưa xong Task 7, bạn có thể viết trước
```
Hãy viết hàm rerank_rrf trong src/task7_reranking.py:

def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """
    Gộp thứ hạng từ nhiều ranker bằng Reciprocal Rank Fusion.
    ranked_lists: list của các list kết quả từ semantic_search, lexical_search, ...
    k = 60 (hằng số RRF)
    RRF(d) = sum(1 / (k + rank(d)))
    """
    ...
```

---

## Nhiệm vụ 3: Task 10 — Generation có Citation (phút 85–125)

### Mục tiêu
Hoàn thiện `generate_with_citation(query, top_k=5)` — reorder chunks → gọi LLM → trả lời có citation.

### Điều kiện bắt đầu
Task 9 (của M4) phải có kết quả `retrieve()` chạy được.

### Cách làm
1. Mở file `src/task10_generation.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task10_generation.py với các yêu cầu:

CONFIG:
- TOP_K = 5
- TOP_P = 0.9
- TEMPERATURE = 0.3
- LLM_MODEL = "openai/gpt-4o-mini"  # hoặc model qua OpenRouter

HÀM 1: reorder_for_llm(chunks: list[dict]) -> list[dict]
- Áp dụng kỹ thuật chống "Lost in the Middle"
- Sắp xếp: chunks[0], chunks[2], chunks[4], chunks[3], chunks[1]
  (hoặc tổng quát: front + back[::-1])
- Giữ nguyên tất cả metadata

HÀM 2: format_context(chunks: list[dict]) -> str
- Format mỗi chunk thành:
  [Nguồn: tên_file.md]
  Nội dung chunk...

HÀM 3: generate_with_citation(query: str, top_k: int = 5) -> dict
- Gọi retrieve() từ task9 (import từ src.task9_retrieval_pipeline)
- Reorder kết quả bằng reorder_for_llm()
- Format context bằng format_context()
- Gọi LLM với prompt:

SYSTEM_PROMPT = """Answer the following question comprehensively.
For every statement of fact, immediately insert a citation in brackets
citing the specific source (e.g., [tuition-fees-rmit.pdf, 2024]).
If the information is NOT in the provided context, say
'I cannot verify this information' rather than guessing.
Do NOT make up information."""

- Trả về dict:
  {
    "answer": "Câu trả lời...",
    "sources": [...],      # list các chunk đã dùng
    "retrieval_source": "hybrid"  # hoặc "pageindex"
  }

QUAN TRỌNG:
- LLM phải trả lời DỰA TRÊN context được cung cấp
- Mỗi khẳng định phải có citation [tên_file.pdf, năm]
- Nếu context rỗng: "I cannot verify this information"
- Xử lý lỗi: nếu API key thiếu, trả về error message rõ ràng

THƯ VIỆN:
- pip install openai
- Hoặc dùng requests gọi OpenRouter API trực tiếp
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask10 -v
```

---

## Mốc chốt cho Thành viên 2

| Thời gian | Mốc | Kiểm tra |
|:---|:---|:---|
| 1:00 | Task 5 xong (chroma_db/ của M1) | `pytest TestTask5 -v` |
| 1:20 | Task 7 hoặc hỗ trợ M3 | `pytest TestTask7 -v` |
| 1:25 | Task 10 chạy được (chờ M4 xong Task 9) | `pytest TestTask10 -v` |
| **1:25** | **Task 5 + Task 10 chạy được** | `pytest TestTask5 TestTask10 -v` |

## Giao tiếp với team

1. **Khi Task 4 xong (M1 báo)**: Bắt đầu ngay Task 5.
2. **Khi Task 5 xong**: Nhắn M3 (BM25) để phối hợp format output cho Task 7.
3. **Khi Task 9 xong (M4 báo)**: Bắt đầu kết nối Task 10.
4. **Task 10 có thể viết khung trước**: Dù M4 chưa xong Task 9, bạn vẫn viết được `reorder_for_llm()` và `format_context()` trước. Chỉ cần `generate_with_citation()` gọi `retrieve()` ở cuối.
5. **Commit sau mỗi task**: `git add . && git commit -m "feat(task5-10): mô tả"`.
