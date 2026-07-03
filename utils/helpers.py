"""
Challenge Arena - Helper Utilities
File storage, formatting, and display helpers.
"""

import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_dirs():
    """Create required data directories."""
    dirs = [
        DATA_DIR / "challenges",
        DATA_DIR / "ground_truth",
        DATA_DIR / "submissions",
    ]
    for d in dirs:
        os.makedirs(str(d), exist_ok=True)


def save_uploaded_file(uploaded_file, challenge_id, user_id=None, file_type="submission"):
    """
    Save an uploaded file to the data directory.
    Returns the storage path.
    """
    ensure_dirs()

    if file_type == "ground_truth":
        dir_path = DATA_DIR / "ground_truth"
        filename = f"{challenge_id}.csv"
    elif file_type == "resource":
        dir_path = DATA_DIR / "challenges" / str(challenge_id) / "resources"
        os.makedirs(str(dir_path), exist_ok=True)
        filename = uploaded_file.name
    elif file_type == "submission":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        dir_path = DATA_DIR / "submissions" / str(challenge_id) / str(user_id)
        os.makedirs(str(dir_path), exist_ok=True)
        filename = f"{timestamp}_{unique_id}.csv"
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    storage_path = str(dir_path / filename)

    with open(storage_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return storage_path


def format_timestamp(timestamp_str):
    """Format a timestamp string for display."""
    if not timestamp_str:
        return "N/A"
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except ValueError:
        return timestamp_str


def format_score(score, decimal_places=4):
    """Format a score for display."""
    if score is None:
        return "N/A"
    return f"{score:.{decimal_places}f}"


def display_metrics(metrics_dict):
    """Display metrics in a formatted way."""
    if not metrics_dict:
        st.info("No metrics available.")
        return

    # Filter out internal keys (starting with _)
    display_metrics = {k: v for k, v in metrics_dict.items() if not k.startswith("_") and k != "primary_score"}

    for key, value in display_metrics.items():
        if isinstance(value, float):
            st.metric(label=key.replace("_", " ").title(), value=f"{value:.4f}")
        elif isinstance(value, int):
            st.metric(label=key.replace("_", " ").title(), value=str(value))
        elif isinstance(value, list) and key == "confusion_matrix":
            with st.expander("Confusion Matrix"):
                labels = metrics_dict.get("confusion_matrix_labels", [])
                st.write("Rows: True labels, Columns: Predicted labels")
                st.dataframe(value, use_container_width=True)
        elif isinstance(value, dict):
            with st.expander(key.replace("_", " ").title()):
                st.json(value)
        else:
            st.metric(label=key.replace("_", " ").title(), value=str(value))


def get_file_download_link(file_path, label="Download File"):
    """Get a markdown download link for a file."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rb") as f:
        data = f.read()

    filename = Path(file_path).name
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime="application/octet-stream",
    )