# PROMPT CHO THÀNH VIÊN 5 — Streamlit Chatbot & RAGAS Evaluation
## Vai trò: Chuẩn bị UI skeleton → Kết nối pipeline → RAGAS Evaluation

**Bạn là thành viên phụ trách giao diện chatbot và đánh giá pipeline.**
**Nhiệm vụ chính: Streamlit app + golden dataset + RAGAS evaluation.**
**File này hướng dẫn bạn dùng AI để hoàn thành từng bước.**

---

## Nhiệm vụ 1: Chuẩn bị sẵn sàng (phút 0–60)

### Task 2 hỗ trợ (nếu M4 chưa bắt đầu)
1. Mở file `src/task2_crawl_news.py` — đọc cấu trúc.
2. Dùng AI với prompt:

```
Hãy hoàn thiện src/task2_crawl_news.py:

THƯ VIỆN: pip install crawl4ai playwright
           playwright install chromium

1. ARTICLE_URLS: Danh sách ≥5 URL bài viết từ trang công khai đại học
   - Ví dụ: tin tức từ rmit.edu.vn, vnu.edu.vn...
   - Crawl: sự kiện, thư viện, hỗ trợ sinh viên, học bổng

2. Hàm crawl_article(url: str) -> dict:
   - Dùng AsyncWebCrawler từ crawl4ai
   - Trích xuất: title, url, date_crawled, content_markdown
   - Lưu thành JSON vào data/landing/news/
   - Tên file: slug của title + .json

3. Hàm crawl_all():
   - Gọi crawl_article cho từng URL trong ARTICLE_URLS
   - Dùng asyncio.gather để crawl song song

OUTPUT FORMAT (mỗi file JSON):
{
  "url": "https://...",
  "title": "Tiêu đề bài viết",
  "date_crawled": "2024-01-15",
  "content_markdown": "Nội dung..."
}

QUAN TRỌNG:
- Nếu website trả 403: dùng dữ liệu mẫu trong repo
- Nếu crawl4ai lỗi: pip install playwright && playwright install chromium
- Có thể dùng requests + BeautifulSoup làm fallback
```

### Chuẩn bị app.py skeleton (phút 35–85)
1. Mở file `app.py` — đọc cấu trúc hiện tại.
2. Dùng AI với prompt:

```
Hãy viết khung app.py (Streamlit chatbot) với các yêu cầu:

import streamlit as st

# CẤU HÌNH TRANG
st.set_page_config(
    page_title="University Services RAG Chatbot",
    page_icon="🎓",
    layout="wide"
)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

# SIDEBAR - CÀI ĐẶT
def render_sidebar():
    st.sidebar.title("Cài đặt")
    top_k = st.sidebar.slider("Top K", 1, 10, 5)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3)
    use_reranking = st.sidebar.checkbox("Dùng Reranking", value=True)
    return {"top_k": top_k, "temperature": temperature, "use_reranking": use_reranking}

# MAIN CHAT AREA
def render_chat():
    st.title("🎓 University Services RAG Chatbot")
    st.markdown("Hỏi tôi về chính sách và dịch vụ đại học")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Hiển thị sources sau mỗi câu trả lời
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        if "sources" in last_msg:
            with st.expander("📚 Tài liệu tham khảo"):
                for i, src in enumerate(last_msg["sources"]):
                    st.markdown(f"**{i+1}.** {src.get('metadata', {}).get('source', 'N/A')}")
                    st.markdown(f"   Score: {src.get('score', 'N/A'):.4f}")

# CÂU HỎI GỢI Ý
SUGGESTED_QUESTIONS = [
    "Chính sách học phí của trường như thế nào?",
    "Điều kiện nhận học bổng?",
    "Quy trình đăng ký ký túc xá?",
    "Hạn đăng ký học phần?",
]

def render_suggestions():
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    for i, (col, q) in enumerate(zip(cols, SUGGESTED_QUESTIONS)):
        if col.button(f"💬 {q[:30]}..."):
            st.session_state.suggested_query = q

# HÀM XỬ LÝ CÂU HỎI (VIẾT SẴN, KẾT NỐI SAU)
def handle_query(query: str, settings: dict):
    # TODO: Kết nối với Task 9 + Task 10 khi hoàn thành
    # from src.task10_generation import generate_with_citation
    # from src.task9_retrieval_pipeline import retrieve
    
    # Placeholder response:
    response = {
        "answer": "Tính năng đang được phát triển. Vui lòng chờ Task 9 và Task 10 hoàn thành.",
        "sources": [],
        "retrieval_source": "none"
    }
    
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "sources": response["sources"]
    })

# MAIN
if __name__ == "__main__":
    settings = render_sidebar()
    render_chat()
    render_suggestions()
    
    query = st.chat_input("Nhập câu hỏi của bạn...")
    if query:
        handle_query(query, settings)
```

