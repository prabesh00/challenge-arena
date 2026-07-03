"""
Challenge Arena - Authentication Module
Lightweight session-based auth for students and admin.
"""

import streamlit as st
import hashlib
import os


def check_admin_password(password):
    """Verify the admin password against the secret."""
    admin_pass = os.environ.get("ADMIN_PASSWORD") or st.secrets.get("admin_password", "")
    return password == admin_pass


def login_admin(password):
    """Attempt admin login. Returns True if successful."""
    if check_admin_password(password):
        st.session_state["admin_logged_in"] = True
        return True
    return False


def logout_admin():
    """Log out the admin."""
    st.session_state["admin_logged_in"] = False
    if "admin_logged_in" in st.session_state:
        del st.session_state["admin_logged_in"]


def is_admin_logged_in():
    """Check if admin is logged in."""
    return st.session_state.get("admin_logged_in", False)


def require_admin():
    """Redirect to admin login if not authenticated."""
    if not is_admin_logged_in():
        st.switch_page("pages/admin_login.py")
        st.stop()


# ─── Student Auth ──────────────────────────────────────────────────────────────

def login_student(user_id, name, email):
    """Store student session info."""
    st.session_state["student_id"] = user_id
    st.session_state["student_name"] = name
    st.session_state["student_email"] = email


def logout_student():
    """Log out the student."""
    if "student_id" in st.session_state:
        del st.session_state["student_id"]
    if "student_name" in st.session_state:
        del st.session_state["student_name"]
    if "student_email" in st.session_state:
        del st.session_state["student_email"]


def is_student_logged_in():
    """Check if a student is logged in."""
    return st.session_state.get("student_id") is not None


def get_current_student_id():
    """Get the current student's user ID."""
    return st.session_state.get("student_id")


def get_current_student_name():
    """Get the current student's name."""
    return st.session_state.get("student_name")


def require_student():
    """Redirect to login if not authenticated as student."""
    if not is_student_logged_in():
        st.switch_page("pages/login.py")
        st.stop()