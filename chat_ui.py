import os
import streamlit as st
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="BJNEXUS AI — Enterprise RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0e1a; }
section[data-testid="stSidebar"] { background: #0f1529; border-right: 1px solid #1e2a4a; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stChatMessage { background: transparent !important; }

.header-container {
    background: linear-gradient(135deg, #0f1529 0%, #1a2550 100%);
    border: 1px solid #2a3a6a; border-radius: 16px;
    padding: 2rem 2.5rem; margin-bottom: 2rem;
    display: flex; align-items: center; gap: 1.5rem;
}
.header-logo { font-size: 3rem; line-height: 1; }
.header-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: -0.5px; }
.header-subtitle { font-size: 0.85rem; color: #7c9cbf; margin: 0.3rem 0 0 0; letter-spacing: 0.5px; }
.header-badge { margin-left: auto; background: #1a3a2a; border: 1px solid #2a6a4a; color: #4ade80; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; }
.header-badge-down { margin-left: auto; background: #2a1a1a; border: 1px solid #6a2a2a; color: #f87171; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; }

.login-container {
    max-width: 480px; margin: 4rem auto;
    background: #0f1529; border: 1px solid #1e2a4a;
    border-radius: 20px; padding: 3rem 2.5rem; text-align: center;
}
.login-logo { font-size: 3.5rem; margin-bottom: 1rem; }
.login-title { font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; }
.login-sub { font-size: 0.9rem; color: #7c9cbf; margin-bottom: 2rem; }
.login-error { background: #2a1a1a; border: 1px solid #6a2a2a; color: #f87171; padding: 0.8rem 1rem; border-radius: 10px; font-size: 0.85rem; margin-top: 1rem; }

.answer-container { background: #111827; border: 1px solid #1f2d4a; border-left: 4px solid #3b82f6; border-radius: 12px; padding: 1.5rem 2rem; margin: 1rem 0; }
.answer-label { font-size: 0.7rem; font-weight: 600; color: #3b82f6; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.8rem; }
.answer-text { font-size: 1.05rem; line-height: 1.8; color: #f1f5f9; font-weight: 400; }

.sources-label { font-size: 0.7rem; font-weight: 600; color: #94a3b8; letter-spacing: 2px; text-transform: uppercase; margin: 1.5rem 0 0.8rem 0; }
.source-card { background: #0f1829; border: 1px solid #1e2d4a; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }
.source-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.4rem; }
.source-filename { font-size: 0.9rem; font-weight: 600; color: #93c5fd; }
.score-pill { padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.score-high { background: #1a3a2a; color: #4ade80; border: 1px solid #2a6a4a; }
.score-mid  { background: #2a2a1a; color: #fbbf24; border: 1px solid #6a5a1a; }
.score-low  { background: #2a1a1a; color: #f87171; border: 1px solid #6a2a2a; }
.source-preview { font-size: 0.82rem; color: #94a3b8; line-height: 1.5; }
.score-bar-bg { background: #1e2d4a; border-radius: 4px; height: 4px; width: 100%; margin-top: 0.3rem; }

.denied-container { background: #1a0a0a; border: 1px solid #4a1a1a; border-left: 4px solid #ef4444; border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0; }
.denied-label { font-size: 0.7rem; font-weight: 600; color: #ef4444; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.5rem; }
.denied-text { font-size: 0.95rem; color: #fca5a5; line-height: 1.6; }

.warning-container { background: #1a1500; border: 1px solid #4a3a00; border-left: 4px solid #f59e0b; border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0; }
.warning-label { font-size: 0.7rem; font-weight: 600; color: #f59e0b; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.5rem; }
.warning-text { font-size: 0.95rem; color: #fcd34d; line-height: 1.6; }

.cost-bar { background: #0f1829; border: 1px solid #1e2d4a; border-radius: 8px; padding: 0.6rem 1rem; margin-top: 1rem; display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.cost-item { font-size: 0.78rem; color: #475569; }
.cost-item span { color: #94a3b8; font-weight: 500; }

.session-card { background: #0a1020; border: 1px solid #1e2a4a; border-radius: 8px; padding: 0.8rem; margin-top: 0.5rem; }
.session-label { font-size: 0.75rem; color: #64748b; }
.session-value { font-size: 1rem; color: #f1f5f9; font-weight: 600; margin: 0.2rem 0; }
.sidebar-title { font-size: 0.7rem; font-weight: 700; color: #4a6a9a !important; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.8rem; }

.footer { text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #1e2a4a; font-size: 0.75rem; color: #334155; }
</style>
""", unsafe_allow_html=True)


def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def validate_key_with_api(api_key: str) -> dict | None:
    """Test the key against /query with a dummy call to verify it works."""
    try:
        r = requests.post(
            f"{API_URL}/query",
            json={"query": "ping", "department": "general", "user_id": "system"},
            headers={"X-API-Key": api_key},
            timeout=5
        )
        if r.status_code in [200, 422]:
            return {"valid": True}
        return None
    except:
        return None


ROLE_DISPLAY = {
    "admin":          ("Administrator",   "All departments",             "#4ade80"),
    "hr_staff":       ("HR Staff",        "HR · General",                "#93c5fd"),
    "finance_staff":  ("Finance Staff",   "Finance · General",           "#93c5fd"),
    "legal_staff":    ("Legal Staff",     "Legal · General",             "#93c5fd"),
    "employee":       ("Employee",        "General only",                "#f87171"),
}

ROLE_DEPARTMENTS = {
    "admin":         ["general", "hr", "finance", "legal"],
    "hr_staff":      ["hr", "general"],
    "finance_staff": ["finance", "general"],
    "legal_staff":   ["legal", "general"],
    "employee":      ["general"],
}


# ── LOGIN GATE ──────────────────────────────────────────────────────────────
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "key_role" not in st.session_state:
    st.session_state.key_role = ""
if "key_owner" not in st.session_state:
    st.session_state.key_owner = ""

if not st.session_state.authenticated:
    api_ok = check_api()

    st.markdown(f"""
    <div class="login-container">
        <div class="login-logo">🧠</div>
        <div class="login-title">BJNEXUS AI</div>
        <div class="login-sub">Enterprise RAG System — Secure Access</div>
    </div>
    """, unsafe_allow_html=True)

    if not api_ok:
        st.error("Cannot connect to API. Make sure the server is running.")
        st.stop()

    with st.form("login_form"):
        key_input = st.text_input(
            "Enter your API Key",
            type="password",
            placeholder="rag-xxxxxxxxxxxxxxxxxxxx"
        )
        submitted = st.form_submit_button("Access System", use_container_width=True)

        if submitted:
            if not key_input.strip():
                st.error("Please enter your API key.")
            else:
                with st.spinner("Verifying..."):
                    result = validate_key_with_api(key_input.strip())
                if result:
                    # Get role from DB via a real query
                    try:
                        r = requests.post(
                            f"{API_URL}/query",
                            json={"query": "ping", "department": "general", "user_id": "system"},
                            headers={"X-API-Key": key_input.strip()},
                            timeout=5
                        )
                        # Key is valid if we get 200 or 422 (validation error is fine)
                        if r.status_code in [200, 422]:
                            # Fetch the REAL identity tied to this key — do not
                            # let the UI guess or let the user self-select a role.
                            who = requests.get(
                                f"{API_URL}/whoami",
                                headers={"X-API-Key": key_input.strip()},
                                timeout=5
                            )
                            who_data = who.json() if who.status_code == 200 else {}
                            st.session_state.api_key = key_input.strip()
                            st.session_state.key_owner = who_data.get("owner", "unknown")
                            st.session_state.key_role = who_data.get("role", "employee")
                            st.session_state.allowed_departments = who_data.get(
                                "allowed_departments", ["general"]
                            )
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.markdown('<div class="login-error">Invalid or inactive API key.</div>', unsafe_allow_html=True)
                    except:
                        st.markdown('<div class="login-error">Could not connect to server.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="login-error">Invalid or inactive API key.</div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">Powered by BJNEXUS AI · pgvector · Cohere · Groq</div>', unsafe_allow_html=True)
    st.stop()


# ── MAIN APP (authenticated) ─────────────────────────────────────────────────
api_ok = check_api()
badge_class = "header-badge" if api_ok else "header-badge-down"
badge_text = "● API LIVE" if api_ok else "● API DOWN"

st.markdown(f"""
<div class="header-container">
    <div class="header-logo">🧠</div>
    <div>
        <p class="header-title">BJNEXUS AI — Enterprise RAG</p>
        <p class="header-subtitle">pgvector · Cohere Rerank v3 · Groq LLaMA 3.3 70B · RBAC + ABAC · Hallucination-Free</p>
    </div>
    <div class="{badge_class}">{badge_text}</div>
</div>
""", unsafe_allow_html=True)

if not api_ok:
    st.error("Cannot connect to API at " + API_URL)
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-title">🔐 Session</p>', unsafe_allow_html=True)

    # Department selector — restricted to what this authenticated key
    # is actually allowed to query (from /whoami), not a static full list.
    all_depts = st.session_state.get("allowed_departments", ["general"])
    department = st.selectbox("Department", all_depts)
    st.caption(f"Signed in as **{st.session_state.get('key_owner', 'unknown')}** ({st.session_state.get('key_role', 'employee')})")

    st.markdown("---")
    st.markdown('<p class="sidebar-title">📁 Ingest Document</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "docx", "xlsx", "txt", "csv"],
        label_visibility="collapsed"
    )
    ingest_dept = st.selectbox("Ingest to department", all_depts)

    if st.button("⬆ Ingest Document", use_container_width=True):
        if not uploaded_file:
            st.warning("Please select a file first.")
        else:
            with st.spinner("Ingesting..."):
                try:
                    response = requests.post(
                        f"{API_URL}/ingest",
                        files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")},
                        data={"department": ingest_dept},
                        headers={"X-API-Key": st.session_state.api_key}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['chunks_created']} chunks ingested from {uploaded_file.name}")
                    else:
                        st.error(f"❌ {response.text}")
                except Exception as e:
                    st.error(f"❌ Ingest error: {e}")

    st.markdown("---")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    if st.button("🔓 Sign Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.api_key = ""
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    query_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.markdown(f"""
<div class="session-card">
    <div class="session-label">Status</div>
    <div class="session-value" style="color:#4ade80;font-size:0.85rem;">● Authenticated</div>
    <div class="session-label" style="margin-top:0.4rem;">Queries this session</div>
    <div class="session-value">{query_count}</div>
</div>
""", unsafe_allow_html=True)

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Ask anything about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": prompt,
                        "department": department,
                        "user_id": st.session_state.get("key_owner", "anonymous"),
                        "top_k": 5
                    },
                    headers={"X-API-Key": st.session_state.api_key},
                    timeout=30
                )
                data = response.json()
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                cost = data.get("cost", {})
                model = data.get("model", "unknown")
                chunks_used = data.get("chunks_used", 0)
                total_cost = cost.get("total_cost_usd", 0)
                total_tokens = cost.get("total_tokens", 0)

                if "Access denied" in answer:
                    html = f"""
<div class="denied-container">
    <div class="denied-label">🚫 Access Denied</div>
    <div class="denied-text">{answer}</div>
</div>"""

                elif "do not meet the relevance threshold" in answer or "not enough information" in answer.lower():
                    html = f"""
<div class="warning-container">
    <div class="warning-label">⚠ No Relevant Documents Found</div>
    <div class="warning-text">{answer}</div>
</div>"""

                else:
                    sources_html = ""
                    if sources:
                        sources_html = '<div class="sources-label">📚 Sources</div>'
                        for s in sources:
                            score = s.get("score", 0)
                            filename = s.get("filename", "unknown")
                            preview = s.get("preview", "")
                            score_pct = int(score * 100)
                            if score >= 0.8:
                                pill_class, bar_color = "score-high", "#4ade80"
                            elif score >= 0.5:
                                pill_class, bar_color = "score-mid", "#fbbf24"
                            else:
                                pill_class, bar_color = "score-low", "#f87171"

                            sources_html += f"""
<div class="source-card">
    <div class="source-header">
        <span class="source-filename">📄 {filename}</span>
        <span class="score-pill {pill_class}">{score_pct}% confidence</span>
    </div>
    <div class="score-bar-bg">
        <div style="background:{bar_color};height:4px;border-radius:4px;width:{score_pct}%;"></div>
    </div>
    <div class="source-preview">{preview}</div>
</div>"""

                    cost_html = f"""
<div class="cost-bar">
    <div class="cost-item">Model <span>{model}</span></div>
    <div class="cost-item">Chunks <span>{chunks_used}</span></div>
    <div class="cost-item">Tokens <span>{total_tokens:,}</span></div>
    <div class="cost-item">Cost <span>${total_cost:.6f}</span></div>
</div>"""

                    html = f"""
<div class="answer-container">
    <div class="answer-label">Answer</div>
    <div class="answer-text">{answer}</div>
</div>
{sources_html}
{cost_html}"""

                st.markdown(html, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": html})

            except requests.exceptions.Timeout:
                st.error("⏱ Request timed out.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to API.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown('<div class="footer">Powered by BJNEXUS AI · pgvector · Cohere · Groq</div>', unsafe_allow_html=True)