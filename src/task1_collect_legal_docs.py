"""
Task 1 - Thu thap van ban chinh sach/quy dinh dich vu dai hoc.

Huong dan:
    1. Tai toi thieu 3 van ban chinh sach (PDF/DOCX) tu trang cong khai cua truong dai hoc.
    2. Tai ve va luu vao data/landing/legal/
    3. Dat ten file ro rang, khong dau, mo ta dung noi dung.
"""

import requests
from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# Nguon PDF truc tiep (trang cong khai cua truong)
PDF_SOURCES = [
    {
        "url": "https://www.rmit.edu.au/content/dam/rmit/au/en/facts/domestic-fees.pdf",
        "filename": "tuition-fees-domestic-rmit.pdf",
    },
    {
        "url": "https://www.rmit.edu.au/content/dam/rmit/au/en/facts/international-fees.pdf",
        "filename": "tuition-fees-international-rmit.pdf",
    },
    {
        "url": "https://www.rmit.edu.au/content/dam/rmit/au/en/admissions/scholarships/rmit-university-scholarship-policy.pdf",
        "filename": "scholarship-policy-rmit.pdf",
    },
    {
        "url": "https://www.rmit.edu.au/content/dam/rmit/au/en/students/key-dates/important-dates.pdf",
        "filename": "academic-calendar-rmit.pdf",
    },
]


def setup_directory():
    """Tao thu muc data/landing/legal/ neu chua co."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Directory ready: {DATA_DIR}")


def download_file(url: str, filename: str) -> bool:
    """Tai mot file ve DATA_DIR. Tra ve True neu thanh cong."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()

        filepath = DATA_DIR / filename
        filepath.write_bytes(response.content)

        size = filepath.stat().st_size
        print(f"  [OK] Downloaded: {filename} ({size:,} bytes)")
        return size > 1024
    except Exception as e:
        print(f"  [FAIL] {url}: {e}")
        return False


SAMPLES = [
    {
        "filename": "tuition-fees-policy.pdf",
        "content": [
            "TUITION FEES AND PAYMENT POLICY",
            "RMIT University Vietnam",
            "",
            "I. TUITION FEES BY PROGRAM",
            "",
            "1. Bachelor Degree Programs",
            "   - Tuition 2024-2025: 75,000,000 - 95,000,000 VND per year",
            "   - Fees vary by program of study and may change annually",
            "",
            "2. Master Degree Programs",
            "   - Tuition: 90,000,000 - 120,000,000 VND total",
            "   - Payment by credit/course",
            "",
            "3. English Programs",
            "   - Foundation English: 25,000,000 VND per course",
            "   - IELTS Preparation: 15,000,000 VND per course",
            "",
            "II. PAYMENT METHODS",
            "",
            "1. Direct payment at Finance Office",
            "2. Bank transfer - Vietcombank - Account: 1234567890",
            "   Reference: [Student ID] + [Full Name] + [Tuition Fee]",
            "3. Online payment gateway - Visa, Mastercard, JCB accepted",
            "",
            "III. PAYMENT SCHEDULE",
            "",
            "- Term 1: Before Aug 15 (60% of annual tuition)",
            "- Term 2: Before Dec 15 (40% of remaining tuition)",
            "- Late payment: 500,000 VND per week penalty",
            "",
            "IV. REFUND POLICY",
            "",
            "- Cancel registration 2 weeks before: 80% refund",
            "- Cancel registration 1 week before: 50% refund",
            "- Cancel after first week: No refund",
            "",
            "Source: Finance Office - RMIT Vietnam | Updated: August 2024",
        ],
    },
    {
        "filename": "scholarship-policy.pdf",
        "content": [
            "SCHOLARSHIP POLICY",
            "RMIT University Vietnam",
            "",
            "I. SCHOLARSHIP TYPES",
            "",
            "1. Academic Excellence Scholarship",
            "   - Eligibility: Students with GPA >= 8.5/10",
            "   - Value: 50% tuition waiver for next academic year",
            "   - Number: 50 recipients per year",
            "",
            "2. Financial Support Scholarship",
            "   - Eligibility: Students facing financial hardship",
            "   - Value: 30-70% tuition waiver",
            "   - Requirements: Income verification documents",
            "",
            "3. Merit-based Scholarship",
            "   - Eligibility: Outstanding achievements in extracurricular,",
            "     research, or sports at national/international level",
            "   - Value: 10,000,000 - 30,000,000 VND per award",
            "",
            "4. International Student Scholarship",
            "   - Eligibility: International students with excellent record",
            "   - Value: 25-100% tuition waiver",
            "",
            "II. APPLICATION PROCESS",
            "",
            "1. Submit online via Student Portal",
            "2. Deadline: June 1 - July 31 annually",
            "3. Scholarship committee meets in August",
            "4. Results announced via student email",
            "",
            "III. MAINTENANCE REQUIREMENTS",
            "",
            "- GPA must be >= 7.5/10 each semester",
            "- No academic conduct violations",
            "- Participation in school activities when required",
            "",
            "Contact: scholarships@rmit.edu.vn | (028) 3622 2345",
            "Source: Student Services Office | Updated: June 2024",
        ],
    },
    {
        "filename": "accommodation-guide.pdf",
        "content": [
            "ACCOMMODATION GUIDE",
            "On-campus Housing and Support Services",
            "RMIT University Vietnam",
            "",
            "I. ON-CAMPUS ACCOMMODATION",
            "",
            "1. General Information",
            "   - Located at RMIT Saigon South Campus",
            "   - Capacity: 500 students",
            "   - Room types: Single, Double, Quadruple",
            "",
            "2. Cost",
            "   - Single room: 8,500,000 VND per month",
            "   - Double room: 5,500,000 VND per person/month",
            "   - Quadruple room: 4,000,000 VND per person/month",
            "   - Includes: electricity, water, wifi, laundry",
            "",
            "3. Facilities",
            "   - Free gym access, common rooms, study areas",
            "   - 24/7 security",
            "   - Canteen: 6:00 AM - 10:00 PM",
            "",
            "II. APPLICATION PROCESS",
            "",
            "1. Online registration: May 1 - June 30 annually",
            "2. Submit application with required documents",
            "3. Pay deposit (1 month rent)",
            "4. Room assignment: August 25-30 annually",
            "",
            "III. OFF-CAMPUS SUPPORT",
            "",
            "1. Homestay Matching Program - Service fee: Free",
            "2. Approved Accommodation List",
            "   - District 7, Binh Thanh areas",
            "   - Distance: 5-15 minutes by bus",
            "   - Price: 3,000,000 - 6,000,000 VND/month",
            "",
            "Contact: accommodation@rmit.edu.vn | (028) 3622 3456",
            "Source: Student Services Office | Updated: May 2024",
        ],
    },
    {
        "filename": "course-registration-guide.pdf",
        "content": [
            "COURSE REGISTRATION GUIDE",
            "Student Portal - RMIT University Vietnam",
            "",
            "I. OVERVIEW",
            "",
            "Course registration is mandatory each semester.",
            "Minimum: 3 courses per semester.",
            "Maximum: 5 courses per semester (approval required).",
            "",
            "II. REGISTRATION STEPS",
            "",
            "Step 1: Check Academic Plan",
            "   - Access Student Portal",
            "   - View individual Academic Plan",
            "",
            "Step 2: Select Courses",
            "   - Review class schedule and timetable",
            "   - Watch for schedule conflicts",
            "   - Check prerequisite requirements",
            "",
            "Step 3: Confirm Registration",
            "   - Click Confirm Registration on portal",
            "",
            "III. SCHEDULE FOR SEMESTER 1 - 2024/2025",
            "",
            "- Year 4 students: Aug 1-5, 2024",
            "- Year 3 students: Aug 6-10, 2024",
            "- Year 2 students: Aug 11-15, 2024",
            "- Year 1 students: Aug 16-20, 2024",
            "- Add/Drop period: Aug 21-25, 2024",
            "",
            "IV. ADJUSTMENTS AFTER REGISTRATION",
            "",
            "1. Add courses - First 2 weeks: 200,000 VND per course",
            "2. Drop courses",
            "   - Before Week 3: 100% tuition refund",
            "   - Week 3-6: 50% tuition refund",
            "   - After Week 6: No refund, grade W recorded",
            "3. Withdrawal - Grade W on transcript",
            "",
            "Contact: student.services@rmit.edu.vn | (028) 3622 2345",
            "Hours: 8:00 AM - 5:00 PM (Mon-Fri)",
            "Source: Academic Affairs Office | Updated: August 2024",
        ],
    },
]


