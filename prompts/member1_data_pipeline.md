# PROMPT CHO THÀNH VIÊN 1 — Data Pipeline & PageIndex
## Vai trò: Thu thập dữ liệu → Convert → Indexing → Vectorless Fallback

**Bạn là thành viên phụ trách toàn bộ pipeline dữ liệu và fallback dùng PageIndex.**
**Các task của bạn: Task 1 → Task 3 (phần legal) → Task 4 → Task 8.**
**File này hướng dẫn bạn dùng AI để hoàn thành từng bước.**

---

## Nhiệm vụ 1: Task 1 — Thu thập văn bản pháp lý (phút 10–35)

### Mục tiêu
Tải ≥ 3 file PDF/DOCX về chính sách dịch vụ đại học vào thư mục `data/landing/legal/`.

### Cách làm
1. Mở file `src/task1_collect_legal_docs.py` — đọc code hiện tại.
2. Sử dụng AI (Cursor, ChatGPT...) kèm prompt sau:

```
Hãy hoàn thiện file src/task1_collect_legal_docs.py để:
1. Tải ≥ 3 văn bản chính sách PDF từ trang công khai của đại học (ví dụ: RMIT Vietnam, ĐH Quốc Gia,...)
   - Gợi ý: học phí, học bổng, ký túc xá, đăng ký học phần
   - Dùng thư viện requests hoặc urllib để tải file
   - Lưu vào data/landing/legal/ với tên rõ ràng
3. Tạo hàm setup_directory() để tạo thư mục nếu chưa có
4. Giữ nguyên structure và test interface hiện tại
```

### Yêu cầu output
- ≥ 3 file PDF/DOCX trong `data/landing/legal/`
- Mỗi file có dung lượng > 1KB
- Đặt tên file rõ ràng, không dấu cách, không tiếng Việt có dấu
- Ví dụ: `tuition-fees-rmit.pdf`, `scholarship-policy-rmit.pdf`, `accommodation-guidelines.pdf`

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask1 -v
```

---

## Nhiệm vụ 2: Task 3 (phần legal) — Convert sang Markdown (phút 10–35, chạy song song với Task 2)

### Mục tiêu
Convert tất cả file PDF/DOCX trong `data/landing/legal/` thành file `.md` trong `data/standardized/legal/`.

### Cách làm
1. Mở file `src/task3_convert_markdown.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện hàm convert_legal_docs() trong src/task3_convert_markdown.py để:
1. Đọc tất cả file trong data/landing/legal/ (PDF và DOCX)
2. Dùng markitdown để convert sang Markdown
   - Cài đặt: pip install "markitdown[pdf]"
   - Nếu markitdown không đọc được, dùng pypdf hoặc pdfplumber làm fallback
3. Lưu output vào data/standardized/legal/ với extension .md
4. Giữ nguyên tên file gốc, chỉ đổi extension
5. Hàm convert_all() gọi cả convert_legal_docs() và convert_news_articles() song song nếu có thể
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask3 -v
```

---

## Nhiệm vụ 3: Task 4 — Chunking & ChromaDB Indexing (phút 35–60)

### Mục tiêu
Cắt văn bản thành chunk (size=800, overlap=100), tạo embedding bằng model `BAAI/bge-m3`, lưu vào ChromaDB.

### Cách làm
1. Mở file `src/task4_chunking_indexing.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task4_chunking_indexing.py với các yêu cầu sau:

CONFIG:
- CHUNK_SIZE = 800
- CHUNK_OVERLAP = 100
- EMBEDDING_MODEL = "BAAI/bge-m3"
- EMBEDDING_DIM = 1024
- COLLECTION_NAME = "university_services_docs"
- VECTOR_STORE = "chromadb"

HÀM CẦN VIẾT:
1. load_documents(): Đọc tất cả .md từ data/standardized/legal/ và data/standardized/news/
   - Trả về list[dict] với keys: content, metadata (filename, source)
2. chunk_documents(documents): Dùng RecursiveCharacterTextSplitter từ langchain
   - pip install langchain-text-splitters
   - chunk_size=800, chunk_overlap=100
   - Mỗi chunk giữ metadata của document gốc
