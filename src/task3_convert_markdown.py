"""
Task 3 - Convert toan bo file trong data/landing/ thanh Markdown.

Su dung pypdf cho PDF, docx2txt cho DOCX, va json cho news articles.
"""

import json
from pathlib import Path 

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _read_pdf(filepath: Path) -> str:
    """Doc noi dung PDF bang pypdf."""
    if PdfReader is None:
        raise ImportError("pypdf not installed. Run: pip install pypdf")
    reader = PdfReader(str(filepath))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _read_docx(filepath: Path) -> str:
    """Doc noi dung DOCX bang zipfile (built-in)."""
    import zipfile
    from xml.etree import ElementTree
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    try:
        with zipfile.ZipFile(str(filepath)) as zf:
            with zf.open("word/document.xml") as f:
                tree = ElementTree.parse(f)
                root = tree.getroot()
                paragraphs = []
                for para in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                    texts = []
                    for node in para.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
                        if node.text:
                            texts.append(node.text)
                    if texts:
                        paragraphs.append("".join(texts))
                return "\n\n".join(paragraphs)
    except Exception:
        return ""


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0

    for filepath in legal_dir.iterdir():
        if not filepath.is_file():
            continue
        if filepath.suffix.lower() not in (".pdf", ".docx", ".doc"):
            continue

        print(f"  Converting: {filepath.name}")
        try:
            if filepath.suffix.lower() == ".pdf":
                text = _read_pdf(filepath)
            elif filepath.suffix.lower() in (".docx", ".doc"):
                text = _read_docx(filepath)
            else:
                continue

            if not text or len(text.strip()) < 50:
                print(f"    [WARN] No text extracted from {filepath.name}")
                continue

            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(text.strip(), encoding="utf-8")
            print(f"    [OK] Saved: {output_path.name}")
            converted += 1
        except Exception as e:
            print(f"    [FAIL] {filepath.name}: {e}")

    if converted == 0:
        print("  [WARN] No files converted. Run Task 1 first.")
    return converted


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0

    for filepath in news_dir.iterdir():
        if not filepath.is_file():
            continue
        if filepath.suffix.lower() != ".json":
            continue

        print(f"  Converting: {filepath.name}")
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))

            title = data.get("title", filepath.stem)
            url = data.get("url", "")
            date_crawled = data.get("date_crawled", "")
            content = data.get("content_markdown", "") or data.get("content", "")

            lines = [
                "---",
                f"title: \"{title}\"",
                f"url: \"{url}\"",
                f"date_crawled: \"{date_crawled}\"",
                "---",
                "",
                f"# {title}",
                "",
                f"**Source:** [{url}]({url})",
                f"**Crawled:** {date_crawled}",
                "",
                "---",
                "",
                content,
            ]

            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"    [OK] Saved: {output_path.name}")
            converted += 1
        except Exception as e:
            print(f"    [FAIL] {filepath.name}: {e}")

    if converted == 0:
        print("  [WARN] No files converted. Run Task 2 first.")
    return converted


def convert_all():
    """Convert toan bo files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    legal_count = convert_legal_docs()

    print("\n--- News Articles ---")
    news_count = convert_news_articles()

    total_md = len(list(OUTPUT_DIR.rglob("*.md")))
    print(f"\n[OK] Done! Output: {OUTPUT_DIR}")
    print(f"  -> Legal: {legal_count} files")
    print(f"  -> News: {news_count} files")
    print(f"  -> Total: {total_md} .md files")


if __name__ == "__main__":
    convert_all()
