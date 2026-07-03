"""
Challenge Arena - Challenge Detail Page
Students view challenge details, upload submissions, see history & leaderboard.
"""

import json
import streamlit as st
import pandas as pd
from pathlib import Path

from database.models import (
    get_challenge, get_active_submission, create_submission,
    get_submission_history_for_user, get_leaderboard,
    get_resources, get_ground_truth,
)
from auth.auth import require_student, get_current_student_id, get_current_student_name, logout_student
from scoring.registry import get_scorer
from utils.validation import validate_file_type, validate_file_size, read_csv_safe
from utils.helpers import save_uploaded_file, format_timestamp, format_score, display_metrics
from utils.memes import display_meme

require_student()

st.set_page_config(page_title="Challenge Arena - Challenge", page_icon="🎯")

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {get_current_student_name()}")
    if st.button("📋 All Challenges"):
        st.switch_page("pages/challenges.py")
    if st.button("🚪 Logout"):
        logout_student()
        st.rerun()

# Get challenge ID from session or query params
challenge_id = st.session_state.get("current_challenge_id") or st.query_params.get("challenge_id")

if not challenge_id:
    st.error("No challenge selected.")
    st.page_link("pages/challenges.py", label="← Back to Challenges")
    st.stop()

try:
    challenge_id = int(challenge_id)
except (ValueError, TypeError):
    st.error("Invalid challenge ID.")
    st.stop()

challenge = get_challenge(challenge_id)
if not challenge:
    st.error("Challenge not found.")
    st.page_link("pages/challenges.py", label="← Back to Challenges")
    st.stop()

user_id = get_current_student_id()

# ─── Challenge Header ──────────────────────────────────────────────────────────
type_icons = {
    "classification": "🔬", "regression": "📈",
    "rag": "📚", "llm": "🤖", "code_challenge": "💻",
}
icon = type_icons.get(challenge["type"], "📝")

st.title(f"{icon} {challenge['title']}")
st.markdown(f"**Type:** {challenge['type'].replace('_', ' ').title()} | "
            f"**Primary Metric:** {challenge['primary_metric'].replace('_', ' ').title()}")

if challenge.get("deadline"):
    st.markdown(f"⏰ **Deadline:** {challenge['deadline']}")

if not challenge["is_open"]:
    st.warning("🔒 Submissions are closed for this challenge.")

# ─── Challenge Description ─────────────────────────────────────────────────────
with st.expander("📖 Challenge Description", expanded=True):
    st.markdown(challenge["description_md"] or "*No description provided.*")

# ─── Downloadable Resources ────────────────────────────────────────────────────
resources = get_resources(challenge_id)
if resources:
    with st.expander("📎 Downloadable Resources"):
        for res in resources:
            res_path = res["storage_path"]
            if Path(res_path).exists():
                with open(res_path, "rb") as f:
                    st.download_button(
                        label=f"📥 {res['filename']}",
                        data=f,
                        file_name=res["filename"],
                        key=f"res_{res['id']}",
                    )
            else:
                st.warning(f"⚠️ {res['filename']} (file not found)")

