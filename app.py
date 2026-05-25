import streamlit as st
from pipeline import run_pipeline
from rag import ask
from config import CATEGORIES

st.set_page_config(
    page_title="NewsDaily",
    page_icon="📰",
    layout="wide"
)

# ---- session state ----
if "articles" not in st.session_state:
    st.session_state.articles = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- header ----
st.title("📰 NewsDaily")
st.caption("AI-powered news summarizer and Q&A")

# ---- sidebar ----
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🔄 Fetch latest news", use_container_width=True):
        with st.spinner("Fetching and summarizing articles..."):
            st.session_state.articles = run_pipeline()
        st.success("Done!")

    st.divider()
    st.caption("NewsDaily uses RAG to answer questions based on today's news only.")

# ---- tabs ----
tab1, tab2 = st.tabs(["📋 Daily Digest", "💬 Ask Anything"])

# ---- tab 1: daily digest ----
with tab1:
    if not st.session_state.articles:
        st.info("Click 'Fetch latest news' in the sidebar to load today's articles.")
    else:
        # category filter
        selected = st.selectbox(
            "Filter by category",
            ["All"] + [c.capitalize() for c in CATEGORIES]
        )

        # filter articles
        filtered = st.session_state.articles
        if selected != "All":
            filtered = [
                a for a in st.session_state.articles
                if a["category"].lower() == selected.lower()
            ]

        st.markdown(f"**{len(filtered)} articles**")
        st.divider()

        # display as cards
        for article in filtered:
            with st.container():
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.subheader(article["title"])
                    st.caption(f"🗞️ {article['source']}  •  📂 {article['category'].capitalize()}  •  🕐 {article['published_at'][:10]}")
                    st.write(article.get("summary", article.get("description", "No summary available.")))
                with col2:
                    st.link_button("Read →", article["url"])
                st.divider()

# ---- tab 2: ask anything ----
with tab2:
    st.subheader("Ask me anything about today's news")

    # display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                st.caption(f"📰 Sources: {', '.join(msg['sources'])}")

    # chat input
    question = st.chat_input("e.g. What happened in tech today?")

    if question:
        # show user message
        with st.chat_message("user"):
            st.write(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # get answer
        with st.chat_message("assistant"):
            with st.spinner("Searching articles..."):
                response = ask(question)
            st.write(response["answer"])
            if response["sources"]:
                st.caption(f"📰 Sources: {', '.join(response['sources'])}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"]
        })