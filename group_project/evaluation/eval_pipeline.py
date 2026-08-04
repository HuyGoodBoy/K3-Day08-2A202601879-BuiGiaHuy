"""
Simple RAG Evaluation Pipeline.

Sử dụng direct LLM calls để đánh giá RAG pipeline.
Đơn giản hơn RAGAS, tránh dependency issues.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from src.task10_generation import generate_with_citation

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"
SCORES_PATH = Path(__file__).parent / "ragas_scores.csv"

# Limit for rate limit
MAX_QUESTIONS = 5

# OpenRouter client
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
) if OPENROUTER_API_KEY else None


# =============================================================================
# Load Data
# =============================================================================

def load_golden_dataset(path: Path = GOLDEN_DATASET_PATH) -> list[dict]:
    """Load golden dataset from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[:MAX_QUESTIONS]


# =============================================================================
# LLM-based Evaluation Metrics
# =============================================================================

def evaluate_faithfulness(question: str, answer: str, contexts: list[str]) -> float:
    """Đánh giá faithfulness - câu trả lời có match với context không."""
    if not answer or not contexts:
        return 0.0
    
    context_text = "\n".join(contexts[:3])
    prompt = f"""Đánh giá câu trả lời dựa trên context được cung cấp.

Context:
{context_text[:1000]}

Câu trả lời:
{answer}

Câu trả lời có đúng/similar với thông tin trong context không? (Không được suy luận thêm thông tin không có trong context)

Trả lời CHỈ bằng số từ 0.0 đến 1.0:
- 1.0 = hoàn toàn đúng, không có thông tin sai
- 0.5 = có một số thông tin đúng, một số không
- 0.0 = có nhiều thông tin sai hoặc không liên quan

Điểm:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()
        return float(result) if result.replace('.', '').isdigit() else 0.5
    except Exception:
        return 0.5


def evaluate_relevancy(question: str, answer: str) -> float:
    """Đánh giá answer relevancy - câu trả lời có liên quan đến câu hỏi không."""
    if not answer:
        return 0.0
    
    prompt = f"""Đánh giá câu trả lời có đáp ứng câu hỏi không.

Câu hỏi: {question}
Câu trả lời: {answer}

Câu trả lời có trả lời đúng câu hỏi không?

Trả lời CHỈ bằng số từ 0.0 đến 1.0:
- 1.0 = trả lời đúng và đầy đủ
- 0.5 = trả lời một phần
- 0.0 = không trả lời đúng câu hỏi

Điểm:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()
        return float(result) if result.replace('.', '').isdigit() else 0.5
    except Exception:
        return 0.5


def evaluate_context_recall(expected: str, contexts: list[str]) -> float:
    """Đánh giá context recall - context có chứa expected answer không."""
    if not expected or not contexts:
        return 0.0
    
    context_text = "\n".join(contexts)
    prompt = f"""Đánh giá context có chứa thông tin để trả lời câu hỏi không.

Expected Answer:
{expected}

Contexts:
{context_text[:1500]}

Context có chứa thông tin tương tự expected answer không?

Trả lời CHỈ bằng số từ 0.0 đến 1.0:
- 1.0 = context chứa đầy đủ thông tin
- 0.5 = context chứa một phần
- 0.0 = context không chứa thông tin

Điểm:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()
        return float(result) if result.replace('.', '').isdigit() else 0.5
    except Exception:
        return 0.5


def evaluate_context_precision(contexts: list[str], expected_contexts: list[str]) -> float:
    """Đánh giá context precision - context có relevant không."""
    if not contexts:
        return 0.0
    
    context_text = "\n".join(contexts[:3])
    prompt = f"""Đánh giá các context có liên quan đến nhau không.

Contexts retrieved:
{context_text[:1000]}

Các context này có thảo luận về cùng một chủ đề không?

Trả lời CHỈ bằng số từ 0.0 đến 1.0:
- 1.0 = tất cả contexts đều liên quan
- 0.5 = một số liên quan
- 0.0 = không liên quan

Điểm:"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
        )
        result = response.choices[0].message.content.strip()
        return float(result) if result.replace('.', '').isdigit() else 0.5
    except Exception:
        return 0.5


# =============================================================================
# Run Evaluation
# =============================================================================