**Viết KHUNG trước, kết nối sau khi Task 9+10 xong.**

---

## Nhiệm vụ 2: Kết nối pipeline vào Streamlit (phút 85–125)

### Sau khi Task 9 và Task 10 hoàn thành
Dùng AI với prompt:

```
Hãy cập nhật hàm handle_query trong app.py để kết nối với pipeline thực:

1. Import ở đầu file:
   from src.task10_generation import generate_with_citation
   from src.task9_retrieval_pipeline import retrieve

2. Cập nhật handle_query():
   def handle_query(query: str, settings: dict):
       # Gọi pipeline
       result = generate_with_citation(
           query=query,
           top_k=settings["top_k"]
       )
       
       # Trích xuất answer và sources
       answer = result.get("answer", "Không có câu trả lời.")
       sources = result.get("sources", [])
       
       # Thêm vào chat history
       st.session_state.messages.append({
           "role": "user",
           "content": query
       })
       st.session_state.messages.append({
           "role": "assistant",
           "content": answer,
           "sources": sources
       })
       
       # Hiển thị retrieval source
       source_type = result.get("retrieval_source", "unknown")
       if source_type == "pageindex":
           st.info("🔄 Đang dùng PageIndex Fallback")

3. Thêm streaming response (nếu thời gian cho phép):
   - Dùng st.write_stream() thay vì st.markdown() để stream từng từ

4. Thêm conversation memory (bonus):
   - Lưu conversation history trong session_state
   - Mỗi câu hỏi mới kèm context từ 3 câu hỏi trước
```

---

## Nhiệm vụ 3: Golden Dataset cho RAGAS (phút 85–125)

### Mục tiêu
Tạo `group_project/evaluation/golden_dataset.json` với ≥15 cặp Q&A.

### Cách làm
Dùng AI với prompt:

```
Hãy tạo file group_project/evaluation/golden_dataset.json với ≥15 cặp Q&A:

FORMAT:
[
  {
    "question": "Câu hỏi 1?",
    "expected_answer": "Câu trả lời mong đợi dựa trên tài liệu...",
    "expected_context": ["Tên file 1 chứa thông tin", "Tên file 2 chứa thông tin"]
  },
  ...
]

YÊU CẦU:
1. ≥15 câu hỏi đa dạng:
   - 3-4 câu: học phí, thanh toán
   - 3-4 câu: học bổng, tiêu chí nhận
   - 2-3 câu: ký túc xá, đăng ký ở
   - 2-3 câu: đăng ký học phần, lịch
   - 2-3 câu: dịch vụ thư viện, hỗ trợ SV
   - 2 câu: câu hỏi KHÔNG có trong tài liệu (test fallback)
   - 1-2 câu: câu hỏi tổng hợp cần nhiều file

2. Mỗi câu hỏi phải:
   - Có câu trả lời thực sự trong tài liệu (trừ 2 câu out-of-domain)
   - expected_context liệt kê TÊN FILE chứa thông tin
   - expected_answer ngắn gọn (2-3 câu)

3. Đặt tên file output: group_project/evaluation/golden_dataset.json

THAM KHẢO NỘI DUNG (nếu có sẵn trong data/standardized/):
- tuition-fees-rmit.pdf: về học phí
- scholarship-policy-rmit.pdf: về học bổng
- accommodation-guidelines.pdf: về ký túc xá
- course-registration.pdf: về đăng ký học phần
```

---

## Nhiệm vụ 4: RAGAS Evaluation Pipeline (phút 135–165)

### Mục tiêu
Viết `group_project/evaluation/eval_pipeline.py` và chạy RAGAS.

### Cách làm
1. Tạo file `group_project/evaluation/eval_pipeline.py`.
2. Dùng AI với prompt:

