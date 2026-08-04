# Phân Công Nhóm — RAG Pipeline v2 (5 Thành Viên)

> **Nguyên tắc**: Các thành viên được giao task theo **dependency chain** để minimize waiting.
> Task 1→2→3→4→5/6→7→8→9→10. Các task 5 và 6 hoàn toàn song song. Task 8 chạy song song với Task 5→7.
> Mốc chốt: **CP4 (phút 85)** = toàn bộ Task 1-10 chạy được → **50 điểm Pipeline Kỹ Thuật**.

---

## Dependency Graph

```
                    [Task 1] ──────┐
                                   ├──→ [Task 3] ──→ [Task 4] ──────────────┐
                    [Task 2] ──────┘                                         │
                                                                         [Task 5] ──┐
                                                                         [Task 6] ──┼──→ [Task 7] ──→ [Task 9] ──→ [Task 10]
                    [Task 3] ──────────────────────────────────────→ [Task 8] ──┘
```

### Luồng song song khả thi

| Phase | Thành viên A làm | Thành viên B làm | Thành viên C làm |
|:-----:|:---:|:---:|:---:|
| **0–10 phút** | Setup + Task 1 | Setup + Task 2 | Setup |
| **10–35 phút** | Task 3 (legal) | Task 3 (news) | — |
| **35–60 phút** | Task 4 (index) | Task 5 (semantic) | Task 6 (BM25) |
| **60–85 phút** | Task 8 (PageIndex) | Task 7 (rerank) | Task 5→7 refine |
| **85 phút** | **ALL → pytest 35/35** | | |
| **85–135 phút** | Task 10 (generation) | Task 9 (pipeline) | Task 9 refine |
| **135–165 phút** | **Streamlit app.py** | **RAGAS golden dataset** | **eval_pipeline.py** |
| **165–180 phút** | **Review & Demo prep** | | |

---

## Phân công chi tiết

### 👑 Thành viên 1 — Team Lead & Data Pipeline
**File prompt**: `prompts/member1_data_pipeline.md`

**Nhiệm vụ**: Task 1 → Task 3 (legal) → Task 4 → Task 8

| Task | File | Mốc | Điểm |
|:----:|:-----|:----|:-----:|
| Task 1 | `src/task1_collect_legal_docs.py` | CP1 | 3 |
| Task 3 (legal) | `src/task3_convert_markdown.py` | CP1 | part of 4 |
| Task 4 | `src/task4_chunking_indexing.py` | CP2 | 7 |
| Task 8 | `src/task8_pageindex_vectorless.py` | CP3 | 4 |

**Điều kiện bắt đầu Task 4**: Task 3 (legal) phải hoàn thành (file `.md` tồn tại trong `data/standardized/legal/`).

**Điều kiện bắt đầu Task 8**: Task 3 hoàn thành (dùng `data/standardized/`).

**Checkpoint chốt**: Sau phút 60 — Task 4 + Task 8 chạy được, chờ Task 5/6/7.

**Test chạy**: `pytest tests/test_individual.py::TestTask1 -v` + `TestTask4 -v` + `TestTask8 -v`.

---

### 🔬 Thành viên 2 — Semantic Search & Generation
**File prompt**: `prompts/member2_semantic_generation.md`

**Nhiệm vụ**: Task 5 → Task 7 (hỗ trợ) → Task 10

| Task | File | Mốc | Điểm |
|:----:|:-----|:----|:-----:|
| Task 5 | `src/task5_semantic_search.py` | CP2 | 6 |
| Task 7 (hỗ trợ logic) | `src/task7_reranking.py` | CP3 | part of 6 |
| Task 10 | `src/task10_generation.py` | CP4 | 4 |

**Điều kiện bắt đầu Task 5**: Task 4 phải hoàn thành (`chroma_db/` có data).

**Điều kiện bắt đầu Task 10**: Task 9 phải hoàn thành (pipeline `retrieve()` chạy được).

