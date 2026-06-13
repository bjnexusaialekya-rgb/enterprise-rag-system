import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="BJNEXUS AI — Enterprise RAG",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stTextInput input { background-color: #1e2130; color: white; }
    .answer-box {
        background-color: #1e2130;
        border-left: 4px solid #4f8ef7;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .source-box {
        background-color: #161822;
        border: 1px solid #2e3250;
        padding: 0.8rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    .score-high { color: #4caf50; font-weight: bold; }
    .score-mid  { color: #ff9800; font-weight: bold; }
    .score-low  { color: #f44336; font-weight: bold; }
    .denied-box {
        background-color: #2a1a1a;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("## 🧠 BJNEXUS AI — Enterprise RAG System")
st.markdown("*Powered by pgvector · Cohere Rerank · Groq LLaMA 3.3 · RBAC + ABAC*")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### 🔐 Access Control")
    user_id = st.selectbox("User", [
        "admin_user",
        "hr_user",
        "finance_user",
        "legal_user",
        "test_user"
    ])
    department = st.selectbox("Department", [
        "general",
        "hr",
        "finance",
        "legal"
    ])
    top_k = st.slider("Chunks to retrieve", 1, 10, 5)

    st.divider()
    st.markdown("### 📁 Role Matrix")
    st.markdown("""
| Role | Access |
|------|--------|
| admin | All |
| hr_staff | HR, General |
| finance_staff | Finance, General |
| legal_staff | Legal, General |
| employee | General only |
    """)

    st.divider()
    st.markdown("### 📤 Ingest Document")
    uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "xlsx", "txt", "csv"])
    ingest_dept = st.selectbox("Ingest to department", ["general", "hr", "finance", "legal"])
    if st.button("Ingest") and uploaded_file:
        with st.spinner("Ingesting..."):
            response = requests.post(
                f"{API_URL}/ingest",
                files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")},
                data={"department": ingest_dept}
            )
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {result['chunks_created']} chunks ingested")
            else:
                st.error(f"❌ Ingest failed: {response.text}")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Query input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and generating answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": prompt,
                        "department": department,
                        "user_id": user_id,
                        "top_k": top_k
                    }
                )
                data = response.json()
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                cost = data.get("cost", {})
                model = data.get("model", "unknown")
                chunks_used = data.get("chunks_used", 0)

                # Check if access denied
                if "Access denied" in answer:
                    st.markdown(f'<div class="denied-box">🚫 {answer}</div>', unsafe_allow_html=True)
                    full_response = f"🚫 {answer}"
                elif "do not meet the relevance threshold" in answer or "not enough information" in answer.lower():
                    st.markdown(f'<div class="denied-box">⚠️ {answer}</div>', unsafe_allow_html=True)
                    full_response = f"⚠️ {answer}"
                else:
                    st.markdown(f'<div class="answer-box">💬 {answer}</div>', unsafe_allow_html=True)
                    full_response = answer

                    # Sources
                    if sources:
                        st.markdown("**📚 Sources:**")
                        for s in sources:
                            score = s.get("score", 0)
                            if score >= 0.8:
                                score_class = "score-high"
                            elif score >= 0.5:
                                score_class = "score-mid"
                            else:
                                score_class = "score-low"

                            st.markdown(f"""
<div class="source-box">
📄 <b>{s.get('filename', 'unknown')}</b> &nbsp;
<span class="{score_class}">Score: {score}</span><br>
<small>{s.get('preview', '')}</small>
</div>
""", unsafe_allow_html=True)

                # Cost info
                total_cost = cost.get("total_cost_usd", 0)
                total_tokens = cost.get("total_tokens", 0)
                st.caption(f"🤖 {model} · {chunks_used} chunks · {total_tokens} tokens · ${total_cost:.6f}")

            except Exception as e:
                st.error(f"Error: {e}")
                full_response = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})
