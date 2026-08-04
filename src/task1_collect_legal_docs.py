"""
Task 1 — Thu thập văn bản chính sách/quy định dịch vụ đại học.

Hướng dẫn:
    1. Tìm tối thiểu 3 văn bản chính sách (PDF/DOCX) từ trang công khai của một trường đại học.
    2. Tải về và lưu vào data/landing/legal/
    3. Đặt tên file rõ ràng, không dấu, mô tả đúng nội dung.

Gợi ý nguồn (ví dụ trang công khai RMIT Vietnam — rmit.edu.vn):
    - https://www.rmit.edu.vn/study-at-rmit/tuition-fees
    - https://www.rmit.edu.vn/study-at-rmit/scholarships/...
    - https://www.rmit.edu.vn/students/my-studies/fees-and-payments

Gợi ý văn bản (chủ đề dịch vụ đại học):
    - Học phí & phương thức thanh toán (Tuition Fees)
    - Chính sách học bổng (Scholarship eligibility)
    - Quy định ký túc xá / hỗ trợ chỗ ở (Accommodation Services)
    - Hướng dẫn đăng ký học phần qua cổng thông tin sinh viên (Course Registration)

Lưu ý: một số trang trường (vd VinUni, Fulbright) chặn bot crawler mặc định (HTTP 403) —
không phải lỗi của bạn, đó là cấu hình WAF/Cloudflare phía server. Đổi sang trang khác
thay vì cố vượt qua, và chỉ dùng nguồn công khai/được phép chia sẻ.
"""

import sys
from pathlib import Path
from urllib.request import Request, urlopen

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_DOCUMENTS = [
    {
        "filename": "student-fees-and-charges-guide-rmit-2026.pdf",
        "topic": "Tuition fees, charges, payment and refund policies",
        "url": (
            "https://www.rmit.edu.vn/assets/vn/en/assets-for-production/documents/"
            "pdfs/study-at-rmit/tuition-fees/"
            "student-fees-and-charges-guide-06-2026.pdf"
        ),
    },
    {
        "filename": "scholarship-terms-and-conditions-rmit.pdf",
        "topic": "Scholarship terms and conditions",
        "url": (
            "https://www.rmit.edu.vn/content/dam/rmit/vn/en/assets-for-production/"
            "documents/pdfs/study-at-rmit/scholarships/english-pdf/"
            "rmit-university-vietnam-scholarship-terms-and-conditions.pdf"
        ),
    },
    {
        "filename": "accommodation-advice-international-students-rmit.pdf",
        "topic": "Accommodation rights, responsibilities and rental advice",
        "url": (
            "https://www.rmit.edu.vn/content/dam/rmit/vn/en/assets-for-production/"
            "documents/pdfs/students/accommodation/"
            "accommodation-advice-for-international-students-in-vietnam.pdf"
        ),
    },
]

REQUEST_TIMEOUT_SECONDS = 180
MIN_PDF_SIZE_BYTES = 10_000


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


def is_valid_pdf(content: bytes) -> bool:
    """Kiểm tra sơ bộ để tránh lưu trang HTML báo lỗi dưới đuôi .pdf."""
    return len(content) >= MIN_PDF_SIZE_BYTES and content.startswith(b"%PDF-")


def download_file(document: dict) -> Path:
    """Tải và xác thực một PDF công khai từ website chính thức của RMIT."""
    output_path = DATA_DIR / document["filename"]

    if output_path.exists() and is_valid_pdf(output_path.read_bytes()):
        print(f"↷ Đã có file hợp lệ, bỏ qua: {output_path.name}")
        return output_path

    request = Request(
        document["url"],
        headers={"User-Agent": "UniversityServicesRAG-Lab/1.0"},
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("Content-Type", "").lower()
        content = response.read()

    if "pdf" not in content_type:
        raise ValueError(
            f"URL không trả về PDF ({content_type or 'unknown'}): {document['url']}"
        )
    if not is_valid_pdf(content):
        raise ValueError(
            f"Nội dung PDF không hợp lệ hoặc quá nhỏ: {document['filename']}"
        )

    output_path.write_bytes(content)
    print(
        f"✓ Đã tải: {output_path.name} "
        f"({len(content) / 1024:.1f} KiB)"
    )
    return output_path


def download_all() -> list[Path]:
    """Tải toàn bộ bộ tài liệu chính sách dùng cho Task 1."""
    setup_directory()
    downloaded = []
    for index, document in enumerate(LEGAL_DOCUMENTS, 1):
        print(f"[{index}/{len(LEGAL_DOCUMENTS)}] {document['topic']}")
        downloaded.append(download_file(document))
    return downloaded


if __name__ == "__main__":
    files = download_all()
    print(f"\n✓ Task 1 hoàn thành: {len(files)} tài liệu hợp lệ tại {DATA_DIR}")