3. embed_chunks(chunks): Dùng sentence-transformers để tạo embedding
   - pip install sentence-transformers chromadb
   - Dùng model "BAAI/bge-m3"
4. index_to_vectorstore(chunks): Lưu vào ChromaDB
   - Persist tại chroma_db/
   - Collection: "university_services_docs"
5. run_pipeline(): Gọi lần lượt load → chunk → embed → index

QUAN TRỌNG:
- Xóa thư mục chroma_db/ cũ trước khi index lại
- Metadata phải chứa: filename, source_path, chunk_index
- Nếu chroma_db/ đã có data và không muốn xóa: kiểm tra trước, chỉ index nếu cần
```

### Yêu cầu
- Tham số chunking phải khớp: `CHUNK_SIZE=800`, `CHUNK_OVERLAP=100`
- Embedding model: `BAAI/bge-m3`
- ChromaDB persist tại `chroma_db/`

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask4 -v
```

---

## Nhiệm vụ 4: Task 8 — PageIndex Vectorless RAG (phút 60–85)

### Mục tiêu
Tích hợp PageIndex SDK để làm fallback khi hybrid search không đủ tốt.

### Cách làm
1. Mở file `src/task8_pageindex_vectorless.py` — đọc cấu trúc.
2. Đảm bảo có `PAGEINDEX_API_KEY` trong `.env`.
3. Dùng AI với prompt:

```
Hãy hoàn thiện src/task8_pageindex_vectorless.py với các yêu cầu:

1. Hàm upload_documents():
   - Đọc file .md từ data/standardized/
   - Convert sang PDF (dùng fpdf2 hoặc markdown2pdf)
   - Upload lên PageIndex bằng SDK
   - pip install pageindex fpdf2

2. Hàm pageindex_search(query, top_k=5):
   - Gọi PageIndex API để search query
   - Trả về list[dict] với format:
     {'content': str, 'score': float, 'metadata': dict, 'source': 'pageindex'}
   - Đọc PAGEINDEX_API_KEY từ os.environ hoặc .env

THAM KHẢO:
- SDK: https://github.com/VectifyAI/PageIndex
- pip install pageindex

OUTPUT FORMAT (phải khớp với Task 5/6/7 để Task 9 gọi được):
[
  {
    "content": "Nội dung đoạn văn tìm được",
    "score": 0.85,
    "metadata": {"source": "tên file gốc", "title": "tiêu đề"},
    "source": "pageindex"
  },
  ...
]

QUAN TRỌNG: Task 9 sẽ dùng kết quả này khi fallback. Output format phải nhất quán với semantic_search và lexical_search.
```

### Kiểm tra
```bash
pytest tests/test_individual.py::TestTask8 -v
```

---

## Mốc chốt cho Thành viên 1

| Thời gian | Mốc | Kiểm tra |
|:---|:---|:---|
| 0:35 | Task 1 + Task 3(legal) xong | `pytest TestTask1 -v` + `TestTask3 -v` |
| 1:00 | Task 4 xong (chroma_db/ có data) | `pytest TestTask4 -v` |
| 1:20 | Task 8 xong | `pytest TestTask8 -v` |
| **1:25** | **Tất cả task của bạn chạy được** | `pytest TestTask1 TestTask3 TestTask4 TestTask8 -v` |

## Ghi chú quan trọng

1. **Nếu crawl website bị 403**: Dùng dữ liệu mẫu trong repo hoặc tải thủ công.
2. **Nếu markitdown lỗi PDF**: `pip install "markitdown[pdf]"`. Nếu vẫn lỗi, dùng `pypdf` hoặc `pdfplumber`.
3. **Xóa chroma_db/ cũ**: Mỗi lần thay đổi data, chạy `Remove-Item -Recurse -Force chroma_db` trước khi index lại.
4. **Commit sau mỗi task**: `git add . && git commit -m "feat(task1-3-4-8): mô tả"` — không đợi hết mới commit.
5. **Giao tiếp với team**: Sau khi Task 4 xong, nhắn ngay cho M2 (semantic) và M3 (BM25) biết `chroma_db/` đã sẵn sàng.
