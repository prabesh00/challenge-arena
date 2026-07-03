"""
Challenge Arena - Student Login/Registration Page
"""

import streamlit as st
from database.models import create_user, get_user_by_email
from auth.auth import login_student, is_student_logged_in, logout_student

st.set_page_config(page_title="Challenge Arena - Join", page_icon="🎯")

st.title("🎯 Challenge Arena")
st.markdown("### Join the Challenge")

# Check if already logged in
if is_student_logged_in():
    st.success(f"✅ You're logged in as **{st.session_state.get('student_name')}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 View Challenges"):
            st.switch_page("pages/challenges.py")
    with col2:
        if st.button("🚪 Logout"):
            logout_student()
            st.rerun()
    st.stop()

# Get cohort from URL parameters or use default
query_params = st.query_params
cohort = query_params.get("cohort", "default")

st.markdown(f"""
Welcome to **Challenge Arena**! 
Register with your name and email to participate.
""")

with st.form("register_form"):
    name = st.text_input("Full Name", placeholder="e.g., John Doe")
    email = st.text_input("Email", placeholder="e.g., john@example.com")
    cohort_input = st.text_input(
        "Cohort Code",
        value=cohort,
        help="Enter the cohort code provided by your instructor"
    )
    submitted = st.form_submit_button("🚀 Join Challenge Arena", use_container_width=True)

    if submitted:
        if not name or not email:
            st.error("Please enter both your name and email.")
        else:
            # Check if user already exists
            existing_user = get_user_by_email(email)
            if existing_user:
                if existing_user["role"] == "student":
                    login_student(existing_user["id"], existing_user["name"], existing_user["email"])
                    st.success(f"Welcome back, {existing_user['name']}! 🎉")
                    st.rerun()
                else:
                    st.error("This email is registered as an admin. Please use a different email.")
            else:
                # Create new user
                user = create_user(name=name, email=email, role="student", cohort=cohort_input or cohort)
                if user:
                    login_student(user["id"], user["name"], user["email"])
                    st.success(f"Welcome to Challenge Arena, {user['name']}! 🎉")
                    st.rerun()
                else:
                    st.error("Could not create account. Please try again.")

st.markdown("---")
st.markdown("👤 **Already registered?** Enter your email above and click Join to log back in.")