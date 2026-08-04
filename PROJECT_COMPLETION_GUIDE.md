# Huong dan hoan thanh University Services RAG tu A den Z

Tai lieu nay huong dan cach tu hoan thanh project theo dung thu tu phu thuoc. Muc tieu
khong phai chi lam cho test pass, ma la tao duoc mot pipeline RAG co du lieu that, truy
xuat duoc nguon, sinh cau tra loi co citation va danh gia duoc chat luong.

> Nguyen tac quan trong: hoan thanh va kiem tra tung tang truoc khi sang tang tiep theo.
> Neu Task 4 chua index duoc du lieu thi khong nen sua Task 9 hay Task 10.

## 1. Hieu kien truc truoc khi lam

Project co hai pipeline rieng:

### 1.1. Offline pipeline: chuan bi kho tri thuc

```text
PDF/DOCX chinh sach ----> data/landing/legal/
Website/tin tuc --------> data/landing/news/
                               |
                               v
                     Convert thanh Markdown
                               |
                               v
                      data/standardized/
                               |
                               v
                Chunking + embedding + indexing
                         |             |
                         v             v
                      ChromaDB      BM25 corpus
```

Pipeline nay chay khi khoi tao project hoac khi du lieu thay doi. Khong nen chay lai
embedding va indexing cho moi cau hoi cua nguoi dung.

### 1.2. Online pipeline: tra loi cau hoi

```text
User query
   |----------------------|
   v                      v
Semantic search       BM25 search
   |                      |
   |---------- RRF -------|
               |
               v
       Kiem tra cosine goc
          |           |
       du tot       qua thap
          |           |
          |           v
          |      PageIndex fallback
          |           |
          |-----------|
               |
               v
        Reorder context
               |
               v
       LLM + citation prompt
               |
               v
          Streamlit UI
```

## 2. Thu tu lam viec de khong bi roi

Lam theo thu tu sau:

1. Cai moi truong va kiem tra import.
2. Task 1: thu thap it nhat 3 tai lieu chinh sach.
3. Task 2: crawl it nhat 5 bai viet.
4. Task 3: convert tat ca thanh Markdown.
5. Task 4: chunk, embed va index vao ChromaDB.
6. Task 5: semantic search.
7. Task 6: BM25 search.
8. Task 7: RRF fusion va, neu can, reranking that su.
9. Task 9: ghep retrieval pipeline va fallback.
10. Task 10: sinh cau tra loi co citation.
11. Task 8: hoan thien PageIndex va noi vao fallback.
12. Hoan thien Streamlit UI.
13. Tao golden dataset, chay evaluation va viet bao cao.

Task 8 duoc lam sau Task 10 trong thu tu thuc hanh vi PageIndex la dich vu ben ngoai.
Hybrid retrieval can chay on dinh truoc khi them fallback.

## 3. Setup moi truong bang uv

Project nen dung Python 3.11 de tranh xung dot giua cac thu vien AI.

### 3.1. Cai uv tren PowerShell

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Dong va mo lai terminal, sau do kiem tra:

```powershell
uv --version
```

### 3.2. Tao virtual environment

Dung PowerShell tai thu muc goc project:

```powershell
uv python install 3.11
uv venv .venv --python 3.11
.\.venv\Scripts\Activate.ps1
```

Neu PowerShell chan activation script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Mo lai PowerShell, vao project va activate lai.

Kiem tra Python dang dung:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

Duong dan phai tro vao `.venv` cua project.

### 3.3. Cai dependencies

```powershell
uv pip install -r requirements.txt
uv run playwright install chromium
```

Lenh thu hai cai Chromium cho Crawl4AI. Chi cai package Python la chua du.

Kiem tra cac package quan trong:

```powershell
python -c "import chromadb, sentence_transformers, streamlit, pytest; print('Imports OK')"
```

### 3.4. Tao file `.env`

Khong commit API key len Git. File `.env` toi thieu nen co:

```dotenv
OPENROUTER_API_KEY=your_openrouter_key
PAGEINDEX_API_KEY=your_pageindex_key
```

Cap nhat `.env.example` bang cung ten bien nhung de gia tri rong:

```dotenv
OPENROUTER_API_KEY=
PAGEINDEX_API_KEY=
```