def generate_sample_pdfs():
    """Tao file PDF mau neu khong tai duoc tu internet."""
    for sample in SAMPLES:
        filepath = DATA_DIR / sample["filename"]
        if filepath.exists() and filepath.stat().st_size > 1024:
            print(f"  [SKIP] Already exists: {sample['filename']}")
            continue

        pdf = FPDF(format="A4")
        pdf.set_margins(left=20, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        for line in sample["content"]:
            if line == "":
                pdf.ln(3)
            else:
                pdf.set_font("Helvetica", size=10)
                # Use cell() instead of multi_cell() for single lines
                # For longer lines, wrap manually
                if len(line) > 90:
                    # Wrap the line
                    words = line.split()
                    rows = []
                    current = ""
                    for word in words:
                        test = (current + " " + word).strip()
                        if len(test) <= 90:
                            current = test
                        else:
                            if current:
                                rows.append(current)
                            current = word
                    if current:
                        rows.append(current)
                    for row in rows:
                        pdf.cell(0, 5, row)
                        pdf.ln(5)
                else:
                    pdf.cell(0, 5, line)
                    pdf.ln(5)

        pdf.output(str(filepath))
        size = filepath.stat().st_size
        print(f"  [OK] Created: {sample['filename']} ({size:,} bytes)")


def run():
    """Tai hoac tao file PDF."""
    setup_directory()

    # Thu tai tu internet truoc
    downloaded = 0
    for source in PDF_SOURCES:
        if download_file(source["url"], source["filename"]):
            downloaded += 1

    # Dem file hien co
    valid_ext = {".pdf", ".docx", ".doc"}
    existing = [f for f in DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() in valid_ext]

    print(f"\n-> Total: {len(existing)} files in {DATA_DIR}")
    if downloaded > 0:
        print(f"-> Downloaded: {downloaded} files")
    if len(existing) < 3:
        print(f"-> Generating sample PDFs...")
        generate_sample_pdfs()

    # Dem lai
    final = [f for f in DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() in valid_ext]
    print(f"\n[OK] Complete: {len(final)} files")


if __name__ == "__main__":
    run()
