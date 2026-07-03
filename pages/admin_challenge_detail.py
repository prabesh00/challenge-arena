"""
Challenge Arena - Admin Challenge Detail Page
Manage ground truth, submissions, manual scoring, delete submissions, toggle open/close.
"""

import json
import streamlit as st
import pandas as pd
from pathlib import Path

from database.models import (
    get_challenge, update_challenge, get_ground_truth, upload_ground_truth,
    get_all_submissions_for_challenge, get_submission, delete_submission,
    update_manual_score, get_leaderboard, get_resources,
    rescore_all_for_challenge, get_pending_submissions,
)
from auth.auth import require_admin, logout_admin
from scoring.registry import get_scorer, CHALLENGE_TYPE_NAMES
from utils.validation import read_csv_safe, validate_ground_truth_csv
from utils.helpers import (
    save_uploaded_file, format_timestamp, format_score,
    display_metrics, ensure_dirs,
)

require_admin()

st.set_page_config(page_title="Challenge Arena - Manage Challenge", page_icon="⚙️")

with st.sidebar:
    st.markdown("### 🔐 Admin Panel")
    if st.button("📊 Dashboard"):
        st.switch_page("pages/admin_dashboard.py")
    if st.button("🚪 Logout"):
        logout_admin()
        st.rerun()

# Get challenge ID
challenge_id = st.query_params.get("challenge_id") or st.session_state.get("manage_challenge_id")
if not challenge_id:
    st.error("No challenge selected.")
    st.page_link("pages/admin_dashboard.py", label="← Back to Dashboard")
    st.stop()

try:
    challenge_id = int(challenge_id)
except (ValueError, TypeError):
    st.error("Invalid challenge ID.")
    st.stop()

challenge = get_challenge(challenge_id)
if not challenge:
    st.error("Challenge not found.")
    st.stop()

st.session_state["manage_challenge_id"] = challenge_id

# ─── Challenge Header ──────────────────────────────────────────────────────────
type_name = CHALLENGE_TYPE_NAMES.get(challenge["type"], challenge["type"])
status_icon = "🟢" if challenge["is_open"] else "🔴"
st.title(f"⚙️ Manage: {challenge['title']}")
st.markdown(f"{status_icon} **Status:** {'Open' if challenge['is_open'] else 'Closed'} | "
            f"**Type:** {type_name} | "
            f"**Primary Metric:** {challenge['primary_metric']}")

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📝 Settings", "📤 Ground Truth", "📊 Submissions", "🏆 Leaderboard"])

# ─── TAB 1: Settings ───────────────────────────────────────────────────────────
with tab1:
    st.subheader("Challenge Settings")

    with st.form("update_challenge_form"):
        title = st.text_input("Title", value=challenge["title"])
        description_md = st.text_area(
            "Description (Markdown)",
            value=challenge["description_md"],
            height=200,
        )

        col1, col2 = st.columns(2)
        with col1:
            new_type = st.selectbox(
                "Challenge Type",
                options=list(CHALLENGE_TYPE_NAMES.keys()),
                format_func=lambda x: CHALLENGE_TYPE_NAMES[x],
                index=list(CHALLENGE_TYPE_NAMES.keys()).index(challenge["type"]),
            )
        with col2:
            primary_metric = st.text_input("Primary Metric", value=challenge["primary_metric"])

        is_open = st.checkbox("Open for submissions", value=bool(challenge["is_open"]))

        submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        if submitted:
            update_challenge(
                challenge_id,
                title=title,
                description_md=description_md,
                type=new_type,
                primary_metric=primary_metric,
                is_open=1 if is_open else 0,
            )
            st.success("✅ Challenge updated!")
            st.rerun()

    st.markdown("---")
    st.subheader("Danger Zone")
    
    # Rescore all button
    if st.button("🔄 Rescore All Submissions", type="secondary"):
        rescore_all_for_challenge(challenge_id)
        st.success("✅ All submissions reset to pending. They will be rescored when ground truth is available.")
        st.rerun()
    
    # Delete challenge
    if st.button("🗑️ Delete Challenge", type="secondary"):
        if st.checkbox("I understand this will permanently delete the challenge and all submissions"):
            if st.button("Confirm Delete", type="primary"):
                from database.models import delete_challenge
                delete_challenge(challenge_id)
                st.success("✅ Challenge deleted!")
                st.switch_page("pages/admin_dashboard.py")

