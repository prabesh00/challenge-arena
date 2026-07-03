"""
Challenge Arena - QR Code Generation Page
Generate QR codes for student join links.
"""

import streamlit as st
from auth.auth import require_admin, is_admin_logged_in, logout_admin

require_admin()

st.set_page_config(page_title="Challenge Arena - QR Code", page_icon="📱")

with st.sidebar:
    st.markdown("### 🔐 Admin Panel")
    if st.button("📊 Dashboard"):
        st.switch_page("pages/admin_dashboard.py")
    if st.button("🚪 Logout"):
        logout_admin()
        st.rerun()

st.title("📱 QR Code - Student Join Link")
st.markdown("Generate a QR code that students can scan to join Challenge Arena.")

# Get the app's base URL
st.info("""
**How to get your app URL:**
1. Deploy your app on Streamlit Community Cloud
2. Copy the URL (e.g., https://challenge-arena.streamlit.app)
3. Enter it below
""")

base_url = st.text_input(
    "App Base URL",
    placeholder="https://challenge-arena.streamlit.app",
    help="The full URL where your app is deployed",
)

cohort = st.text_input(
    "Cohort Code",
    value="default",
    help="Optional cohort code to track which group of students this QR is for",
)

if base_url and cohort:
    join_url = f"{base_url.rstrip('/')}/login?cohort={cohort}"

    st.markdown("---")
    st.markdown(f"**Join URL:** `{join_url}`")

    # Generate QR code
    try:
        import qrcode
        from PIL import Image
        import io

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(join_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes for display
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # Display QR code (centered, large)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(buf, caption=f"Scan to Join - Cohort: {cohort}", use_container_width=True)

        # Download button
        st.download_button(
            label="📥 Download QR Code (PNG)",
            data=buf.getvalue(),
            file_name=f"challenge_arena_qr_{cohort}.png",
            mime="image/png",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("### 📋 Instructions for Students")
        st.markdown("""
        1. Open your phone's camera app
        2. Point it at the QR code
        3. Tap the notification/link that appears
        4. Enter your name and email
        5. Start submitting solutions!
        """)

    except ImportError:
        st.error("QR code library not installed. Run: `pip install qrcode pillow`")
    except Exception as e:
        st.error(f"Error generating QR code: {str(e)}")
else:
    st.info("👆 Enter your app URL and cohort code above to generate the QR code.")