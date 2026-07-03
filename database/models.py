"""
Challenge Arena - Data Models & CRUD Operations
All database interaction logic.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from .db import get_connection

DATA_DIR = Path(__file__).parent.parent / "data"


# ─── User Operations ───────────────────────────────────────────────────────────

def create_user(name, email, role="student", cohort=None):
    """Create a new user. Returns the user dict or None if email exists."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, role, cohort) VALUES (?, ?, ?, ?)",
            (name, email, role, cohort)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return get_user(user_id)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user(user_id):
    """Get a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email):
    """Get a user by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students(cohort=None):
    """Get all students, optionally filtered by cohort."""
    conn = get_connection()
    cursor = conn.cursor()
    if cohort:
        cursor.execute("SELECT * FROM users WHERE role = 'student' AND cohort = ? ORDER BY name", (cohort,))
    else:
        cursor.execute("SELECT * FROM users WHERE role = 'student' ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Challenge Operations ──────────────────────────────────────────────────────

def create_challenge(title, description_md, challenge_type, primary_metric, is_open=0, deadline=None):
    """Create a new challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO challenges (title, description_md, type, primary_metric, is_open, deadline)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description_md, challenge_type, primary_metric, is_open, deadline)
    )
    conn.commit()
    challenge_id = cursor.lastrowid
    conn.close()
    return get_challenge(challenge_id)


def get_challenge(challenge_id):
    """Get a challenge by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_challenges(include_closed=False):
    """Get all challenges, optionally including closed ones."""
    conn = get_connection()
    cursor = conn.cursor()
    if include_closed:
        cursor.execute("SELECT * FROM challenges ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM challenges WHERE is_open = 1 ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_challenge(challenge_id, **kwargs):
    """Update challenge fields. Pass only the fields to update."""
    allowed = ["title", "description_md", "type", "primary_metric", "is_open", "deadline"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_challenge(challenge_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [challenge_id]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE challenges SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return get_challenge(challenge_id)


def delete_challenge(challenge_id):
    """Delete a challenge and all associated files."""
    challenge = get_challenge(challenge_id)
    if not challenge:
        return False

    # Remove challenge data directory
    challenge_dir = DATA_DIR / "challenges" / str(challenge_id)
    if challenge_dir.exists():
        shutil.rmtree(challenge_dir)

    # Remove ground truth
    gt_dir = DATA_DIR / "ground_truth"
    gt_file = gt_dir / f"{challenge_id}.csv"
    if gt_file.exists():
        os.remove(gt_file)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM challenges WHERE id = ?", (challenge_id,))
    conn.commit()
    conn.close()
    return True


# ─── Resource Operations ───────────────────────────────────────────────────────

def add_resource(challenge_id, filename, storage_path):
    """Add a downloadable resource to a challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO challenge_resources (challenge_id, filename, storage_path) VALUES (?, ?, ?)",
        (challenge_id, filename, storage_path)
    )
    conn.commit()
    resource_id = cursor.lastrowid
    conn.close()
    return resource_id


def get_resources(challenge_id):
    """Get all resources for a challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM challenge_resources WHERE challenge_id = ?", (challenge_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_resource(resource_id):
    """Delete a resource."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT storage_path FROM challenge_resources WHERE id = ?", (resource_id,))
    row = cursor.fetchone()
    if row:
        path = row["storage_path"]
        if os.path.exists(path):
            os.remove(path)
    cursor.execute("DELETE FROM challenge_resources WHERE id = ?", (resource_id,))
    conn.commit()
    conn.close()


# ─── Ground Truth Operations ───────────────────────────────────────────────────

def upload_ground_truth(challenge_id, storage_path):
    """Upload or replace ground truth for a challenge."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if ground truth already exists
    cursor.execute("SELECT id, storage_path FROM ground_truths WHERE challenge_id = ?", (challenge_id,))
    existing = cursor.fetchone()

    if existing:
        # Remove old file
        if os.path.exists(existing["storage_path"]):
            os.remove(existing["storage_path"])
        cursor.execute(
            "UPDATE ground_truths SET storage_path = ?, uploaded_at = CURRENT_TIMESTAMP WHERE challenge_id = ?",
            (storage_path, challenge_id)
        )
    else:
        cursor.execute(
            "INSERT INTO ground_truths (challenge_id, storage_path) VALUES (?, ?)",
            (challenge_id, storage_path)
        )

    conn.commit()
    conn.close()
    return True


def get_ground_truth(challenge_id):
    """Get ground truth info for a challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ground_truths WHERE challenge_id = ?", (challenge_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Submission Operations ─────────────────────────────────────────────────────

def create_submission(challenge_id, user_id, storage_path):
    """Create a new submission. Marks previous active submissions as inactive."""
    conn = get_connection()
    cursor = conn.cursor()

    # Deactivate previous active submissions for this user+challenge
    cursor.execute(
        """UPDATE submissions SET is_active_for_ranking = 0
           WHERE challenge_id = ? AND user_id = ? AND is_active_for_ranking = 1""",
        (challenge_id, user_id)
    )

    # Save old submission to history before deactivating
    cursor.execute(
        """SELECT id, challenge_id, user_id, storage_path, uploaded_at, metrics_json, primary_score, status
           FROM submissions WHERE challenge_id = ? AND user_id = ? AND is_active_for_ranking = 0
           AND id NOT IN (SELECT submission_id FROM submission_history WHERE challenge_id = ? AND user_id = ?)""",
        (challenge_id, user_id, challenge_id, user_id)
    )
    old_submissions = cursor.fetchall()
    for old in old_submissions:
        cursor.execute(
            """INSERT INTO submission_history (submission_id, challenge_id, user_id, storage_path, uploaded_at, metrics_json, primary_score, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (old["id"], old["challenge_id"], old["user_id"], old["storage_path"],
             old["uploaded_at"], old["metrics_json"], old["primary_score"], old["status"])
        )

    # Create new submission
    cursor.execute(
        """INSERT INTO submissions (challenge_id, user_id, storage_path, is_active_for_ranking, status)
           VALUES (?, ?, ?, 1, 'pending')""",
        (challenge_id, user_id, storage_path)
    )
    conn.commit()
    submission_id = cursor.lastrowid
    conn.close()
    return submission_id


def get_submission(submission_id):
    """Get a submission by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_submission(challenge_id, user_id):
    """Get the active submission for a user on a challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM submissions
           WHERE challenge_id = ? AND user_id = ? AND is_active_for_ranking = 1
           ORDER BY uploaded_at DESC LIMIT 1""",
        (challenge_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_submissions_for_challenge(challenge_id):
    """Get all active submissions for a challenge (for leaderboard)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT s.*, u.name, u.email
           FROM submissions s
           JOIN users u ON s.user_id = u.id
           WHERE s.challenge_id = ? AND s.is_active_for_ranking = 1
           ORDER BY s.primary_score DESC, s.uploaded_at ASC""",
        (challenge_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_submission_history_for_user(challenge_id, user_id):
    """Get all submissions (active + history) for a user on a challenge."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get active submissions
    cursor.execute(
        """SELECT id, challenge_id, user_id, storage_path, uploaded_at, metrics_json,
                  primary_score, status, error_message, manual_score, manual_feedback
           FROM submissions
           WHERE challenge_id = ? AND user_id = ? AND is_active_for_ranking = 1
           ORDER BY uploaded_at DESC""",
        (challenge_id, user_id)
    )
    active = [dict(r) for r in cursor.fetchall()]

    # Get history
    cursor.execute(
        """SELECT id, challenge_id, user_id, storage_path, uploaded_at, metrics_json,
                  primary_score, status, NULL as error_message, NULL as manual_score, NULL as manual_feedback
           FROM submission_history
           WHERE challenge_id = ? AND user_id = ?
           ORDER BY uploaded_at DESC""",
        (challenge_id, user_id)
    )
    history = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return active + history


def update_submission_score(submission_id, metrics_json, primary_score, status="scored", error_message=None):
    """Update a submission with scoring results."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE submissions
           SET metrics_json = ?, primary_score = ?, status = ?, error_message = ?
           WHERE id = ?""",
        (json.dumps(metrics_json), primary_score, status, error_message, submission_id)
    )
    conn.commit()
    conn.close()


def update_manual_score(submission_id, manual_score, manual_feedback):
    """Update a submission with manual scoring (for code challenges)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE submissions
           SET manual_score = ?, manual_feedback = ?, primary_score = ?, status = 'scored'
           WHERE id = ?""",
        (manual_score, manual_feedback, manual_score, submission_id)
    )
    conn.commit()
    conn.close()


def delete_submission(submission_id):
    """Delete a submission and its file."""
    submission = get_submission(submission_id)
    if not submission:
        return False

    # Remove file
    if os.path.exists(submission["storage_path"]):
        os.remove(submission["storage_path"])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM submissions WHERE id = ?", (submission_id,))
    conn.commit()
    conn.close()
    return True


def get_pending_submissions(challenge_id=None):
    """Get all pending submissions, optionally for a specific challenge."""
    conn = get_connection()
    cursor = conn.cursor()
    if challenge_id:
        cursor.execute(
            "SELECT * FROM submissions WHERE challenge_id = ? AND status = 'pending'",
            (challenge_id,)
        )
    else:
        cursor.execute("SELECT * FROM submissions WHERE status = 'pending'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def rescore_all_for_challenge(challenge_id):
    """Reset all scored submissions to pending for rescoring."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE submissions SET status = 'pending', metrics_json = NULL, primary_score = NULL WHERE challenge_id = ?",
        (challenge_id,)
    )
    conn.commit()
    conn.close()


# ─── Leaderboard Operations ────────────────────────────────────────────────────

def get_leaderboard(challenge_id):
    """Get the leaderboard for a challenge."""
    submissions = get_all_submissions_for_challenge(challenge_id)
    leaderboard = []
    for i, sub in enumerate(submissions, 1):
        leaderboard.append({
            "rank": i,
            "name": sub["name"],
            "email": sub["email"],
            "score": sub["primary_score"] if sub["primary_score"] is not None else sub.get("manual_score"),
            "submitted_at": sub["uploaded_at"],
            "status": sub["status"],
        })
    return leaderboard


def get_student_rank(challenge_id, user_id):
    """Get a student's rank on a challenge."""
    leaderboard = get_leaderboard(challenge_id)
    for entry in leaderboard:
        # Find by user_id from the submission
        sub = get_active_submission(challenge_id, user_id)
        if sub and entry["email"] == get_user(user_id)["email"]:
            return entry["rank"]
    return None