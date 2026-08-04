# PROMPT CHO THÀNH VIÊN 4 — Pipeline Integration & Team Lead
## Vai trò: Convert news → Kết nối Task 9 → Tổng hợp toàn bộ pipeline

**Bạn là thành viên phụ trách nối toàn bộ pipeline và điều phối team.**
**Các task của bạn: Task 3 (news) → Task 9 (chính).**
**File này hướng dẫn bạn dùng AI để hoàn thành từng bước.**

---

## Nhiệm vụ 1: Task 3 (phần news) — Convert bài viết tin tức (phút 10–35)

### Mục tiêu
Convert file JSON từ Task 2 thành Markdown trong `data/standardized/news/`.

### Điều kiện bắt đầu
Task 2 (M5 hoặc bạn) phải hoàn thành.

### Cách làm
1. Mở file `src/task3_convert_markdown.py` — tìm hàm `convert_news_articles()`.
2. Dùng AI với prompt:

```
Hãy hoàn thiện hàm convert_news_articles() trong src/task3_convert_markdown.py:

1. Đọc tất cả file JSON trong data/landing/news/
2. Extract nội dung từ field "content_markdown" hoặc "content"
3. Giữ nguyên metadata (url, title, date_crawled)
4. Lưu thành file .md trong data/standardized/news/
   - Tên file: chuyển title thành slug (không dấu, không khoảng trắng)
   - Nếu có field markdown sẵn trong JSON: dùng trực tiếp, không cần convert

5. Đảm bảo convert_all() gọi được cả convert_legal_docs() và convert_news_articles()

OUTPUT FORMAT trong .md file:
---
title: Tiêu đề bài viết
url: https://...
date: 2024-01-15
---

Nội dung bài viết...
```

---

## Nhiệm vụ 2: Task 9 — Retrieval Pipeline Hoàn Chỉnh (phút 60–125)

### Mục tiêu
Viết hàm `retrieve()` nối Semantic + BM25 + RRF + PageIndex Fallback.

### Điều kiện bắt đầu
Task 5 (M2), Task 6 (M3), Task 7 (M3), Task 8 (M1) phải hoàn thành.

### Cách làm
1. Mở file `src/task9_retrieval_pipeline.py` — đọc cấu trúc.
2. **Viết khung TRƯỚC** (phút 60–80) khi Task 5/6/7/8 chưa xong.
3. Dùng AI với prompt:

```
Hãy hoàn thiện src/task9_retrieval_pipeline.py với các yêu cầu:

CONFIG:
- SCORE_THRESHOLD = 0.3
- DEFAULT_TOP_K = 5
- RERANK_METHOD = "rrf"
- FALLBACK_THRESHOLD = 0.48  # cosine score threshold cho PageIndex fallback

HÀM CHÍNH: retrieve(query: str, top_k: int = 5, score_threshold: float = 0.3, use_reranking: bool = True) -> list[dict]

PIPELINE LOGIC (thứ tự BẮT BUỘC):

1. Gọi semantic_search(query, top_k*2) từ task5
   - Import: from src.task5_semantic_search import semantic_search

2. Gọi lexical_search(query, top_k*2) từ task6
   - Import: from src.task6_lexical_search import lexical_search

3. Nếu use_reranking=True:
   - Gọi rerank_rrf([semantic_results, lexical_results], top_k=top_k) từ task7
   - Import: from src.task7_reranking import rerank_rrf
   - Kết quả = reranked list
   - Lưu ý: RRF chỉ dùng THỨ HẠNG, không dùng điểm RRF

4. Kiểm tra FALLBACK:
   - Lấy điểm cosine gốc từ semantic_results[0]['score']
   - NẾU semantic_results[0]['score'] < 0.48:
     → Gọi pageindex_search(query, top_k) từ task8
     → Kết quả = pageindex_results
   - NẾU KHÔNG:
     → Kết quả = reranked results (từ bước 3)

5. Trả về list[dict]:
   [
     {
       "content": "Nội dung chunk...",
       "score": 0.85,        # cosine score (trước RRF)
       "metadata": {...},
       "source": "hybrid"    # "hybrid" hoặc "pageindex"
     },
     ...
   ]

QUAN TRỌNG - LỖI THƯỜNG GẶP:
⚠️ SAI: Dùng reranked_results[0]['score'] < 0.48
✅ ĐÚNG: Dùng semantic_results[0]['score'] < 0.48

Lý do: Điểm RRF sau khi fuse LUÔN rất nhỏ (~0.016) vì chỉ phụ thuộc rank,
KHÔNG phản ánh độ liên quan thực sự. Dùng điểm COSINE GỐC từ Task 5.

HÀM PHỤ CẦN VIẾT:

def _merge_sources(semantic_results, lexical_results, reranked_results) -> list[dict]:
    """Merge kết quả từ nhiều nguồn, đánh dấu source"""
    ...

def _check_fallback_trigger(semantic_results, threshold=0.48) -> bool:
    """Kiểm tra xem có cần fallback sang PageIndex không"""
    if not semantic_results:
        return True
    return semantic_results[0]['score'] < threshold

FALLBACK LOGIC chi tiết:
- Nếu semantic_results TRỐNG → fallback PageIndex
- Nếu semantic_results[0]['score'] < 0.48 → fallback PageIndex
- Nếu KHÔNG → dùng kết quả RRF đã gộp

XỬ LÝ LỖI:
- Nếu Task 5/6/7/8 chưa hoàn thành: try/except, trả về empty list với warning
- Nếu ChromaDB rỗng: fallback ngay sang PageIndex
- Nếu PageIndex fail: trả về kết quả RRF dù score thấp
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask9 -v
```

