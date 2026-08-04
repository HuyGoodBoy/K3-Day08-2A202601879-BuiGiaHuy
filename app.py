"""
RAG Chatbot — University Services (Starter Template)
Streamlit app kết nối RAG Retrieval (Task 9) và Generation (Task 10).

Chạy:
    streamlit run app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Thêm project root vào sys.path để import các task từ src/
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="University Services RAG Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# STYLE — "General Intelligence Company" editorial design system
# (warm parchment canvas, serif headings, hairline mist borders, signal-blue accent)
# =============================================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --color-parchment: #fefffc;
        --color-paper: #ffffff;
        --color-linen: #f9faf7;
        --color-graphite: #2c2c2c;
        --color-charcoal: #444141;
        --color-ash: #646464;
        --color-fog: #b4b8b4;
        --color-mist: #dee2de;
        --color-twilight: #282834;
        --color-dusk: #1f1f29;
        --color-signal-blue: #41a1cf;
        --color-cerulean: #0081c0;
        --font-serif: 'Fraunces', Georgia, serif;
        --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--color-charcoal);
    }

    .stApp {
        background: var(--color-parchment);
    }

    /* ---- Hide default chrome clutter ---- */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* ---- Hero banner (stands in for the atmospheric illustration) ---- */
    .gic-hero {
        background: linear-gradient(135deg, #0081c0 0%, #1f6fa8 55%, #1f1f29 100%);
        border-radius: 24px;
        padding: 48px 56px;
        margin: 8px 0 32px 0;
        box-shadow: rgba(0, 0, 0, 0.06) 0px 2px 2px 0px, rgba(0, 0, 0, 0.04) 0px 0px 0px 5px;
    }
    .gic-hero .eyebrow {
        font-family: var(--font-sans);
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.75);
        margin-bottom: 12px;
    }
    .gic-hero h1 {
        font-family: var(--font-serif) !important;
        font-weight: 400 !important;
        font-size: 48px !important;
        line-height: 1.1 !important;
        letter-spacing: -0.02em;
        color: #ffffff !important;
        margin: 0 0 12px 0 !important;
    }
    .gic-hero p {
        font-family: var(--font-sans);
        font-size: 16px;
        line-height: 1.5;
        color: rgba(255,255,255,0.85);
        max-width: 640px;
        margin: 0;
    }

    /* ---- Headings ---- */
    h1, h2, h3 {
        font-family: var(--font-serif) !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em;
        color: var(--color-graphite) !important;
    }
    h2 { font-size: 27px !important; }
    h3 { font-size: 20px !important; }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: var(--color-paper);
        border-right: 1px solid var(--color-mist);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 32px;
    }
    section[data-testid="stSidebar"] h1 {
        font-family: var(--font-serif) !important;
        font-size: 27px !important;
        color: var(--color-graphite) !important;
    }
    section[data-testid="stSidebar"] h3 {
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--color-ash) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--color-mist);
        margin: 20px 0;
    }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: var(--color-ash) !important;
    }

    /* ---- Buttons: outlined ghost style, Signal Blue on hover ---- */
    .stButton > button {
        background: var(--color-linen);
        border: 1px solid var(--color-mist);
        border-radius: 8px;
        color: var(--color-charcoal);
        font-family: var(--font-sans);
        font-weight: 500;
        font-size: 14px;
        padding: 8px 14px;
        text-align: left;
        box-shadow: none;
        transition: border-color 0.15s ease, color 0.15s ease;
    }
    .stButton > button:hover {
        border-color: var(--color-signal-blue);
        color: var(--color-signal-blue);
        background: var(--color-linen);
    }
    .stButton > button:focus:not(:active) {
        border-color: var(--color-signal-blue);
        color: var(--color-signal-blue);
    }

    /* ---- Slider (signal blue accent) ---- */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--color-signal-blue) !important;
        border-color: var(--color-signal-blue) !important;
    }
    div[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"] {
        background-color: var(--color-signal-blue) !important;
    }

    /* ---- Chat messages: white cards with hairline mist border ---- */
    div[data-testid="stChatMessage"] {
        background: var(--color-paper);
        border: 1px solid var(--color-mist);
        border-radius: 12px;
        padding: 4px 8px;
        margin-bottom: 12px;
        box-shadow: rgba(0, 0, 0, 0.08) 0px 1px 1px 0px;
    }

    /* ---- Chat input: flat, bottom-border only (paper-form feel) ---- */
    div[data-testid="stChatInput"] {
        background: var(--color-linen);
        border: none;
        border-bottom: 1px solid var(--color-charcoal);
        border-radius: 4px 4px 0 0;
    }
    div[data-testid="stChatInput"] textarea {
        color: var(--color-charcoal);
        font-family: var(--font-sans);
    }

    /* ---- Expander: diagram-card treatment for sources ---- */
    div[data-testid="stExpander"] {
        border: 1px solid var(--color-mist) !important;
        border-radius: 16px !important;
        background: rgba(255,255,255,0.7);
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 8px 0px;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-family: var(--font-sans);
        font-weight: 500;
        color: var(--color-graphite);
    }

    /* ---- Dividers ---- */
    hr {
        border-color: var(--color-mist) !important;
    }

    /* ---- Caption text ---- */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--color-ash) !important;
        font-family: var(--font-sans);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# SIDEBAR — INFO & SETTINGS
# =============================================================================

with st.sidebar:
    st.title("🎓 University RAG")
    st.caption("Trợ lý hỏi đáp về dịch vụ và chính sách đại học (học phí, học bổng, ký túc xá, thư viện)")

    st.divider()

    st.subheader("💡 Câu hỏi gợi ý")
    suggestions = [
        "Học phí tại RMIT Vietnam là bao nhiêu?",
        "Làm sao để đặt phòng học nhóm ở thư viện?",
        "Điều kiện xin học bổng Academic Achievement?",
        "Dịch vụ hỗ trợ chỗ ở cho sinh viên như thế nào?",
        "Cách đăng ký học phần qua myRMIT?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{s[:20]}"):
            st.session_state["pending_query"] = s

    st.divider()
    st.subheader("⚙️ Thiết lập")
    top_k = st.slider("Số chunks retrieval (top_k)", 3, 10, 5)

    st.divider()
    st.caption("**Kiến trúc hệ thống**")
    st.caption("Hybrid Retrieval (Semantic + BM25) → RRF Rerank → PageIndex Fallback → LLM Generation có Citation")

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# =============================================================================
# HERO
# =============================================================================

st.markdown(
    """
    <div class="gic-hero">
        <div class="eyebrow">RAG · Retrieval-Augmented Generation</div>
        <h1>University Services Assistant</h1>
        <p>Hỏi đáp thông tin dịch vụ đại học — học phí, học bổng, ký túc xá, thư viện —
        với trích dẫn nguồn rõ ràng từ tài liệu chính thức.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander(f"📚 Nguồn tham khảo ({len(msg['sources'])} chunks)"):
                for i, src in enumerate(msg["sources"], 1):
                    meta = src.get("metadata", {})
                    source_name = meta.get("source", "Unknown")
                    doc_type = meta.get("type", "unknown")
                    score = src.get("score", 0)
                    st.markdown(f"**[{i}] {source_name}** `{doc_type}` | score: `{score:.4f}`")
                    st.text(src.get("content", "")[:300] + "...")
                    st.divider()