Kiem tra `.gitignore` phai co:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
chroma_db/
```

Khong in gia tri API key ra terminal, log hay giao dien Streamlit.

## 4. Task 1 - Thu thap tai lieu chinh sach

File can lam: `src/task1_collect_legal_docs.py`.

### 4.1. Dau ra bat buoc

Can it nhat 3 file PDF/DOCX that trong:

```text
data/landing/legal/
```

Vi du chu de:

- Hoc phi va thanh toan.
- Dieu kien hoc bong.
- Ho tro cho o hoac ky tuc xa.
- Dang ky hoc phan.

### 4.2. Cach lam

Co hai cach hop le:

- Tai thu cong tai lieu tu website chinh thuc va dat vao dung thu muc.
- Viet ham download bang `requests` neu URL tro truc tiep den file.

Neu viet ham download, can:

1. Goi `requests.get(url, timeout=30)`.
2. Goi `raise_for_status()` de bat HTTP 404/403/500.
3. Kiem tra `Content-Type` hoac phan mo rong file.
4. Ghi bang `Path.write_bytes()`.
5. Khong luu trang HTML bao loi thanh file `.pdf`.

Nen dat ten khong dau va co y nghia, vi du:

```text
tuition-fees-rmit.pdf
academic-scholarship-rmit.pdf
student-accommodation-rmit.pdf
```

### 4.3. Tu kiem tra

```powershell
Get-ChildItem data\landing\legal
```

Moi file phai mo duoc va co noi dung that. File vai tram byte thuong la trang bao loi.

### 4.4. Bao cao Task 1 da thuc hien

**Trang thai:** Hoan thanh ngay 04/08/2026.

Script `src/task1_collect_legal_docs.py` da duoc implement de:

- Tao thu muc dau ra neu chua ton tai.
- Tai ba tai lieu tu website chinh thuc cua RMIT Vietnam.
- Theo redirect va dat timeout 180 giay cho CDN.
- Kiem tra HTTP response phai la PDF.
- Kiem tra file bat dau bang magic bytes `%PDF-`.
- Tu choi file nho hon 10.000 bytes de tranh luu trang HTML bao loi.
- Bo qua file da ton tai neu file van hop le, khong tai trung moi lan chay.
- Cau hinh console UTF-8 de chay duoc tren PowerShell Windows.

Ket qua trong `data/landing/legal/`:

| Tai lieu | Chu de | Kich thuoc | Magic | Trang thai |
|---|---|---:|---|---|
| `student-fees-and-charges-guide-rmit-2026.pdf` | Hoc phi, phi phu thu, thanh toan va hoan phi | 886.921 bytes | `%PDF-` | Hop le |
| `scholarship-terms-and-conditions-rmit.pdf` | Dieu khoan va dieu kien hoc bong | 558.608 bytes | `%PDF-` | Hop le |
| `accommodation-advice-international-students-rmit.pdf` | Quyen, trach nhiem va loi khuyen thue nha | 1.466.649 bytes | `%PDF-` | Hop le |

Nguon tai lieu chinh thuc:

1. [2026 Student Fees and Charges Guide](https://www.rmit.edu.vn/assets/vn/en/assets-for-production/documents/pdfs/study-at-rmit/tuition-fees/student-fees-and-charges-guide-06-2026.pdf) - tai lieu song ngu, khoang 60 trang.
2. [RMIT University Vietnam Scholarship Terms and Conditions](https://www.rmit.edu.vn/content/dam/rmit/vn/en/assets-for-production/documents/pdfs/study-at-rmit/scholarships/english-pdf/rmit-university-vietnam-scholarship-terms-and-conditions.pdf) - khoang 6 trang.
3. [Accommodation Advice for International Students in Vietnam](https://www.rmit.edu.vn/content/dam/rmit/vn/en/assets-for-production/documents/pdfs/students/accommodation/accommodation-advice-for-international-students-in-vietnam.pdf) - 7 trang.

SHA-256 de doi chieu file da tai:

```text
e77ef293e02e217326056f490b2a5a712341fabc97f5ed5fb83c49eac65c393b  student-fees-and-charges-guide-rmit-2026.pdf
fa1fb3c8b930c16b741aec545a3ed02621041d64099ad8ad29080d4dbd6fdf1d  scholarship-terms-and-conditions-rmit.pdf
6af78ee4c56146ccbbf42d224385f5afea90b6a4440ef481a5ea4c546b2ae958  accommodation-advice-international-students-rmit.pdf
```

Lenh da dung de xac nhan script co the chay lai an toan:

```powershell
python -m src.task1_collect_legal_docs
```

Ket qua lan chay lai: script nhan dien ca ba file da hop le, bo qua viec tai lai va bao
`Task 1 hoan thanh: 3 tai lieu hop le`.

## 5. Task 2 - Crawl bai viet va thong bao

File can lam: `src/task2_crawl_news.py`.

### 5.1. Dau ra bat buoc

It nhat 5 file JSON trong:

```text
data/landing/news/
```

Moi file nen co schema thong nhat:

```json
{
  "url": "https://example.edu/article",
  "title": "Article title",
  "date_crawled": "2026-08-04T10:30:00+07:00",
  "published_year": 2026,
  "content_markdown": "# Noi dung..."
}
```

`published_year` rat huu ich cho citation o Task 10. Neu khong tim duoc nam xuat ban,
co the de `null`; khong tu bia nam.

### 5.2. Cac buoc implement

1. Dien it nhat 5 URL cong khai vao `ARTICLE_URLS`.
2. Mo `AsyncWebCrawler` bang `async with`.
3. Goi `crawler.arun(url=url)`.
4. Kiem tra crawl co thanh cong va Markdown khong rong.
5. Lay title tu metadata; neu thieu thi dung URL hoac ten ro rang.
6. Tra ve dict dung schema.
7. Luu JSON bang UTF-8.

Khi ghi file, dung ro encoding:

```python
filepath.write_text(
    json.dumps(article, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
```

### 5.3. Loi thuong gap

- `Executable doesn't exist`: chua chay `uv run playwright install chromium`.
- HTTP 403: website chan crawler; chon nguon cong khai khac, khong co vuot bao mat.
- Content rong: trang render JavaScript, cookie banner hoac selector khong dung.
- Tieng Viet bi loi: thieu `encoding="utf-8"`.

### 5.4. Tu kiem tra

```powershell
python -m src.task2_crawl_news
Get-ChildItem data\landing\news
```

Mo tung JSON va dam bao `content_markdown` la noi dung bai viet, khong phai menu/footer.

### 5.5. Bao cao Task 2 da thuc hien

**Trang thai:** Hoan thanh ngay 04/08/2026.

Script `src/task2_crawl_news.py` da duoc implement voi cac kha nang:

- Quan ly danh sach 5 URL va ten file dau ra on dinh.
- Uu tien `AsyncWebCrawler` cua Crawl4AI khi package san sang.
- Tu dong fallback sang parser HTML cua Python standard library khi chua cai Crawl4AI.
- Chi trich noi dung trong container semantic cua trang RMIT (`main`, `article` hoac
  `body-gridcontent`), tranh lay toan bo navigation va footer.
- Chuyen heading, paragraph va list item thanh Markdown co cau truc.
- Loai bo khoang trang thua va block trung lien tiep.
- Validate response la HTML va noi dung sau trich xuat co it nhat 500 ky tu.
- Luu JSON UTF-8 voi title, URL, thoi diem crawl, nam xuat ban, noi dung va crawler.
- Crawl cac trang chua co du lieu theo kieu bat dong bo.
- Bo qua JSON da ton tai neu URL, title va content van hop le.

Moi file co schema:

```json
{
  "url": "https://www.rmit.edu.vn/...",
  "title": "Article title",
  "date_crawled": "2026-08-04T...+07:00",
  "published_year": 2026,
  "content_markdown": "# Noi dung...",
  "crawler": "stdlib-html-parser"
}
```

Ket qua trong `data/landing/news/`:

| File | Chu de | Content | File size | Nam | Trang thai |
|---|---|---:|---:|---:|---|
| `rmit-2026-scholarship-announcement.json` | Thong bao hoc bong RMIT 2026 | 3.189 ky tu | 3.612 bytes | 2026 | Hop le |
| `rmit-library-newbie-101.json` | Dich vu va tai nguyen thu vien | 10.934 ky tu | 11.487 bytes | 2026 | Hop le |
| `rmit-student-wellbeing-services.json` | Wellbeing va ho tro sinh vien | 7.903 ky tu | 8.476 bytes | Khong xac dinh | Hop le |
| `rmit-student-enrolment.json` | Dang ky hoc phan va quan ly enrolment | 2.392 ky tu | 2.771 bytes | Khong xac dinh | Hop le |
| `rmit-international-student-accommodation.json` | Cho o cho sinh vien quoc te | 3.614 ky tu | 4.013 bytes | Khong xac dinh | Hop le |

`published_year` duoc de `null` voi trang dich vu khong cong bo nam, thay vi tu suy dien
hoac bia nam cho citation.

Nguon chinh thuc:

1. [RMIT Vietnam announces record 2026 scholarships](https://www.rmit.edu.vn/news/all-news/2026/jan/rmit-vietnam-announces-record-2026-scholarships-worth-more-than-200-billion-vnd).
2. [Newbie 101: Unlock Library Power](https://www.rmit.edu.vn/students/student-news-and-events/student-news/2026/newbie-101-unlock-library-power).
3. [RMIT Student Wellbeing](https://www.rmit.edu.vn/student-life/support-services/wellbeing).
4. [RMIT Student Enrolment](https://www.rmit.edu.vn/students/my-studies/enrolment).
5. [Accommodation for international students](https://www.rmit.edu.vn/students/my-studies/international-students/accommodation-for-international-students).

SHA-256 cua cac JSON da tao:

```text
afdcee553edf49a584ce63db2fa8e7f440baf3732dcf3660015d7930f2eda7cb  rmit-2026-scholarship-announcement.json
b0b3bf577d16efc6c9c26afe264c2e8f6635a6fc0d380110448a71520fa49e3e  rmit-library-newbie-101.json
a3bf146e0070b1289e443dd1bd02ad045b6e336120a79c6743d59677e002d89e  rmit-student-wellbeing-services.json
dc5a3fd6495d12be1ac8a7b03a28f422c653d27ba0c8f5d8e69904d878c101ac  rmit-student-enrolment.json
8ea6c1061e4b7570df78bbc0776bfe4f915938074af0aba0156883cbee919656  rmit-international-student-accommodation.json
```

Kiem chung:

- Chay lai `python -m src.task2_crawl_news`: ca 5 file duoc nhan dien hop le va bo qua.
- Chay `python -m unittest tests.test_individual.TestTask2 -v`: **4/4 test pass**.
- `python -m py_compile src/task2_crawl_news.py`: thanh cong.

Luu y: moi truong Python hien tai chua cai `crawl4ai`, nen bo du lieu tren duoc tao boi
fallback `stdlib-html-parser`. Sau khi cai requirements va Chromium, script se uu tien
Crawl4AI khi can crawl lai tu dau.

## 6. Task 3 - Chuan hoa thanh Markdown

File can lam: `src/task3_convert_markdown.py`.

### 6.1. Muc tieu

Chuyen:

```text
data/landing/legal/*.pdf|docx -> data/standardized/legal/*.md
data/landing/news/*.json      -> data/standardized/news/*.md
```

### 6.2. Convert legal documents

Trong `convert_legal_docs()`:

1. Duyet file PDF/DOCX.
2. Dung `pypdf.PdfReader` de extract text PDF nhe hon MarkItDown.
3. Voi DOCX, doc `word/document.xml` bang `zipfile` va `xml.etree`.
4. Loai bo output rong hoac qua ngan.
5. Luu UTF-8 voi cung stem.

Nen them metadata header vao dau Markdown:

```markdown
---
source: tuition-fees-rmit.pdf
type: legal
year: 2026
---
```

Nam phai lay tu tai lieu neu co, khong doan.

### 6.3. Convert news JSON

Trong `convert_news_articles()`:

1. Doc JSON bang UTF-8.
2. Validate `url`, `title`, `content_markdown`.
3. Tao YAML front matter gom source URL, title, type va year.
4. Noi header voi content.
5. Luu thanh `.md`.

### 6.4. Xu ly loi

Khong nen dung `raise NotImplementedError` ben trong vong lap sau khi implement. Neu mot
file loi, ghi ro ten file. Trong giai doan debug co the cho dung ngay; khi pipeline on
dinh, nen tong hop danh sach file loi de cac file tot van duoc convert.

### 6.5. Tu kiem tra

```powershell
python -m src.task3_convert_markdown
Get-ChildItem data\standardized -Recurse -Filter *.md
```

Mo thu 2 file legal va 2 file news. Kiem tra heading, Unicode, URL va noi dung khong bi
lap menu/footer qua nhieu.

### 6.6. Bao cao dau ra Task 3

Trang thai: **hoan thanh**.

Da implement:

- `src/task3_convert_markdown.py` khong con `NotImplementedError`.
- Dung dependency nhe `pypdf` de convert PDF, khong dung `markitdown[pdf]`.
- JSON news duoc convert bang Python standard library.
- Moi file Markdown co YAML front matter gom title, source, path, type, nam neu xac dinh duoc va converter.
- Co buoc repair mojibake cho cac ky tu UTF-8 bi doc sai dang `â€™`, `â€œ`.

Output da tao:

| Nhom | File | Kich thuoc noi dung |
| --- | --- | ---: |
| legal | `data/standardized/legal/accommodation-advice-international-students-rmit.md` | 5,894 chars |
| legal | `data/standardized/legal/scholarship-terms-and-conditions-rmit.md` | 8,915 chars |
| legal | `data/standardized/legal/student-fees-and-charges-guide-rmit-2026.md` | 174,411 chars |
| news | `data/standardized/news/rmit-2026-scholarship-announcement.md` | 3,752 chars |
| news | `data/standardized/news/rmit-international-student-accommodation.md` | 4,069 chars |
| news | `data/standardized/news/rmit-library-newbie-101.md` | 11,361 chars |
| news | `data/standardized/news/rmit-student-enrolment.md` | 2,695 chars |
| news | `data/standardized/news/rmit-student-wellbeing-services.md` | 8,234 chars |

Ket qua test:

```text
python -m unittest tests.test_individual.TestTask3 -v
Ran 4 tests in 0.025s
OK
```

Kiem tra lien thong Task 1-3:

```text
python -m unittest tests.test_individual.TestTask1 tests.test_individual.TestTask2 tests.test_individual.TestTask3 -v
Ran 11 tests
OK
```

## 7. Task 4 - Chunking, embedding va ChromaDB

File can lam: `src/task4_chunking_indexing.py`.

### 7.1. Chot mot cau hinh duy nhat

Tai lieu dang mau thuan giua `800/100` va `500/50`. Nen chon mot cau hinh, ghi ro ly do
va dung thong nhat. Cau hinh khoi dau de danh gia:

```python
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
```

Sau nay co the A/B test `500/50` voi `800/100`, khong nen thay doi tuy y giua cac file.

### 7.2. Implement `load_documents()`

1. Duyet `STANDARDIZED_DIR.rglob("*.md")`.
2. Doc UTF-8.
3. Bo qua file rong.
4. Lay metadata tu front matter hoac duong dan.
5. Dung duong dan tuong doi lam `source`, khong chi dung filename.

Mot document nen co dang:

```python
{
    "content": "...",
    "metadata": {
        "source": "legal/tuition-fees-rmit.md",
        "type": "legal",
        "year": 2026,
    },
}
```

### 7.3. Implement `chunk_documents()`

Dung `RecursiveCharacterTextSplitter` voi separators uu tien doan va dong:

```python
["\n\n", "\n", ". ", " ", ""]
```

Moi chunk can metadata:

```python
{
    "source": "legal/tuition-fees-rmit.md",
    "type": "legal",
    "year": 2026,
    "chunk_index": 0,
    "chunk_id": "legal/tuition-fees-rmit.md::0"
}
```

`chunk_id` phai on dinh va duy nhat. Khong dung moi filename vi legal/news co the trung
ten.

### 7.4. Implement embedding

1. Tao `SentenceTransformer(EMBEDDING_MODEL)` mot lan.
2. Lay tat ca chunk text.
3. Encode theo batch, bat progress bar khi chay CLI.
4. Dung `normalize_embeddings=True` de score cosine de hieu va on dinh hon.
5. Chuyen NumPy array thanh list truoc khi dua vao Chroma.

Nen tao helper co cache:

```python
def get_embedding_model(): ...
def get_collection(): ...
```

Task 5 se tai su dung dung hai helper nay, tranh load model moi lan.

### 7.5. Implement Chroma indexing

1. Tao `PersistentClient(path=str(CHROMA_DIR))`.
2. Tao collection voi `hnsw:space = cosine`.
3. Dung `chunk_id` lam Chroma ID.
4. `upsert` documents, embeddings va metadatas.
5. In `collection.count()` sau khi index.

Khi thay doi embedding model, chunk size hoac corpus, xoa `chroma_db/` cu va index lai:

```powershell
Remove-Item -Recurse -Force .\chroma_db
python -m src.task4_chunking_indexing
```

Chi xoa dung thu muc `chroma_db` trong project.

### 7.6. Tu kiem tra

```powershell
python -m src.task4_chunking_indexing
```

Dieu kien dat:

- Loaded document count > 0.
- Chunk count lon hon hoac bang document count.
- Moi chunk khong vuot qua size qua nhieu.
- Embedding moi chunk co 1024 phan tu.
- Chroma collection count bang so chunk mong doi.

## 8. Task 5 - Semantic search

File can lam: `src/task5_semantic_search.py`.

### 8.1. Luong xu ly

```text
query -> BAAI/bge-m3 -> query vector -> Chroma cosine query -> top_k chunks
```

### 8.2. Cac buoc implement

1. Validate query khong rong va `top_k > 0`.
2. Lay model tu `get_embedding_model()` cua Task 4.
3. Embed query voi cung model va cung normalize setting.
4. Lay collection tu `get_collection()`.
5. Query `documents`, `metadatas`, `distances`.
6. Chuyen cosine distance thanh similarity bang `1 - distance`.
7. Sort giam dan va cat `top_k`.

Output phai dung contract:

```python
{
    "content": "...",
    "score": 0.72,
    "metadata": {...}
}
```

Khong thay score semantic bang RRF score; Task 9 can cosine goc de quyet dinh fallback.

### 8.3. Tu kiem tra

Thu ba loai query:

- Lien quan ro: `hoc phi RMIT thanh toan theo hoc ky`.
- Dung keyword khac tai lieu nhung cung y nghia.
- Lac de: `cach nau pho bo tai nha`.

Ghi lai top score de phuc vu calibrate threshold o Task 9.

## 9. Task 6 - BM25 lexical search

File can lam: `src/task6_lexical_search.py`.

### 9.1. Corpus phai giong semantic corpus

BM25 nen tim tren cung cac chunk da dua vao Chroma. Co hai cach:

- Goi lai `load_documents()` va `chunk_documents()`.
- Doc documents va metadata tu Chroma collection.

Cach thu hai tranh hai ben bi lech chunk, nhung can giu thu tu corpus on dinh.

### 9.2. Tokenization

Ban dau co the dung tokenizer don gian:

1. Lowercase.
2. Chuan hoa dau cau thanh space.
3. Tach token.
4. Bo token rong.

`split()` thuan tuy van chay, nhung yeu voi tu ghep tieng Viet. Neu can cai thien sau khi
co baseline, co the dung mot Vietnamese tokenizer va ap dung dung cung ham cho corpus va
query.

### 9.3. Xay index mot lan

Khong khoi tao BM25 lai cho moi query. Nen co bien cache hoac helper lazy loading:

```python
_bm25 = None
_corpus = None
```

Lan dau search moi load corpus va build index; cac lan sau tai su dung.

### 9.4. Output

Tra ve cung contract voi semantic search. Chi lay item co BM25 score > 0 va sort giam
dan.

### 9.5. Tu kiem tra

Thu query co keyword dac biet nhu ten hoc bong, ma chuong trinh, con so hoac ten cong
thong tin. Ket qua chua keyword chinh xac phai co score cao.

## 10. Task 7 - RRF fusion va reranking

File can lam: `src/task7_reranking.py`.

### 10.1. Phan biet hai khai niem

- RRF la fusion: gop hai danh sach ranked result.
- Cross-encoder/MMR la reranking: cham lai candidates sau retrieval.

Khong goi RRF hai lan.

### 10.2. Implement `rerank_rrf()`

Voi moi item o rank bat dau tu 1:

```text
rrf_score += 1 / (60 + rank)
```

Dung `metadata.chunk_id` lam khoa gop. Chi fallback sang content lam khoa neu du lieu cu
chua co chunk ID. Dung content co the gop nham hai chunk trung noi dung.

Ket qua can giu metadata va gan:

```python
item["score"] = rrf_score
item["retrieval_scores"] = {
    "semantic": original_semantic_score,
    "bm25": original_bm25_score,
}
```

### 10.3. Xu ly interface `rerank()` hien tai

Test hien tai goi `rerank()` voi mot flat list, trong khi RRF dung dung can nhieu ranked
lists. De interface khong vo:

- `rerank_rrf([dense_results, sparse_results])` dung cho fusion o Task 9.
- `rerank(query, candidates, method="cross_encoder")` dung neu co cross-encoder.
- Neu `method="rrf"` nhan mot flat list, co the coi day la mot ranked list va tra lai
  thu tu theo RRF, nhung buoc nay khong cai thien relevance.

Ban baseline khong bat buoc cross-encoder. RRF fusion la du de hoan thanh pipeline co
the chay local.

### 10.4. Khong dung RRF score de fallback

RRF score thuong xap xi `0.016`, khong bieu dien do lien quan tuyet doi. Task 9 phai
kiem tra `dense_results[0]["score"]`, khong kiem tra fused score.

## 11. Task 9 - Retrieval pipeline hoan chinh

File can lam: `src/task9_retrieval_pipeline.py`.

### 11.1. Baseline nen implement

1. Validate query va tham so.
2. Lay `top_k * 2` semantic candidates.
3. Lay `top_k * 2` BM25 candidates.
4. Luu `best_dense_score` truoc khi fusion.
5. Fusion hai list bang `rerank_rrf()`.
6. Gan `source="hybrid"`.
7. Neu co cross-encoder thi rerank fused candidates mot lan.
8. Neu `best_dense_score < threshold`, thu PageIndex.
9. Neu PageIndex co ket qua thi tra PageIndex.
10. Neu PageIndex khong san sang, tra hybrid neu con ket qua; generation se quyet dinh
    context co du evidence hay khong.

Pseudo-flow:

```python
dense = semantic_search(query, top_k=top_k * 2)
sparse = lexical_search(query, top_k=top_k * 2)
best_dense_score = dense[0]["score"] if dense else 0.0
merged = rerank_rrf([dense, sparse], top_k=top_k)

if best_dense_score < score_threshold:
    fallback = pageindex_search(query, top_k=top_k)
    if fallback:
        return fallback

return merged[:top_k]
```

### 11.2. Calibrate threshold, khong copy may moc

Tai lieu noi `0.48`, code dang de `0.3`. Khong co gia tri nao dung cho moi corpus.

Tao khoang 10 query lien quan va 10 query lac de, ghi top cosine vao bang:

```text
query | label | top_cosine
```

Chon threshold nam giua hai nhom. Neu diem hai nhom chong lan nhieu, can cai thien data,
chunking hoac embedding thay vi chi thay threshold.

### 11.3. Song song hoa la toi uu sau

Tai lieu noi semantic va BM25 chay song song, nhung baseline co the chay tuan tu de de
debug. Khi pipeline dung roi moi dung thread pool. Khong nen song song luc model/index
con bi khoi tao lai moi request.

## 12. Task 8 - PageIndex vectorless fallback

File can lam: `src/task8_pageindex_vectorless.py`.

### 12.1. Muc dich

PageIndex khong thay the hybrid retrieval. No la fallback cho query can cau truc tai
lieu rong hon hoac khi Chroma khong co chunk du lien quan.

### 12.2. Upload documents

1. Kiem tra `PAGEINDEX_API_KEY`; neu thieu thi bao loi cau hinh ro rang.
2. Xac nhan format ma SDK hien tai ho tro.
3. Neu chi nhan PDF, convert Markdown sang PDF tam hoac upload PDF goc.
4. Upload tung tai lieu.
5. Luu mapping `source -> doc_id` vao file local, vi du
   `pageindex_documents.json`.
6. Khong upload lai moi khi nguoi dung gui query.

Khong viet `doc_id` cung trong code. Khi corpus thay doi, cap nhat mapping.

### 12.3. Query va parse response

PageIndex API co the thay doi schema. In response da an thong tin nhay cam trong luc
debug, sau do parse dung schema that. Theo ghi chu hien tai, can xem:

```text
retrieved_nodes -> relevant_contents -> relevant_content
```

PageIndex co the khong tra relevance score. Co the gan score theo rank, nhung phai danh
dau ro day la score noi bo, khong so sanh no voi cosine.

Moi result can co:

```python
{
    "content": "...",
    "score": 1.0,
    "metadata": {"source": "...", "section": "..."},
    "source": "pageindex",
}
```

### 12.4. Xu ly dich vu ngoai

Phan biet:

- Thieu API key: configuration error.
- 401/403: key sai hoac thieu quyen.
- 429: rate limit.
- Timeout/network: loi tam thoi.
- Response khong co node: query khong co ket qua.

Khong de mot loi PageIndex lam ca chatbot crash. Ghi log ky thuat va cho retrieval quay
ve hybrid/no-evidence path.

## 13. Task 10 - Generation co citation

File can lam: `src/task10_generation.py`.

### 13.1. `reorder_for_llm()`

Voi chunks da sort theo relevance:

```text
[1, 2, 3, 4, 5] -> [1, 3, 5, 4, 2]
```

Dam bao khong mat item, khong duplicate va khong mutate list goc ngoai y muon.

### 13.2. `format_context()`

Moi chunk phai co label ro rang:

```text
[Document 1]
Source: legal/tuition-fees-rmit.md
Year: 2026
Type: legal
Content: ...
```

Neu year khong co, dung `Unknown`, khong tu dien nam hien tai.

### 13.3. Goi dung provider

Code hien tai dung OpenRouter base URL, vi vay baseline nen chi lay
`OPENROUTER_API_KEY`. Khong lay `OPENAI_API_KEY` roi gui nham sang OpenRouter.

Truoc khi goi API:

1. Kiem tra key ton tai.
2. Kiem tra context khong rong.
3. Chon model ID dang ton tai trong tai khoan OpenRouter cua ban.
4. Dat timeout va bat loi 401/429/network.

Cau hinh factual nen bat dau voi:

```python
TOP_K = 5
TEMPERATURE = 0.2
TOP_P = 0.9
```

Khong can vua temperature cao vua top-p cao cho bai toan factual.

### 13.4. Citation

Prompt chi duoc yeu cau citation ma metadata co the cung cap. Mau:

```text
[tuition-fees-rmit.pdf, 2026]
```

Sau khi nhan answer, nen validate toi thieu:

- Cau tra loi co citation neu co factual claim.
- Citation source ton tai trong danh sach chunks.
- Neu context rong/score qua thap, tra ve cau khong the xac minh ma khong goi LLM.

### 13.5. Contract dau ra

```python
{
    "answer": "...",
    "sources": chunks,
    "retrieval_source": "hybrid"
}
```

Nen tra `sources` theo dung thu tu context da dua cho LLM de UI va citation de doi
chieu.

## 14. Hoan thien Streamlit UI

File can lam: `app.py`.

UI hien tai da co khung. Sau khi Task 10 chay duoc:

1. Import `generate_with_citation` mot lan, khong import trong moi request neu khong can.
2. Validate input rong va gioi han do dai query.
3. Hien answer.
4. Hien source, type, score va excerpt.
5. Khong hien raw stack trace hoac API key cho user.
6. Disable/bao ro PageIndex neu chua cau hinh.

### 14.1. Conversation memory

Hien tai `st.session_state.messages` chi dung de hien thi. De follow-up that su hoat
dong, can dua lich su lien quan vao query rewriting hoac generation prompt.

Baseline don gian:

- Lay 2-4 luot hoi dap gan nhat.
- Yeu cau LLM rewrite follow-up thanh standalone question.
- Retrieval dung standalone question.
- Generation van tra loi cau hoi hien tai dua tren context.

Khong dua toan bo lich su vo han vao prompt.

### 14.2. Chay app

```powershell
streamlit run app.py
```

Thu cac tinh huong:

- Cau hoi co trong tai lieu.
- Cau hoi paraphrase.
- Cau hoi lac de.
- Follow-up nhu `Con dieu kien thi sao?`.
- Mat mang hoac API key sai.

## 15. Tests va cach debug theo tang

### 15.1. Chay toan bo test

```powershell
python -m pytest tests/test_individual.py -v
```

Repo co 35 test. Chu y `skipped` khong phai la hoan thanh. Muc tieu la test pass va ban
tu demo duoc output that.

### 15.2. Chay test theo task

```powershell
python -m pytest tests/test_individual.py -v -k Task4
python -m pytest tests/test_individual.py -v -k Task5
python -m pytest tests/test_individual.py -v -k Task9
python -m pytest tests/test_individual.py -v -k Task10
```

### 15.3. Debug theo thu tu

Neu Task 10 loi, kiem tra nguoc:

```text
Task 10 co context khong?
  -> Task 9 co result khong?
     -> Task 5/6 co result khong?
        -> Chroma co chunk khong?
           -> standardized co Markdown khong?
              -> landing co du lieu that khong?
```

Khong sua prompt neu retrieval dang tra chunk sai.

## 16. Evaluation pipeline

Files:

- `group_project/evaluation/golden_dataset.json`
- `group_project/evaluation/eval_pipeline.py`
- `group_project/evaluation/results.md`

### 16.1. Mo rong golden dataset

Hien tai dataset chi co 3 cau; can it nhat 15. Nen chia deu:

- 4 cau hoc phi/thanh toan.
- 3 cau hoc bong.
- 2 cau cho o.
- 2 cau thu vien.
- 2 cau dang ky hoc phan.
- 2 cau lac de/khong du evidence.

Moi item nen co:

```json
{
  "question": "...",
  "expected_answer": "...",
  "expected_context": "...",
  "expected_sources": ["legal/tuition-fees-rmit.md"],
  "answerable": true
}
```

Golden answer phai duoc viet tu tai lieu that sau Task 3, khong tu tri nho.

### 16.2. Chon framework

Requirements dang pin RAGAS `0.1.21`, vi vay co the dung RAGAS de giam thay doi moi
truong. Can tao Dataset voi:

- `question`
- `answer`
- `contexts`
- `ground_truth`

Danh gia bon metric:

- Faithfulness: answer co bam context khong.
- Answer relevancy: answer co tra loi dung cau hoi khong.
- Context recall: retrieval co lay du evidence khong.
- Context precision: cac chunk lay ve co that su huu ich khong.

### 16.3. A/B test dung nghia

Pipeline hien tai chua co `alpha`, vi vay khong dua tham so khong ton tai vao config.
Nen sua `retrieve()` de ho tro mode ro rang, vi du:

```text
Config A: hybrid + RRF
Config B: dense-only
```

Hai config phai dung cung golden dataset, model generation va top_k. Chi thay mot bien
chinh de ket qua co the giai thich.

### 16.4. Bao cao

`results.md` can co:

1. Framework va model evaluator.
2. Bang diem tong.
3. Chenh lech A/B.
4. Bottom 3 cau hoi.
5. Failure stage: ingestion, retrieval, reranking hay generation.
6. Root cause cu the.
7. De xuat cai thien co the do lai.

Can luu y RAGAS co the goi LLM nhieu lan. Chay 2-3 cau de smoke test truoc, sau do moi
chay full 15+ cau de tranh het quota.

## 17. Cac mau thuan trong starter can sua thong nhat

Truoc khi nop bai, dam bao cac diem sau da duoc thong nhat trong code va README:

| Van de | Hien tai | Cach xu ly |
|---|---|---|
| Chunking | Tai lieu `800/100`, code `500/50` | Chon mot config, ghi ly do va A/B test neu can |
| Fallback threshold | Tai lieu `0.48`, code `0.3` | Calibrate tren corpus that |
| RRF | Pseudo-code co nguy co goi hai lan | RRF mot lan de fusion; rerank sau do chi khi co model khac |
| Citation year | Prompt yeu cau nam, metadata khong co | Them year tu ingestion; thieu thi ghi Unknown |
| Provider | Lay OpenAI key nhung goi OpenRouter URL | Dung key va base URL cung provider |
| Sample data | README noi co data mau | Repo hien chi co `.gitkeep`; phai thu thap data that |
| PageIndex | `doc_id` chua duoc luu | Persist mapping source/doc_id |
| Conversation | UI chi hien history | Rewrite follow-up hoac dua history co gioi han vao prompt |

## 18. Definition of Done

Project chi nen coi la hoan thanh khi dat tat ca muc sau:

- [ ] `.venv` hoat dong va dependencies import duoc.
- [x] Co it nhat 3 legal documents that.
- [x] Co it nhat 5 news JSON co metadata.
- [x] Tat ca du lieu duoc convert thanh Markdown UTF-8.
- [x] Metadata co source, type va year neu xac dinh duoc.
- [ ] Chunk ID duy nhat va on dinh.
- [ ] ChromaDB co embeddings cua toan bo chunks.
- [ ] Semantic search tra ket qua dung y nghia.
- [ ] BM25 tra ket qua dung keyword.
- [ ] RRF gop dung theo chunk ID.
- [ ] Fallback dung cosine goc va threshold da calibrate.
- [ ] PageIndex co mapping document ID va xu ly loi dich vu ngoai.
- [ ] Generation chi dung context va citation co the doi chieu.
- [ ] Query lac de tra ve khong the xac minh.
- [ ] Streamlit hien answer va sources.
- [ ] Follow-up question co su dung context hoi thoai.
- [ ] 35 test khong con bi skip vi `NotImplementedError`.
- [ ] Golden dataset co it nhat 15 cau.
- [ ] Evaluation co 4 metrics va hai config A/B.
- [ ] `results.md` co diem, worst cases va de xuat cai thien.

## 19. Lenh chay day du sau khi hoan thanh

Lan dau hoac khi thay data/chunking/model:

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.task2_crawl_news
python -m src.task3_convert_markdown
python -m src.task4_chunking_indexing
python -m pytest tests/test_individual.py -v
streamlit run app.py
```

Evaluation:

```powershell
python -m group_project.evaluation.eval_pipeline
```

Hang ngay, neu index da co va data khong doi:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

## 20. Cach tu hoc trong luc implement

Voi moi task, tu tra loi bon cau sau truoc khi viet code:

1. Input cua ham la gi?
2. Output contract chinh xac la gi?
3. State nao can luu lai de khong tinh lai moi request?
4. Khi dependency ben ngoai loi, pipeline se fallback nhu nao?

Neu luon giu ro bon cau nay, ban se thay project khong phai mot khoi RAG lon, ma la cac
module nho co contract ro rang noi voi nhau.