**Checkpoint chốt**: Sau phút 60 — Task 5 chạy được. Task 10 cần Task 9 trước (có thể viết khung trước, kết nối sau).

**Test chạy**: `pytest tests/test_individual.py::TestTask5 -v` + `TestTask10 -v`.

---

### 📊 Thành viên 3 — Lexical Search & Reranking
**File prompt**: `prompts/member3_bm25_rerank.md`

**Nhiệm vụ**: Task 6 → Task 7 (chính) → Task 9 (hỗ trợ)

| Task | File | Mốc | Điểm |
|:----:|:-----|:----|:-----:|
| Task 6 | `src/task6_lexical_search.py` | CP2 | 6 |
| Task 7 | `src/task7_reranking.py` | CP3 | 6 |
| Task 9 (hỗ trợ interface) | `src/task9_retrieval_pipeline.py` | CP4 | part of 7 |

**Điều kiện bắt đầu Task 6**: Task 3 phải hoàn thành (file `.md` tồn tại — dùng nội dung để build BM25 corpus).

**Điều kiện bắt đầu Task 7**: Task 5 và Task 6 phải hoàn thành (cần kết quả từ cả hai để gộp RRF).

**Checkpoint chốt**: Sau phút 60 — Task 6 chạy được. Task 7 cần cả Task 5+6 (bắt đầu phút 60–80).

**Test chạy**: `pytest tests/test_individual.py::TestTask6 -v` + `TestTask7 -v`.

---

### ⚙️ Thành viên 4 — Pipeline Integration & Orchestration
**File prompt**: `prompts/member4_pipeline_integration.md`

**Nhiệm vụ**: Task 3 (news) → Task 9 (chính) → Tổng hợp pipeline

| Task | File | Mốc | Điểm |
|:----:|:-----|:----|:-----:|
| Task 3 (news) | `src/task3_convert_markdown.py` | CP1 | part of 4 |
| Task 9 | `src/task9_retrieval_pipeline.py` | CP4 | 7 |
| Tích hợp pipeline | N/A | CP4 | — |

**Điều kiện bắt đầu Task 3 (news)**: Task 2 phải hoàn thành.

**Điều kiện bắt đầu Task 9**: Task 5, 6, 7, 8 phải hoàn thành.

**Checkpoint chốt**: Phút 60–85 — viết khung Task 9, chờ Task 5/6/7/8 xong thì kết nối. **Đây là task người cuối cùng hoàn thành** (Task 9 là mốc nối mọi thứ lại).

**Trách nhiệm thêm**: Sau phút 85, kiểm tra tất cả các task chạy `pytest` và hỗ trợ fix lỗi nếu test fail.

**Test chạy**: `pytest tests/test_individual.py::TestTask9 -v`.

---

### 🎨 Thành viên 5 — Streamlit Chatbot & RAGAS Evaluation
**File prompt**: `prompts/member5_chatbot_evaluation.md`

**Nhiệm vụ**: Chuẩn bị sẵn sàng → Task 10 (hỗ trợ kết nối) → Streamlit + RAGAS

| Nhiệm vụ | File | Mốc | Điểm |
|:----------|:-----|:----|:-----:|
| Chuẩn bị `app.py` skeleton | `app.py` | CP5 | part of 8 |
| Chuẩn bị golden dataset | `group_project/evaluation/golden_dataset.json` | CP5 | 3 |
| Chuẩn bị eval pipeline | `group_project/evaluation/eval_pipeline.py` | CP5 | part of 12 |
| Kết nối Task 10 vào `app.py` | `app.py` | CP5 | part of 8 |
| Chạy RAGAS + viết results | `group_project/evaluation/results.md` | CP5 | part of 12 |

**Điều kiện bắt đầu chính**: Task 10 phải hoàn thành (để kết nối `generate_with_citation()` vào chatbot).

**Điều kiện bắt đầu RAGAS**: Task 9 + Task 10 chạy được.

