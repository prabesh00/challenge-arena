"""
Challenge Arena - Admin Login Page
"""

import streamlit as st
from auth.auth import login_admin, is_admin_logged_in, logout_admin

st.set_page_config(page_title="Challenge Arena - Admin Login", page_icon="🔐")

st.title("🔐 Admin Login")
st.markdown("### Instructor Access")

if is_admin_logged_in():
    st.success("✅ You are already logged in as admin.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Go to Dashboard"):
            st.switch_page("pages/admin_dashboard.py")
    with col2:
        if st.button("🚪 Logout"):
            logout_admin()
            st.rerun()
    st.stop()

with st.form("admin_login_form"):
    password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
    submitted = st.form_submit_button("🔑 Login", use_container_width=True)

    if submitted:
        if login_admin(password):
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password.")

st.markdown("---")
st.markdown("👤 **Students go to the [Student Login](pages/login.py) page.**")