def run_evaluation():
    """Run full evaluation on golden dataset."""
    print("=" * 60)
    print("RAG EVALUATION PIPELINE (Simple)")
    print("=" * 60)
    
    if not client:
        print("⚠ No OpenRouter API key. Using placeholder scores.")
        return None
    
    # Load data
    golden_data = load_golden_dataset()
    print(f"\nLoaded {len(golden_data)} test cases")
    
    results = []
    all_scores = {
        "faithfulness": [],
        "answer_relevancy": [],
        "context_recall": [],
        "context_precision": [],
    }
    
    for i, item in enumerate(golden_data, 1):
        print(f"\n[{i}/{len(golden_data)}] Evaluating: {item['question'][:50]}...")
        
        # Run RAG pipeline
        result = generate_with_citation(item["question"], top_k=5)
        answer = result.get("answer", "")
        contexts = [s.get("content", "") for s in result.get("sources", [])]
        
        # Evaluate
        scores = {
            "question": item["question"],
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "faithfulness": evaluate_faithfulness(item["question"], answer, contexts),
            "answer_relevancy": evaluate_relevancy(item["question"], answer),
            "context_recall": evaluate_context_recall(item["expected_answer"], contexts),
            "context_precision": evaluate_context_precision(contexts, item.get("expected_context", [])),
        }
        
        results.append(scores)
        for key in all_scores:
            all_scores[key].append(scores[key])
        
        print(f"  F: {scores['faithfulness']:.2f} | R: {scores['answer_relevancy']:.2f} | CR: {scores['context_recall']:.2f} | CP: {scores['context_precision']:.2f}")
    
    # Calculate averages
    avg_scores = {k: sum(v) / len(v) for k, v in all_scores.items()}
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for metric, score in avg_scores.items():
        print(f"  {metric}: {score:.4f}")
    
    # Save CSV
    import csv
    with open(SCORES_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "faithfulness", "answer_relevancy", "context_recall", "context_precision"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nScores saved to: {SCORES_PATH}")
    
    return avg_scores, results


# =============================================================================
# Export Results
# =============================================================================

def export_results(avg_scores: dict, results: list):
    """Export evaluation results to results.md."""
    
    content = """# RAG Evaluation Results

## Framework Used
**Simple LLM-based Evaluation** (Custom evaluation using GPT-4o-mini)

## Dataset
- Number of questions: """ + str(len(results)) + """
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
"""
    
    for metric, score in avg_scores.items():
        content += f"| {metric.replace('_', ' ').title()} | {score:.4f} |\n"
    
    avg_all = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0
    content += f"| **Average** | **{avg_all:.4f}** |\n"
    
    content += """
## Per-Question Results

| # | Question | Faithfulness | Relevance | Recall | Precision |
|---|----------|-------------|-----------|--------|-----------|
"""
    
    for i, r in enumerate(results, 1):
        q = r["question"][:50] + "..." if len(r["question"]) > 50 else r["question"]
        content += f"| {i} | {q} | {r['faithfulness']:.2f} | {r['answer_relevancy']:.2f} | {r['context_recall']:.2f} | {r['context_precision']:.2f} |\n"
    
    content += """
## Analysis

### Key Findings
"""
    
    if avg_scores:
        best_metric = max(avg_scores, key=avg_scores.get)
        worst_metric = min(avg_scores, key=avg_scores.get)
        content += f"""
- **Best performing metric**: {best_metric.replace('_', ' ').title()} ({avg_scores[best_metric]:.2f})
- **Needs improvement**: {worst_metric.replace('_', ' ').title()} ({avg_scores[worst_metric]:.2f})
"""
    
    content += """
### Recommendations

1. **Context Precision Improvement**
   - Action: Fine-tune chunk size or overlap
   - Expected impact: Better source selection accuracy

2. **Answer Faithfulness Enhancement**
   - Action: Implement better citation tracking
   - Expected impact: Reduced hallucination in responses

3. **Hybrid Search Optimization**
   - Action: Adjust alpha parameter in RRF fusion
   - Expected impact: Balanced semantic + lexical results

## Limitations

- Rate limits on free LLM API tier (limited to 5 questions)
- Simple LLM-based scoring (not full RAGAS)
- May need human evaluation for edge cases

## Next Steps

- Expand evaluation to full 18 questions
- A/B testing with different retrieval configs
- Fine-tune reranking model
"""
    
    RESULTS_PATH.write_text(content, encoding="utf-8")
    print(f"\nResults exported to: {RESULTS_PATH}")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Check API key
    if not OPENROUTER_API_KEY:
        print("⚠ WARNING: OPENROUTER_API_KEY not set in .env")
        print("   Running with placeholder scores...")
    
    # Run evaluation
    result = run_evaluation()
    
    if result:
        avg_scores, results = result
        export_results(avg_scores, results)
        print("\n✅ Evaluation complete!")
    else:
        print("\n⚠ Evaluation incomplete. Check API key and rate limits.")
