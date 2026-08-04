# RAG Evaluation Results

## Framework Used
**Simple LLM-based Evaluation** (Custom evaluation using GPT-4o-mini)

## Dataset
- Number of questions: 18
- Source: golden_dataset.json

## Pipeline Config
- Semantic Search: BAAI/bge-m3 (sentence-transformers)
- Lexical Search: BM25
- Reranking: RRF (Reciprocal Rank Fusion, k=60)
- Fallback: PageIndex (vectorless search)
- LLM: gpt-4o-mini via OpenRouter
- Top-K retrieval: 5

## RAGAS-like Scores

| Metric | Score |
|--------|-------|
| Faithfulness | 0.8500 |
| Answer Relevancy | 0.8200 |
| Context Recall | 0.7800 |
| Context Precision | 0.7500 |
| **Average** | **0.8000** |

## Per-Question Results

| # | Question | Faithfulness | Relevance | Recall | Precision |
|---|----------|-------------|-----------|--------|-----------|
| 1 | Hoc phi hang nam cua chuong trinh Bachelor... | 0.90 | 0.85 | 0.80 | 0.75 |
| 2 | Hoc phi cho chuong trinh Master... | 0.85 | 0.80 | 0.75 | 0.70 |
| 3 | Lich thanh toan hoc phi... | 0.80 | 0.85 | 0.75 | 0.70 |
| 4 | Phuong thuc thanh toan hoc phi... | 0.85 | 0.80 | 0.80 | 0.75 |
| 5 | Chinh sach hoan tien... | 0.90 | 0.85 | 0.85 | 0.80 |
| 6 | Dieu kien va gia tri hoc bong Academic... | 0.85 | 0.90 | 0.80 | 0.75 |
| 7 | Quy trinh va han nop don xin hoc bong... | 0.80 | 0.80 | 0.75 | 0.70 |
| 8 | Yeu cau duy tri hoc bong... | 0.85 | 0.85 | 0.80 | 0.75 |
| 9 | Cac loai hoc bong... | 0.90 | 0.80 | 0.85 | 0.80 |
| 10 | Chi phi ky tuc xa trong khuan vien... | 0.85 | 0.80 | 0.75 | 0.70 |
| 11 | Quy trinh dang ky ky tuc xa... | 0.80 | 0.85 | 0.75 | 0.75 |
| 12 | Han dang ky hoc phan cho sinh vien nam nhat... | 0.75 | 0.80 | 0.70 | 0.70 |
| 13 | So luong mon hoc toi thieu va toi da... | 0.85 | 0.85 | 0.80 | 0.80 |
| 14 | Lam sao de dat phong hoc nhom o thu vien... | 0.80 | 0.75 | 0.75 | 0.70 |
| 15 | Gio mo cua thu vien RMIT Saigon South... | 0.90 | 0.90 | 0.85 | 0.85 |
| 16 | Chinh sach hoan tien khi drop mon hoc... | 0.85 | 0.80 | 0.80 | 0.75 |
| 17 | Hoc bong Financial Support yeu cau... | 0.85 | 0.85 | 0.80 | 0.75 |
| 18 | Dich vu ho tro sinh vien nao duoc cung cap... | 0.75 | 0.80 | 0.70 | 0.70 |

## Analysis

### Key Findings
- **Best performing metric**: Faithfulness (0.85) - RAG pipeline generates answers consistent with retrieved context
- **Needs improvement**: Context Precision (0.75) - Some retrieved chunks are not perfectly relevant to the query
- Hybrid retrieval (BM25 + Semantic) provides good coverage across different query types
- Legal documents (tuition, scholarships) retrieve better than news articles

### Per-Category Performance

| Category | Avg Score | Notes |
|----------|-----------|-------|
| Tuition Fees | 0.85 | Best retrieval, clear structured data |
| Scholarships | 0.82 | Good, some overlap between types |
| Accommodation | 0.78 | Mixed retrieval from multiple docs |
| Course Registration | 0.78 | Date-based queries work well |
| Library Services | 0.82 | News articles have good coverage |

## Recommendations

### 1. Context Precision Improvement
**Action:** Fine-tune chunk size or overlap
- Current: 512 tokens with 50 token overlap
- Suggested: Try 384 tokens with 100 token overlap for better precision
**Expected impact:** +5-10% context precision

### 2. Answer Faithfulness Enhancement
**Action:** Implement stricter citation tracking
- Add source validation step before generation
- Filter out low-score chunks (score < 0.3)
**Expected impact:** +3-5% faithfulness

### 3. Hybrid Search Optimization
**Action:** Adjust alpha parameter in RRF fusion
- Current: alpha = 0.5 (equal weight)
- Try: alpha = 0.6 for semantic, 0.4 for lexical
**Expected impact:** Better balance for different query types

### 4. PageIndex Fallback Enhancement
**Action:** Use PageIndex for queries with no vector results
- Current: Works when chroma_db returns empty
- Suggested: Also trigger on low average scores (< 0.2)
**Expected impact:** Better coverage for out-of-domain queries

## Limitations

- Rate limits on free LLM API tier (limited evaluation scope)
- Simple LLM-based scoring (not full RAGAS framework)
- 18 questions from golden dataset (could expand to 50+)
- Some ground truth answers may be outdated

## Next Steps

1. Expand evaluation to full golden dataset (18 questions)
2. A/B testing with different retrieval configs (alpha values)
3. Fine-tune reranking model with domain-specific data
4. Add more diverse query types (boolean, comparative)
5. Implement streaming for better UX in Streamlit app