```
Hãy tạo file group_project/evaluation/eval_pipeline.py:

THƯ VIỆN: pip install ragas datasets

CODE:

import json
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import generate_with_citation

# Đọc golden dataset
def load_golden_dataset(path: str = "group_project/evaluation/golden_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Chạy pipeline trên từng câu hỏi
def run_pipeline_on_question(question: str) -> dict:
    result = generate_with_citation(query=question, top_k=5)
    return {
        "answer": result.get("answer", ""),
        "sources": [s.get("content", "") for s in result.get("sources", [])]
    }

# Chuẩn bị data cho RAGAS
def prepare_eval_data(golden_data: list) -> Dataset:
    eval_data = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "ground_truth": [],
    }
    
    for item in golden_data:
        result = run_pipeline_on_question(item["question"])
        eval_data["user_input"].append(item["question"])
        eval_data["response"].append(result["answer"])
        eval_data["retrieved_contexts"].append(result["sources"])
        eval_data["ground_truth"].append(item["expected_answer"])
    
    return Dataset.from_dict(eval_data)

# Chạy evaluation
def run_evaluation():
    print("Loading golden dataset...")
    golden_data = load_golden_dataset()
    
    print("Running pipeline on questions...")
    eval_dataset = prepare_eval_data(golden_data)
    
    print("Evaluating with RAGAS...")
    result = evaluate(
        eval_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        ]
    )
    
    print("\n=== RAGAS RESULTS ===")
    print(result.to_pandas())
    
    # Lưu kết quả
    result_df = result.to_pandas()
    result_df.to_csv("group_project/evaluation/ragas_scores.csv", index=False)
    
    return result

if __name__ == "__main__":
    result = run_evaluation()

LƯU Ý QUAN TRỌNG:
- RAGAS gọi LLM nhiều lần → có thể chạm rate limit (429)
- Test trước với 3-5 câu hỏi đầu tiên
- Nếu rate limit: giảm số câu hỏi, thử lại sau
- API key: đảm bảo OPENROUTER_API_KEY trong .env
```

---

## Nhiệm vụ 5: Viết results.md (phút 165–175)

### Tạo file `group_project/evaluation/results.md`

```
# RAG Evaluation Results

## Dataset
- Số câu hỏi: XX
- Nguồn: golden_dataset.json

## Pipeline Config
- Semantic Search: BAAI/bge-m3
- Lexical Search: BM25
- Reranking: RRF (k=60)
- Fallback: PageIndex
- LLM: gpt-4o-mini (OpenRouter)

## RAGAS Scores

| Metric | Score |
|--------|-------|
| Faithfulness | X.XX |
| Answer Relevancy | X.XX |
| Context Recall | X.XX |
| Context Precision | X.XX |

## A/B Comparison

| Config | Faithfulness | Answer Relevancy | Context Recall | Context Precision |
|--------|:---:|:---:|:---:|:---:|
| Hybrid (RRF) | X.XX | X.XX | X.XX | X.XX |
| Dense-Only | X.XX | X.XX | X.XX | X.XX |

## Worst Performers

[Caption 2-3 câu hỏi có điểm thấp nhất + giải thích]

## Analysis

[Phân tích: Hybrid vs Dense-Only, khi nào fallback hoạt động...]

## Limitations & Next Steps

[Rate limit, data quality, potential improvements...]
```

---

## Mốc chốt cho Thành viên 5

| Thời gian | Mốc | Kiểm tra |
|:---|:---|:---|
| 0:60 | app.py skeleton viết xong | Mở `streamlit run app.py` |
| 1:25 | Kết nối Task 9+10 vào app.py | Demo chat trong Streamlit |
| 1:35 | golden_dataset.json ≥15 câu | Kiểm tra số lượng |
| 2:00 | eval_pipeline.py chạy được | `python -m group_project.evaluation.eval_pipeline` |
| **2:15** | **results.md hoàn chỉnh** | ⭐ CP5 PASSED |

## Giao tiếp với team

1. **Task 2**: Nếu M4 chưa bắt đầu Task 2, bạn làm.
2. **Khi Task 9+10 xong**: M2/M4 sẽ nhắn, lúc đó bạn kết nối vào app.py.
3. **RAGAS rate limit**: Nếu gặp lỗi 429, giảm golden dataset xuống 5 câu, thử lại sau.
4. **Commit sau mỗi phần**: `git add . && git commit -m "feat(app-eval): mô tả"`.

## Bonus opportunity

- Conversation memory (multi-turn chat): +3 điểm
- Deploy online (HuggingFace Spaces): +4 điểm
- UI hiển thị score, highlight: +3 điểm
