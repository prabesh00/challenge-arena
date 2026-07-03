"""
Challenge Arena - Main Entry Point
Multi-page Streamlit application for running AI/ML bootcamp challenges.
"""

import streamlit as st
from database.db import init_db
from utils.helpers import ensure_dirs

st.set_page_config(
    page_title="Challenge Arena",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database and directories on first run
if "db_initialized" not in st.session_state:
    ensure_dirs()
    init_db()
    st.session_state["db_initialized"] = True


def main():
    """Main entry point - redirects to appropriate page based on auth status."""
    from auth.auth import is_admin_logged_in, is_student_logged_in

    # Landing page
    st.title("🎯 Challenge Arena")
    st.markdown("### AI/ML Bootcamp Challenge Platform")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("#### 👨‍🏫 Instructor")
        if is_admin_logged_in():
            st.success("✅ Logged in")
            if st.button("📊 Go to Dashboard", use_container_width=True):
                st.switch_page("pages/admin_dashboard.py")
        else:
            if st.button("🔐 Admin Login", use_container_width=True):
                st.switch_page("pages/admin_login.py")

    with col2:
        st.markdown("#### 👩‍🎓 Student")
        if is_student_logged_in():
            st.success(f"✅ Logged in as {st.session_state.get('student_name', '')}")
            if st.button("📋 View Challenges", use_container_width=True):
                st.switch_page("pages/challenges.py")
        else:
            if st.button("🎯 Join Challenge", type="primary", use_container_width=True):
                st.switch_page("pages/login.py")

    with col3:
        st.markdown("#### 📱 Quick Access")
        if st.button("📋 QR Login Page", use_container_width=True):
            st.switch_page("pages/login.py")

    st.markdown("---")

    # Show features section
    st.markdown("""
    ## 🚀 Features

    | Feature | Description |
    |---------|-------------|
    | 🔬 **Classification** | Accuracy, Precision, Recall, F1, AUC-ROC scoring |
    | 📈 **Regression** | MSE, MAE, R², RMSE, MAPE scoring |
    | 📚 **RAG** | Retrieval metrics + semantic similarity |
    | 🤖 **LLM** | Semantic similarity + OpenRouter LLM-as-Judge |
    | 💻 **Code Challenges** | Manual scoring with feedback |
    | 🏆 **Live Leaderboard** | Real-time rankings with tie-breaking |
    | 📱 **QR Code Login** | One-scan student registration |
    | 📤 **CSV Upload** | Validate, score, and rank automatically |
    """)

    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit & SQLite | "
        "[GitHub](https://github.com)"
    )


if __name__ == "__main__":
    main()