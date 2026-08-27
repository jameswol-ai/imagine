import streamlit as st

def render():
    st.header("🏛️ Buildings")

    # Initialize mock data store if not present
    if "buildings_data" not in st.session_state:
        st.session_state.buildings_data = []

    # Form to add a new building
    with st.form("add_building_form", clear_on_submit=True):
        name = st.text_input("Building Name")
        address = st.text_area("Address")
        submitted = st.form_submit_button("Add Building")

        if submitted and name:
            new_building = {"name": name, "address": address}
            st.session_state.buildings_data.append(new_building)
            st.success(f"Added building: {name}")

    # Display existing buildings
    if st.session_state.buildings_data:
        st.subheader("Existing Buildings")
        st.table(st.session_state.buildings_data)
    else:
        st.info("No buildings added yet.")