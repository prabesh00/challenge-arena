"""
Challenge Arena - Admin Dashboard
List all challenges, create new ones, quick actions.
"""

import streamlit as st
import pandas as pd

from database.models import (
    get_all_challenges, create_challenge,
    get_leaderboard, get_all_students, add_resource,
)
from auth.auth import require_admin, logout_admin
from scoring.registry import CHALLENGE_TYPE_NAMES, get_default_primary_metric
from utils.helpers import save_uploaded_file

require_admin()

st.set_page_config(page_title="Challenge Arena - Admin Dashboard", page_icon="📊")

with st.sidebar:
    st.markdown("### 🔐 Admin Panel")
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["📊 Dashboard", "➕ New Challenge", "👥 Students", "📋 QR Code"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("🚪 Logout"):
        logout_admin()
        st.rerun()

if menu == "📊 Dashboard":
    st.title("📊 Admin Dashboard")

    challenges = get_all_challenges(include_closed=True)

    if not challenges:
        st.info("No challenges created yet. Create your first challenge!")

    for challenge in challenges:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                status_icon = "🟢" if challenge["is_open"] else "🔴"
                type_name = CHALLENGE_TYPE_NAMES.get(challenge["type"], challenge["type"])
                st.markdown(f"### {status_icon} {challenge['title']}")
                st.markdown(f"**Type:** {type_name} | **Primary Metric:** {challenge['primary_metric']}")
                if challenge.get("deadline"):
                    st.markdown(f"⏰ **Deadline:** {challenge['deadline']}")

            with col2:
                leaderboard = get_leaderboard(challenge["id"])
                st.metric("Submissions", len(leaderboard))

            with col3:
                if st.button("Manage →", key=f"manage_{challenge['id']}"):
                    st.query_params["challenge_id"] = challenge["id"]
                    st.switch_page("pages/admin_challenge_detail.py")

elif menu == "➕ New Challenge":
    st.title("➕ Create New Challenge")

    with st.form("create_challenge_form"):
        title = st.text_input("Challenge Title", placeholder="e.g., Flower Classification Challenge")
        description_md = st.text_area(
            "Description (Markdown supported)",
            placeholder="Describe the challenge, requirements, and instructions...",
            height=200,
        )

        col1, col2 = st.columns(2)
        with col1:
            challenge_type = st.selectbox(
                "Challenge Type",
                options=list(CHALLENGE_TYPE_NAMES.keys()),
                format_func=lambda x: CHALLENGE_TYPE_NAMES[x],
                help="Select the type of challenge. This determines how submissions are scored.",
            )
        with col2:
            default_metric = get_default_primary_metric(challenge_type)
            primary_metric = st.text_input(
                "Primary Metric",
                value=default_metric,
                help="The metric used for ranking on the leaderboard",
            )

        col1, col2 = st.columns(2)
        with col1:
            is_open = st.checkbox("Open for submissions", value=True)
        with col2:
            deadline = st.date_input("Deadline (optional)", value=None)

        st.markdown("### 📎 Downloadable Resources (optional)")
        st.markdown("Upload files that students can download (datasets, starter notebooks, etc.)")
        resource_files = st.file_uploader(
            "Choose resource files",
            accept_multiple_files=True,
            help="Students will be able to download these files from the challenge page",
        )

        submitted = st.form_submit_button("🚀 Create Challenge", type="primary", use_container_width=True)

        if submitted:
            if not title:
                st.error("Please enter a challenge title.")
            else:
                challenge = create_challenge(
                    title=title,
                    description_md=description_md,
                    challenge_type=challenge_type,
                    primary_metric=primary_metric,
                    is_open=1 if is_open else 0,
                    deadline=str(deadline) if deadline else None,
                )

                st.success(f"✅ Challenge '{title}' created successfully!")

                if resource_files:
                    for uploaded_file in resource_files:
                        storage_path = save_uploaded_file(uploaded_file, challenge["id"], file_type="resource")
                        add_resource(challenge["id"], uploaded_file.name, storage_path)
                    st.success(f"✅ {len(resource_files)} resource(s) uploaded.")

                st.rerun()

elif menu == "👥 Students":
    st.title("👥 Registered Students")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students)
        df = df[["name", "email", "cohort", "created_at"]]
        df.columns = ["Name", "Email", "Cohort", "Registered At"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"**Total Students:** {len(students)}")
    else:
        st.info("No students registered yet.")

elif menu == "📋 QR Code":
    st.switch_page("pages/admin_qr.py")