**Checkpoint chốt**:
- Phút 60–85: Viết sẵn `app.py` skeleton, import Task 10, chuẩn bị golden dataset.
- Phút 85–135: Kết nối pipeline thực vào Streamlit khi Task 10 + 9 xong.
- Phút 135–165: Chạy RAGAS, viết results.

**Test chạy**: `pytest tests/test_individual.py -v` (toàn bộ) + demo Streamlit.

---

## Timeline tổng hợp (180 phút)

| Thời gian | CP | Sự kiện | Ai làm gì |
|:---|:---|:---|:---|
| 0:00–0:10 | CP0 | Setup | **Tất cả**: clone repo, venv, `.env`, chia prompt |
| 0:10–0:35 | CP1 | Data | **M1**: Task 1 (legal). **M4**: Task 2 (news). **M3**: chờ Task 2 |
| 0:35–0:60 | CP2 | Index+Search | **M1**: Task 3 legal → Task 4. **M2**: Task 5. **M3**: Task 6 |
| 0:60–0:85 | CP3 | Rerank+Fallback | **M1**: Task 8. **M2**: hỗ trợ Task 7. **M3**: Task 7. **M4**: Task 9 (viết khung) |
| 0:85 | ⭐ | **CHỐT 50 ĐIỂM** | **Tất cả**: `pytest tests/test_individual.py` — 35/35 |
| 0:85–1:25 | CP4b | Pipeline + Gen | **M4**: kết nối Task 9. **M2**: Task 10 |
| 1:25–1:45 | | Refine | **M2**: kết nối Task 10. **M4**: verify pipeline. **M1**: review code |
| 1:45–2:15 | CP5 | Nhóm | **M5**: Streamlit + RAGAS. **M1–4**: hỗ trợ |
| 2:15–3:00 | CP6 | Demo | **Tất cả**: thuyết trình + push GitHub |

---

## Quy tắc làm việc nhóm

1. **Không đợi nhau vô ích**: Nếu task của bạn phụ thuộc vào task chưa xong, chuyển sang làm phần khác hoặc viết khung code trước.
2. **Commit thường xuyên**: Mỗi task xong → commit ngay. Message format: `feat(taskN): mô tả ngắn`.
3. **Test ngay sau khi viết**: Chạy `pytest tests/test_individual.py::TestTaskN -v` trước khi chuyển task.
4. **Task 9 là của M4**: Dù M2/M3 viết Task 5/6/7, **M4 chịu trách nhiệm kết nối** tất cả vào `task9_retrieval_pipeline.py`.
5. **Task 10 là của M2**: M2 viết `task10_generation.py`, M5 kết nối vào `app.py`.
6. **Git conflict**: Nếu 2 người sửa cùng file, **M4 (Team Lead)** quyết định phiên bản nào giữ.
7. **API key**: `.env` phải có `OPENROUTER_API_KEY`. `PAGEINDEX_API_KEY` cần cho Task 8.

---

## Bảng tổng hợp điểm theo thành viên

| Thành viên | Task | Tổng điểm cá nhân |
|:---|:---|:---:|
| M1 (Data Pipeline) | 1 + 3(legal) + 4 + 8 | 3 + 2 + 7 + 4 = **16** |
| M2 (Semantic + Gen) | 5 + 10 | 6 + 4 = **10** |
| M3 (BM25 + Rerank) | 6 + 7 | 6 + 6 = **12** |
| M4 (Pipeline Lead) | 3(news) + 9 | 2 + 7 = **9** |
| M5 (Chatbot + Eval) | (không tính vào 50đ cá nhân — là phần nhóm) | — |
| **Verification** | `pytest tests/test_individual.py -v` (tất cả chạy) | **35/35 = 50** |

> **Ghi chú**: Điểm trên là ước lượng dựa trên tỷ trọng task. Thực tế điểm cá nhân = **tổng điểm task mà cá nhân đó viết code**, không phải cứng nhắc theo bảng trên. Quan trọng là **tất cả 35 test phải pass**, không phân biệt ai viết task nào.
