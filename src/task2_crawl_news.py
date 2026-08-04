"""
Task 2 — Crawl bài viết/thông báo về dịch vụ đại học.

Output:
    data/landing/news/*.json

Mỗi JSON có các trường: url, title, date_crawled, published_year,
content_markdown và crawler. Script ưu tiên Crawl4AI; nếu package chưa được cài,
script dùng bộ trích xuất HTML tối giản từ Python standard library.
"""

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
REQUEST_TIMEOUT_SECONDS = 180
MIN_CONTENT_LENGTH = 500

ARTICLES = [
    {
        "filename": "rmit-2026-scholarship-announcement.json",
        "url": (
            "https://www.rmit.edu.vn/news/all-news/2026/jan/"
            "rmit-vietnam-announces-record-2026-scholarships-worth-more-than-"
            "200-billion-vnd"
        ),
    },
    {
        "filename": "rmit-library-newbie-101.json",
        "url": (
            "https://www.rmit.edu.vn/students/student-news-and-events/"
            "student-news/2026/newbie-101-unlock-library-power"
        ),
    },
    {
        "filename": "rmit-student-wellbeing-services.json",
        "url": "https://www.rmit.edu.vn/student-life/support-services/wellbeing",
    },
    {
        "filename": "rmit-student-enrolment.json",
        "url": "https://www.rmit.edu.vn/students/my-studies/enrolment",
    },
    {
        "filename": "rmit-international-student-accommodation.json",
        "url": (
            "https://www.rmit.edu.vn/students/my-studies/"
            "international-students/accommodation-for-international-students"
        ),
    },
]


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


class MainContentParser(HTMLParser):
    """Trích xuất title và nội dung có cấu trúc từ main/article của trang HTML."""

    BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}

    def __init__(self, article_mode: bool = False):
        super().__init__(convert_charrefs=True)
        self.article_mode = article_mode
        self.title_parts = []
        self.blocks = []
        self._inside_title = False
        self._skip_depth = 0
        self._content_depth = 0
        self._has_semantic_container = False
        self._current_tag = None
        self._current_parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        css_classes = set(attrs_dict.get("class", "").split())
        if self.article_mode:
            is_content_root = (
                tag == "div"
                and "responsivegrid" in css_classes
                and "aem-GridColumn--default--9" in css_classes
            )
        else:
            is_content_root = (
                tag in {"main", "article"}
                or (tag == "div" and "body-gridcontent" in css_classes)
            )

        if self._content_depth:
            self._content_depth += 1
        elif is_content_root:
            self._content_depth = 1
            self._has_semantic_container = True

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if tag == "title":
            self._inside_title = True
        if self._content_depth and tag in self.BLOCK_TAGS:
            self._flush_block()
            self._current_tag = tag

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            if self._content_depth:
                self._content_depth -= 1
            return
        if tag == "title":
            self._inside_title = False
        if self._content_depth and tag == self._current_tag:
            self._flush_block()
        if self._content_depth:
            if self._content_depth == 1:
                self._flush_block()
            self._content_depth -= 1

    def handle_data(self, data):
        if self._skip_depth:
            return
        if self._inside_title:
            self.title_parts.append(data)
        if self._content_depth and self._current_tag:
            self._current_parts.append(data)

    def _flush_block(self):
        text = _clean_text(" ".join(self._current_parts))
        if text:
            prefix = ""
            if self._current_tag and self._current_tag.startswith("h"):
                prefix = "#" * int(self._current_tag[1]) + " "
            elif self._current_tag == "li":
                prefix = "- "
            self.blocks.append(prefix + text)
        self._current_tag = None
        self._current_parts = []

    @property
    def title(self) -> str:
        return _clean_text(" ".join(self.title_parts)).replace(" - RMIT University", "")

    @property
    def markdown(self) -> str:
        self._flush_block()
        unique_blocks = []
        for block in self.blocks:
            if not unique_blocks or block != unique_blocks[-1]:
                unique_blocks.append(block)
        return "\n\n".join(unique_blocks).strip()


def _crawl_with_stdlib(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "UniversityServicesRAG-Lab/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("Content-Type", "").lower()
        html_bytes = response.read()

    if "html" not in content_type:
        raise ValueError(f"URL không trả về HTML ({content_type or 'unknown'}): {url}")

    html_text = html_bytes.decode("utf-8", errors="replace")
    article_mode = "/news/" in url or "/student-news/" in url
    parser = MainContentParser(article_mode=article_mode)
    parser.feed(html_text)
    content = parser.markdown

    if not parser._has_semantic_container:
        raise ValueError(f"Không tìm thấy thẻ main/article trong trang: {url}")
    if len(content) < MIN_CONTENT_LENGTH:
        raise ValueError(f"Nội dung trích xuất quá ngắn ({len(content)} ký tự): {url}")

    return {
        "title": parser.title or "Unknown",
        "content_markdown": content,
        "crawler": "stdlib-html-parser",
    }


async def crawl_article(url: str) -> dict:
    """Crawl một bài viết và trả về metadata cùng nội dung Markdown."""
    try:
        from crawl4ai import AsyncWebCrawler
    except ImportError:
        extracted = await asyncio.to_thread(_crawl_with_stdlib, url)
    else:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
        if hasattr(result, "success") and not result.success:
            raise RuntimeError(f"Crawl4AI không crawl được {url}: {result.error_message}")

        markdown_result = result.markdown
        content = getattr(markdown_result, "raw_markdown", markdown_result)
        content = str(content).strip()
        if len(content) < MIN_CONTENT_LENGTH:
            raise ValueError(f"Nội dung Crawl4AI quá ngắn ({len(content)} ký tự): {url}")
        extracted = {
            "title": (result.metadata or {}).get("title", "Unknown"),
            "content_markdown": content,
            "crawler": "crawl4ai",
        }

    year_match = re.search(r"/(20\d{2})/", url)
    return {
        "url": url,
        "title": extracted["title"],
        "date_crawled": datetime.now(timezone.utc).astimezone().isoformat(),
        "published_year": int(year_match.group(1)) if year_match else None,
        "content_markdown": extracted["content_markdown"],
        "crawler": extracted["crawler"],
    }


def _is_valid_article(filepath: Path, expected_url: str) -> bool:
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("url") == expected_url
        and bool(data.get("title"))
        and len(data.get("content_markdown", "")) >= MIN_CONTENT_LENGTH
    )


async def crawl_all() -> list[Path]:
    """Crawl toàn bộ bài viết và lưu từng bài thành một file JSON UTF-8."""
    setup_directory()
    pending = []
    outputs = []

    for article in ARTICLES:
        filepath = DATA_DIR / article["filename"]
        outputs.append(filepath)
        if _is_valid_article(filepath, article["url"]):
            print(f"↷ Đã có bài hợp lệ, bỏ qua: {filepath.name}")
        else:
            pending.append((article, filepath))

    if pending:
        results = await asyncio.gather(
            *(crawl_article(article["url"]) for article, _ in pending)
        )
        for (article, filepath), result in zip(pending, results):
            filepath.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(
                f"✓ Đã lưu: {filepath.name} "
                f"({len(result['content_markdown']):,} ký tự, {result['crawler']})"
            )

    return outputs


if __name__ == "__main__":
    files = asyncio.run(crawl_all())
    print(f"\n✓ Task 2 hoàn thành: {len(files)} bài viết hợp lệ tại {DATA_DIR}")
