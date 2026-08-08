import streamlit as st
from auth import update_user_password

def render_change_password_ui():
    """Renders password update form with client-side validation."""
    st.subheader("🔑 Change Password")
    
    with st.form("change_password_form", clear_on_submit=True):
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Update Password", use_container_width=True)
        
        if submit:
            # Basic validation
            if not current_pw or not new_pw or not confirm_pw:
                st.error("Please fill in all fields.")
            elif new_pw != confirm_pw:
                st.error("New password and confirmation do not match.")
            elif len(new_pw) < 8:
                st.error("New password must be at least 8 characters long.")
            elif current_pw == new_pw:
                st.error("New password must be different from your current password.")
            else:
                username = st.session_state["user"]["username"]
                success, message = update_user_password(username, current_pw, new_pw)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Example Usage inside a User Profile / Settings Expander
if st.session_state.get("authenticated"):
    with st.expander("👤 User Account Settings"):
        st.write(f"Logged in as: **{st.session_state['user']['username']}**")
        st.divider()
        render_change_password_ui()