---

## Nhiệm vụ 3: Tổng hợp & Verify toàn pipeline (phút 85–125)

### Sau khi Task 9 xong, chạy test toàn bộ
```bash
pytest tests/test_individual.py -v
```

### Nếu có test fail, đây là quy trình debug

**Thứ tự ưu tiên sửa lỗi:**

1. **TestTask1/2/3 fail** → Nhắn M1 (data) hoặc M4 (news) check data
2. **TestTask4 fail** → Nhắn M1 kiểm tra ChromaDB
3. **TestTask5 fail** → Nhắn M2 kiểm tra ChromaDB connection
4. **TestTask6 fail** → Nhắn M3 kiểm tra BM25 corpus
5. **TestTask7 fail** → Kiểm tra M2+M3 format output khớp nhau
6. **TestTask8 fail** → Nhắn M1 kiểm tra PageIndex API key
7. **TestTask9 fail** → Kiểm tra tất cả import và fallback logic
8. **TestTask10 fail** → Nhắn M2 kiểm tra LLM call

---

## Mốc chốt cho Thành viên 4 (Team Lead)

| Thời gian | Mốc | Kiểm tra |
|:---|:---|:---|
| 0:35 | Task 3 (news) xong | `pytest TestTask3 -v` |
| 0:60 | Viết khung Task 9 (dù Task 5/6/7/8 chưa xong) | — |
| 1:25 | Task 9 kết nối xong | `pytest TestTask9 -v` |
| **1:25** | **pytest tests/test_individual.py → 35/35** | ⭐ CP4 PASSED |

## Vai trò Team Lead

1. **Điều phối**: Theo dõi tiến độ các thành viên, nhắc nhở khi gần mốc checkpoint.
2. **Git conflict**: Nếu 2 người sửa cùng file, bạn quyết định version nào giữ.
3. **Review code**: Kiểm tra nhanh code mỗi task trước khi commit.
4. **Fix lỗi cross-task**: Nếu test fail do interface không khớp, bạn là người sửa.
5. **Chốt mốc 35/35**: Sau phút 85, đảm bảo tất cả test pass trước khi chuyển sang phần nhóm.

## Giao tiếp với team

1. **Phút 10**: Nhắn M1 bắt đầu Task 1, nhắn M5 bắt đầu Task 2.
2. **Phút 35**: Xác nhận Task 3 (cả legal và news) xong.
3. **Phút 60**: Xác nhận Task 4, 5, 6 chạy được.
4. **Phút 85**: Chạy `pytest tests/test_individual.py -v` — TẤT CẢ phải pass.
5. **Nếu fail**: Xác định ai sửa, không tự sửa code của người khác mà không báo.

## Commit message convention

```
feat(task1): thu thập văn bản pháp lý
feat(task2): crawl bài viết tin tức  
feat(task3): convert markdown legal + news
feat(task4): chunking + chromadb indexing
feat(task5): semantic search module
feat(task6): lexical search BM25
feat(task7): rrf reranking
feat(task8): pageindex vectorless fallback
feat(task9): retrieval pipeline hoàn chỉnh
feat(task10): generation có citation
```
