"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API

Lưu ý: API `/retrieval` của PageIndex có thể deprecated, trả kết quả trong
"retrieved_nodes". Luôn print(json.dumps(...)) trước khi viết logic parse
để xác nhận response schema thực tế.
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Cache uploaded doc IDs
_uploaded_docs: dict[str, str] = {}


def _require_api_key():
    """Raise error if API key not set."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError(
            "PAGEINDEX_API_KEY not set. "
            "Add it to .env file. Register at https://pageindex.ai/"
        )
    return PAGEINDEX_API_KEY


def upload_documents():
    """
    Upload toàn bộ markdown documents lên PageIndex.
    Lưu doc_id vào cache để query sau.
    """
    api_key = _require_api_key()

    from pageindex.client import PageIndexClient

    client = PageIndexClient(api_key=api_key)
    uploaded = 0

    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        filename = md_file.name
        print(f"  Uploading: {filename}")

        # Check cache
        if filename in _uploaded_docs:
            print(f"    ⊘ Already uploaded: {filename}")
            uploaded += 1
            continue

        try:
            # PageIndex nhận PDF; convert .md → HTML rồi upload
            html_content = _md_to_html(md_file.read_text(encoding="utf-8"), str(md_file))
            doc_id = client.submit_document(
                file_name=filename + ".html",
                file_content=html_content,
            )
            # doc_id = response.get("doc_id") or response.get("id")
            doc_id = doc_id if isinstance(doc_id, str) else str(doc_id)
            _uploaded_docs[filename] = doc_id
            print(f"    ✓ Uploaded: {filename} → {doc_id}")
            uploaded += 1

        except Exception as e:
            print(f"    ✗ Upload error: {e}")

    print(f"\n  ✓ Total uploaded: {uploaded}")
    return uploaded


def _md_to_html(md_content: str, source_path: str) -> str:
    """Convert simple markdown to HTML for PageIndex."""
    lines = md_content.split("\n")
    html_lines = ['<html><head><meta charset="utf-8"/></head><body>']
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            html_lines.append(f"<h1>{_escape_html(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{_escape_html(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{_escape_html(line[4:])}</h3>")
        elif line.startswith("**") and line.endswith("**"):
            html_lines.append(f"<p><b>{_escape_html(line[2:-2])}</b></p>")
        elif line.startswith("- ") or line.startswith("* "):
            html_lines.append(f"<li>{_escape_html(line[2:])}</li>")
        elif line.startswith("| "):
            html_lines.append(f"<p>{_escape_html(line)}</p>")
        elif line and not line.startswith("---"):
            html_lines.append(f"<p>{_escape_html(line)}</p>")
    html_lines.append("</body></html>")
    return "\n".join(html_lines)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    Dùng làm fallback khi hybrid search không có kết quả tốt.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'   # Đánh dấu nguồn retrieval
        }
    """
    if not PAGEINDEX_API_KEY:
        return []

    if not _uploaded_docs:
        print("  ⚠ Chưa upload documents — đang upload tự động...")
        try:
            upload_documents()
        except Exception as e:
            print(f"  ⚠ Upload thất bại: {e}")
            return []

    from pageindex.client import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    results = []

    # Query all uploaded documents
    for filename, doc_id in list(_uploaded_docs.items())[:3]:
        try:
            retrieval = client.submit_query(doc_id=doc_id, query=query)
            retrieval_id = retrieval if isinstance(retrieval, str) else str(retrieval)

            # Poll for completion
            for _ in range(10):
                time.sleep(1)
                status = client.get_retrieval(retrieval_id)
                if isinstance(status, dict) and status.get("status") == "completed":
                    break

            if isinstance(status, dict):
                nodes = status.get("retrieved_nodes", [])
            else:
                # If get_retrieval returns string, use submit_query result directly
                nodes = []
                # Print raw response for debugging
                # print(json.dumps(status, indent=2))

            for node_idx, node in enumerate(nodes[:top_k]):
                relevant_contents = node.get("relevant_contents", [])
                for group in relevant_contents:
                    for item in group:
                        content = item.get("relevant_content", "")
                        if content and len(content.strip()) > 20:
                            score = 1.0 / (node_idx + 1)  # Rank-based score
                            results.append({
                                "content": content,
                                "score": round(score, 3),
                                "metadata": {
                                    "source": filename,
                                    "section": item.get("section_title", ""),
                                },
                                "source": "pageindex",
                            })
        except Exception as e:
            print(f"  ⚠ PageIndex query error for {filename}: {e}")

    # Sort by score and dedupe by content
    results.sort(key=lambda x: x["score"], reverse=True)
    seen_content = set()
    deduped = []
    for r in results:
        key = r["content"][:100]
        if key not in seen_content:
            seen_content.add(key)
            deduped.append(r)

    return deduped[:top_k]


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong file .env")
        print("  Đăng ký tại: https://pageindex.ai/")
    else:
        print("Uploading documents...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("tuition fee payment methods", top_k=3)
        for r in results:
            print(f"  [{r['score']:.3f}] {r['content'][:80]}...")
