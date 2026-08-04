"""
Task 3 - Convert files in data/landing/ to Markdown.

This implementation keeps the dependency surface small:
    - PDF: pypdf only
    - DOCX: Python standard library zip/xml reader
    - JSON: Python standard library json

Output keeps the landing subfolders:
    data/landing/legal/*.pdf|docx -> data/standardized/legal/*.md
    data/landing/news/*.json      -> data/standardized/news/*.md
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - exercised only when env is incomplete.
    PdfReader = None


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
MIN_MARKDOWN_CHARS = 200


@dataclass(frozen=True)
class ConversionResult:
    source: Path
    output: Path
    chars: int


def configure_console() -> None:
    """Make Vietnamese/Unicode logs readable on Windows terminals."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def yaml_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return json.dumps(text, ensure_ascii=False)


def front_matter(**metadata: object) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if value is None or value == "":
            continue
        lines.append(f"{key}: {yaml_escape(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def title_from_stem(stem: str) -> str:
    words = re.sub(r"[-_]+", " ", stem).strip()
    return re.sub(r"\s+", " ", words).title()


def detect_year(text: str) -> str | None:
    match = re.search(r"\b(20[0-9]{2})\b", text)
    return match.group(1) if match else None


def normalize_markdown(text: str) -> str:
    text = repair_mojibake(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def repair_mojibake(text: str) -> str:
    """Repair common UTF-8 text that was decoded as Windows-1252."""
    markers = ("â", "Ã", "Â")
    if not any(marker in text for marker in markers):
        return text

    fixed_lines: list[str] = []
    replacements = {
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "â€¦": "...",
        "Â ": " ",
        "Â": "",
    }

    for line in text.splitlines():
        if any(marker in line for marker in markers):
            try:
                line = line.encode("cp1252").decode("utf-8")
            except UnicodeError:
                for bad, good in replacements.items():
                    line = line.replace(bad, good)
        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def convert_pdf(filepath: Path) -> str:
    if PdfReader is None:
        raise RuntimeError(
            "Missing dependency: pypdf. Install with `.\\.venv\\Scripts\\python.exe -m pip install pypdf`."
        )

    reader = PdfReader(str(filepath))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = normalize_markdown(text)
        if text.strip():
            pages.append(f"## Page {index}\n\n{text}")

    content = "\n\n".join(pages)
    if len(content) < MIN_MARKDOWN_CHARS:
        raise ValueError(f"Extracted text too short from {filepath.name}: {len(content)} chars")
    return content


def iter_docx_paragraphs(filepath: Path) -> Iterable[str]:
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(filepath) as archive:
        xml_bytes = archive.read("word/document.xml")

    root = ET.fromstring(xml_bytes)
    for para in root.findall(".//w:p", namespaces):
        chunks = [node.text or "" for node in para.findall(".//w:t", namespaces)]
        text = "".join(chunks).strip()
        if text:
            yield text


def convert_docx(filepath: Path) -> str:
    paragraphs = list(iter_docx_paragraphs(filepath))
    content = "\n\n".join(paragraphs)
    if len(content) < MIN_MARKDOWN_CHARS:
        raise ValueError(f"Extracted text too short from {filepath.name}: {len(content)} chars")
    return normalize_markdown(content)


def write_markdown(output_path: Path, content: str) -> ConversionResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = normalize_markdown(content)
    output_path.write_text(content, encoding="utf-8")
    return ConversionResult(source=Path(), output=output_path, chars=len(content))


def convert_legal_docs() -> list[ConversionResult]:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[ConversionResult] = []
    for filepath in sorted(legal_dir.iterdir()):
        if filepath.suffix.lower() not in {".pdf", ".docx", ".doc"}:
            continue

        print(f"Converting legal: {filepath.name}")
        if filepath.suffix.lower() == ".pdf":
            body = convert_pdf(filepath)
        else:
            body = convert_docx(filepath)

        title = title_from_stem(filepath.stem)
        year = detect_year(f"{filepath.stem}\n{body[:2000]}")
        content = (
            front_matter(
                title=title,
                source_file=filepath.name,
                source_path=filepath.relative_to(LANDING_DIR).as_posix(),
                document_type="legal",
                year=year,
                converter="pypdf" if filepath.suffix.lower() == ".pdf" else "stdlib-docx",
            )
            + f"# {title}\n\n"
            + body
        )

        output_path = output_dir / f"{filepath.stem}.md"
        write_markdown(output_path, content)
        result = ConversionResult(filepath, output_path, len(content))
        results.append(result)
        print(f"  Saved: {output_path.relative_to(OUTPUT_DIR)} ({result.chars:,} chars)")

    return results


def convert_news_articles() -> list[ConversionResult]:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[ConversionResult] = []
    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() != ".json":
            continue

        print(f"Converting news: {filepath.name}")
        data = json.loads(filepath.read_text(encoding="utf-8"))
        title = data.get("title") or title_from_stem(filepath.stem)
        body = data.get("content_markdown") or ""
        if len(body.strip()) < MIN_MARKDOWN_CHARS:
            raise ValueError(f"News content too short in {filepath.name}: {len(body)} chars")

        content = (
            front_matter(
                title=title,
                source_url=data.get("url"),
                source_file=filepath.name,
                source_path=filepath.relative_to(LANDING_DIR).as_posix(),
                document_type="news",
                published_year=data.get("published_year"),
                date_crawled=data.get("date_crawled"),
                converter=data.get("crawler") or "json-stdlib",
            )
            + f"# {title}\n\n"
            + body
        )

        output_path = output_dir / f"{filepath.stem}.md"
        write_markdown(output_path, content)
        result = ConversionResult(filepath, output_path, len(content))
        results.append(result)
        print(f"  Saved: {output_path.relative_to(OUTPUT_DIR)} ({result.chars:,} chars)")

    return results


def convert_all() -> list[ConversionResult]:
    configure_console()
    print("=" * 50)
    print("Task 3: Convert landing files to Markdown")
    print("=" * 50)

    all_results: list[ConversionResult] = []

    print("\n--- Legal Documents ---")
    all_results.extend(convert_legal_docs())

    print("\n--- News Articles ---")
    all_results.extend(convert_news_articles())

    legal_count = sum(1 for item in all_results if "legal" in item.output.parts)
    news_count = sum(1 for item in all_results if "news" in item.output.parts)
    print("\nDone.")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Converted: {len(all_results)} files ({legal_count} legal, {news_count} news)")

    return all_results


if __name__ == "__main__":
    convert_all()
