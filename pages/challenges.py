"""
Challenge Arena - Student Challenges List Page
"""

import streamlit as st
from database.models import get_all_challenges, get_active_submission
from auth.auth import require_student, get_current_student_id, get_current_student_name, logout_student

require_student()

st.set_page_config(page_title="Challenge Arena - Challenges", page_icon="📋")

# Sidebar with user info
with st.sidebar:
    st.markdown(f"### 👤 {get_current_student_name()}")
    if st.button("🚪 Logout"):
        logout_student()
        st.rerun()

st.title("📋 Active Challenges")

challenges = get_all_challenges(include_closed=False)

if not challenges:
    st.info("🎯 No active challenges right now. Check back later!")
    st.stop()

for challenge in challenges:
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            # Show challenge type badge
            type_badges = {
                "classification": "🔬",
                "regression": "📈",
                "rag": "📚",
                "llm": "🤖",
                "code_challenge": "💻",
            }
            badge = type_badges.get(challenge["type"], "📝")
            st.markdown(f"### {badge} {challenge['title']}")
            st.markdown(f"**Type:** {challenge['type'].replace('_', ' ').title()}")
            
            # Show deadline if set
            if challenge.get("deadline"):
                st.markdown(f"⏰ **Deadline:** {challenge['deadline']}")

        with col2:
            # Check if user has submitted
            active_sub = get_active_submission(challenge["id"], get_current_student_id())
            if active_sub:
                if active_sub["status"] == "scored":
                    st.metric("Your Score", f"{active_sub['primary_score']:.4f}" if active_sub['primary_score'] else "N/A")
                elif active_sub["status"] == "pending":
                    st.info("⏳ Pending")
                elif active_sub["status"] == "error":
                    st.error("❌ Error")
            else:
                st.markdown("**No submission**")

        with col3:
            if st.button("View →", key=f"view_{challenge['id']}"):
                st.switch_page("pages/challenge_detail.py")

# Handle navigation via query params
query_params = st.query_params
if "challenge_id" in query_params:
    st.session_state["current_challenge_id"] = query_params["challenge_id"]