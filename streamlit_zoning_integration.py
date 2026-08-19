# Add this import near the other page/module imports in streamlit_app.py:
from architecture.zoning.ui import render_zoning


# Inside the existing page_architecture() function, replace only the
# current Zoning tab body:
#
#     with tab_objects[1]:
#         st.subheader("Zoning & Land Use")
#         st.session_state.zoning_data = editable_table(
#             st.session_state.zoning_data,
#             "zoning_editor",
#         )
#
# with:
#
#     with tab_objects[1]:
#         render_zoning()
#
# The Architecture tab labels remain unchanged:
#
# ["Generative Design", "Zoning", "Site Planning",
#  "Floor Planning", "Room Programming", "Compliance"]
#
# Also remove the old `zoning_data` seed block from init_session_state()
# after the database-backed zoning module is verified.