# =============================================================================
# QUERY HANDLING
# =============================================================================

# Xử lý khi bấm nút gợi ý hoặc nhập câu hỏi mới
user_input = st.chat_input("Nhập câu hỏi của bạn về chính sách/dịch vụ đại học...")
query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None

    # Hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Sinh câu trả lời từ RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            try:
                # TODO (Học viên): Tích hợp hàm sinh câu trả lời từ Task 10
                # Ví dụ:
                # from src.task10_generation import generate_with_citation
                # response = generate_with_citation(query, top_k=top_k)
                # answer = response["answer"]
                # sources = response.get("sources", [])

                # Tạm thời mockup để test UI:
                from src.task10_generation import generate_with_citation
                response = generate_with_citation(query, top_k=top_k)
                answer = response.get("answer", "Chưa thể trả lời.")
                sources = response.get("sources", [])

            except NotImplementedError:
                answer = "[!] **Task 10 chưa được implement.** Hãy hoàn thành `src/task10_generation.py` để kết nối pipeline vào UI!"
                sources = []
            except Exception as e:
                answer = f"[X] **Lỗi khi chạy RAG Pipeline:** {e}"
                sources = []

            st.markdown(answer)

            if sources:
                with st.expander(f"📚 Nguồn tham khảo ({len(sources)} chunks)"):
                    for i, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        source_name = meta.get("source", "Unknown")
                        doc_type = meta.get("type", "unknown")
                        score = src.get("score", 0)
                        st.markdown(f"**[{i}] {source_name}** `{doc_type}` | score: `{score:.4f}`")
                        st.text(src.get("content", "")[:300] + "...")
                        st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