# ─── TAB 2: Ground Truth ──────────────────────────────────────────────────────
with tab2:
    st.subheader("📤 Ground Truth CSV")
    st.markdown("Upload the correct answers/labels for this challenge. "
                "This file is **kept private** and is only used for scoring submissions.")

    existing_gt = get_ground_truth(challenge_id)
    if existing_gt:
        st.success(f"✅ Ground truth uploaded on {format_timestamp(existing_gt['uploaded_at'])}")
        if Path(existing_gt["storage_path"]).exists():
            gt_df, _ = read_csv_safe(existing_gt["storage_path"])
            if gt_df is not None:
                st.markdown("**Preview:**")
                st.dataframe(gt_df.head(), use_container_width=True)
                st.markdown(f"**Rows:** {len(gt_df)} | **Columns:** {', '.join(gt_df.columns)}")

    # Show expected format
    scorer = get_scorer(challenge["type"])
    if challenge["type"] != "code_challenge":
        with st.expander("📋 Required Ground Truth Format"):
            req_cols = scorer.required_ground_truth_columns
            id_col_example = {
                "classification": "image_id",
                "regression": "id",
                "rag": "question_id",
                "llm": "question_id",
            }
            example_id = id_col_example.get(challenge["type"], "id")
            st.markdown(f"**Required columns:** `{example_id}` (ID column) + `{', '.join(req_cols)}`")

    uploaded_gt = st.file_uploader(
        "Upload Ground Truth CSV",
        type=["csv"],
        key="gt_upload",
    )

    if uploaded_gt is not None:
        df, error = read_csv_safe(uploaded_gt)
        if error:
            st.error(f"❌ {error}")
        else:
            # Validate
            is_valid, val_error = validate_ground_truth_csv(df, scorer)
            if not is_valid:
                st.error(f"❌ {val_error}")
            else:
                st.success("✅ Ground truth CSV looks valid!")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("📤 Upload Ground Truth", type="primary"):
                    ensure_dirs()
                    storage_path = save_uploaded_file(uploaded_gt, challenge_id, file_type="ground_truth")
                    upload_ground_truth(challenge_id, storage_path)

                    # Score any pending submissions
                    pending = get_pending_submissions(challenge_id)
                    for sub in pending:
                        try:
                            sub_df, _ = read_csv_safe(sub["storage_path"])
                            if sub_df is not None:
                                metrics = scorer.score(sub_df, df)
                                primary_score = metrics.get("primary_score", 0.0)
                                from database.models import update_submission_score
                                update_submission_score(sub["id"], metrics, primary_score)
                        except Exception as e:
                            from database.models import update_submission_score
                            update_submission_score(sub["id"], {}, 0.0, "error", str(e))

                    st.success(f"✅ Ground truth uploaded and {len(pending)} pending submission(s) scored!")
                    st.rerun()

# ─── TAB 3: Submissions ───────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 All Submissions")

    all_subs = get_all_submissions_for_challenge(challenge_id)

    if not all_subs:
        st.info("No submissions yet.")
    else:
        for sub in all_subs:
            with st.container(border=True):
                cols = st.columns([2, 1, 1, 1, 1])
                with cols[0]:
                    st.markdown(f"**{sub['name']}** ({sub['email']})")
                with cols[1]:
                    st.markdown(f"**{format_timestamp(sub['uploaded_at'])}**")
                with cols[2]:
                    status = sub["status"]
                    if status == "scored":
                        st.success("✅ Scored")
                    elif status == "pending":
                        st.info("⏳ Pending")
                    elif status == "error":
                        st.error("❌ Error")

                with cols[3]:
                    score = sub.get("primary_score") or sub.get("manual_score")
                    st.markdown(f"**Score:** {format_score(score) if score else 'N/A'}")

                with cols[4]:
                    # Delete button
                    if st.button("🗑️ Delete", key=f"del_{sub['id']}"):
                        # Get user_id and submission_id to properly handle
                        sub_id = sub["id"]
                        sub_record = get_submission(sub_id)
                        if sub_record:
                            delete_submission(sub_id)
                            st.success(f"✅ Submission deleted for {sub['name']}")
                            st.rerun()

                # Manual scoring for code challenges
                if challenge["type"] == "code_challenge":
                    with st.expander(f"✏️ Manual Score for {sub['name']}"):
                        with st.form(key=f"manual_score_form_{sub['id']}"):
                            manual_score = st.slider(
                                "Score (0-100)",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(sub.get("manual_score") or 50.0),
                                step=0.5,
                            )
                            manual_feedback = st.text_area(
                                "Feedback",
                                value=sub.get("manual_feedback") or "",
                                placeholder="Provide feedback to the student...",
                            )
                            save_score = st.form_submit_button("💾 Save Score", type="primary")
                            if save_score:
                                update_manual_score(sub["id"], manual_score, manual_feedback)
                                st.success(f"✅ Score saved for {sub['name']}: {manual_score}")
                                st.rerun()

                # Show metrics
                if sub.get("metrics_json"):
                    metrics = json.loads(sub["metrics_json"]) if isinstance(sub["metrics_json"], str) else sub["metrics_json"]
                    with st.expander("📊 View Metrics"):
                        display_metrics(metrics)

                # Show error
                if sub.get("error_message"):
                    st.error(f"Error: {sub['error_message']}")

# ─── TAB 4: Leaderboard ───────────────────────────────────────────────────────
with tab4:
    st.subheader("🏆 Leaderboard")

    leaderboard = get_leaderboard(challenge_id)

    if not leaderboard:
        st.info("No submissions yet.")
    else:
        lb_df = pd.DataFrame(leaderboard)
        lb_df["score"] = lb_df["score"].apply(lambda x: format_score(x) if x is not None else "N/A")
        lb_df["submitted_at"] = lb_df["submitted_at"].apply(format_timestamp)
        lb_df = lb_df[["rank", "name", "email", "score", "submitted_at", "status"]]
        lb_df.columns = ["Rank", "Name", "Email", "Score", "Submitted At", "Status"]
        
        st.dataframe(lb_df, use_container_width=True, hide_index=True)

        # Download as CSV
        csv_data = lb_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Leaderboard CSV",
            data=csv_data,
            file_name=f"leaderboard_challenge_{challenge_id}.csv",
            mime="text/csv",
        )