# ─── Submission Form ───────────────────────────────────────────────────────────
if challenge["is_open"]:
    st.markdown("---")
    st.subheader("📤 Submit Your Solution")

    # Show expected columns based on challenge type
    scorer = get_scorer(challenge["type"])
    if challenge["type"] != "code_challenge":
        with st.expander("📋 Required CSV Format"):
            req_cols = scorer.required_submission_columns
            id_col_example = {
                "classification": "image_id",
                "regression": "id",
                "rag": "question_id",
                "llm": "question_id",
            }
            example_id = id_col_example.get(challenge["type"], "id")
            st.markdown(f"**Required columns:** `{example_id}` (ID column) + `{', '.join(req_cols)}`")
            st.markdown("**Example:**")
            example_data = {example_id: ["sample_1", "sample_2"], **{col: ["value1", "value2"] for col in req_cols}}
            st.dataframe(pd.DataFrame(example_data), use_container_width=True)

    uploaded_file = st.file_uploader(
        "Choose your submission CSV file",
        type=["csv"],
        help=f"Maximum file size: 10MB",
    )

    if uploaded_file is not None:
        # Validate file
        if not validate_file_type(uploaded_file.name):
            st.error("❌ Only CSV files are accepted.")
        elif not validate_file_size(uploaded_file.getvalue()):
            st.error("❌ File is too large. Maximum size is 10MB.")
        else:
            # Read CSV
            df, error = read_csv_safe(uploaded_file)
            if error:
                st.error(f"❌ {error}")
            else:
                # Validate against scorer
                is_valid, val_error = scorer.validate_submission(df)
                if not is_valid:
                    st.error(f"❌ {val_error}")
                else:
                    # Check ID mismatch if ground truth exists
                    gt = get_ground_truth(challenge_id)
                    if gt:
                        gt_df, _ = read_csv_safe(gt["storage_path"])
                        if gt_df is not None:
                            id_ok, id_error, _, _ = scorer.check_id_mismatch(df, gt_df)
                            if not id_ok:
                                st.warning(f"⚠️ {id_error}")

                    # Submit button
                    if st.button("✅ Submit Solution", type="primary", use_container_width=True):
                        storage_path = save_uploaded_file(uploaded_file, challenge_id, user_id, "submission")
                        submission_id = create_submission(challenge_id, user_id, storage_path)

                        # If ground truth exists, score immediately
                        if gt:
                            try:
                                gt_df, _ = read_csv_safe(gt["storage_path"])
                                if gt_df is not None:
                                    # Score
                                    metrics = scorer.score(df, gt_df)
                                    primary_score = metrics.get("primary_score", 0.0)
                                    from database.models import update_submission_score
                                    update_submission_score(submission_id, metrics, primary_score)
                                    st.success(f"✅ Submission scored! Score: {format_score(primary_score)}")
                                    # Show meme reaction based on score
                                    display_meme(primary_score, "Your Score")
                                else:
                                    st.info("⏳ Submission stored. Will be scored when ground truth is ready.")
                            except Exception as e:
                                from database.models import update_submission_score
                                update_submission_score(submission_id, {}, 0.0, "error", str(e))
                                st.error(f"❌ Scoring error: {str(e)}")
                        else:
                            st.info("⏳ Submission stored. Will be scored once the ground truth is uploaded.")

                        st.rerun()

# ─── Your Submission History ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("📜 Your Submission History")

history = get_submission_history_for_user(challenge_id, user_id)

if not history:
    st.info("You haven't submitted anything yet for this challenge.")

for sub in history:
    with st.container(border=True):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{format_timestamp(sub['uploaded_at'])}**")
        with cols[1]:
            status = sub["status"]
            if status == "scored":
                st.success("✅ Scored")
            elif status == "pending":
                st.info("⏳ Pending")
            elif status == "error":
                st.error("❌ Error")
        with cols[2]:
            if sub["primary_score"] is not None:
                st.markdown(f"**Score:** {format_score(sub['primary_score'])}")
            elif sub.get("manual_score") is not None:
                st.markdown(f"**Score:** {format_score(sub['manual_score'])}")
            else:
                st.markdown("**Score:** N/A")
        with cols[3]:
            if sub.get("is_active_for_ranking"):
                st.markdown("🏆 **Active**")

        # Show metrics if scored
        if sub.get("metrics_json"):
            metrics = json.loads(sub["metrics_json"]) if isinstance(sub["metrics_json"], str) else sub["metrics_json"]
            with st.expander("📊 View Metrics"):
                display_metrics(metrics)

        # Show error if any
        if sub.get("error_message"):
            st.error(f"Error: {sub['error_message']}")

# ─── Leaderboard ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 Leaderboard")

leaderboard = get_leaderboard(challenge_id)

if not leaderboard:
    st.info("No submissions yet. Be the first!")
else:
    lb_df = pd.DataFrame(leaderboard)
    
    # Highlight current user
    current_email = st.session_state.get("student_email")
    
    # Style the dataframe
    def highlight_user(row):
        if row["email"] == current_email:
            return ["background-color: #e8f4fd; font-weight: bold"] * len(row)
        return [""] * len(row)

    # Display columns
    display_df = lb_df[["rank", "name", "score", "submitted_at"]].copy()
    display_df["score"] = display_df["score"].apply(lambda x: format_score(x) if x is not None else "N/A")
    display_df["submitted_at"] = display_df["submitted_at"].apply(format_timestamp)
    display_df.columns = ["Rank", "Name", "Score", "Submitted At"]
    
    st.dataframe(
        display_df.style.apply(highlight_user, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    # Show user's rank
    user_sub = get_active_submission(challenge_id, user_id)
    if user_sub:
        for entry in leaderboard:
            if entry["email"] == current_email:
                st.markdown(f"### 🎯 Your Rank: #{entry['rank']} / {len(leaderboard)}")
                break