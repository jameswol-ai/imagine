import streamlit as st
from admin_backend import get_all_users, admin_reset_password, admin_update_role

def render_admin_panel():
    # Enforce access control guard
    current_user = st.session_state.get("user", {})
    if current_user.get("role") != "Admin":
        st.error("⛔ Access Denied: Admin privileges required.")
        return

    st.title("🛠️ Admin User Management")

    # 1. Roster Overview
    users_df = get_all_users()
    st.subheader("Current User Accounts")
    st.dataframe(users_df, use_container_width=True, hide_index=True)

    if users_df.empty:
        st.info("No users found.")
        return

    st.divider()

    # 2. User Selector & Actions
    usernames = users_df["username"].tolist()
    selected_user = st.selectbox("Select User to Manage", usernames)
    current_role = users_df[users_df["username"] == selected_user]["role"].values[0]

    col1, col2 = st.columns(2)

    # Action A: Override Password
    with col1:
        st.subheader("🔑 Reset Password")
        with st.form("admin_reset_pw_form", clear_on_submit=True):
            temp_password = st.text_input("New Password", type="password")
            submit_pw = st.form_submit_button("Reset Password", use_container_width=True)

            if submit_pw:
                if len(temp_password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    success, msg = admin_reset_password(selected_user, temp_password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    # Action B: Modify Role
    with col2:
        st.subheader("🛡️ Change Role")
        with st.form("admin_role_form"):
            roles = ["Admin", "Project Manager", "Lead Engineer", "Junior Inspector", "Viewer"]
            default_index = roles.index(current_role) if current_role in roles else 0
            
            new_role = st.selectbox("Assigned Role", roles, index=default_index)
            submit_role = st.form_submit_button("Update Role", use_container_width=True)

            if submit_role:
                if new_role == current_role:
                    st.warning("User already holds this role.")
                else:
                    success, msg = admin_update_role(selected_user, new_role)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# Navigation Hook
if st.session_state.get("authenticated"):
    render_admin_panel()
