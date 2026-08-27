# modules/utils/crud.py
import streamlit as st

def crud_table(data_key, item_name, endpoint, id_field="id", display_fields=None, edit_fields=None, add_fields=None):
    data = st.session_state.get(data_key, [])
    if not data:
        st.info(f"No {item_name} data available.")
        return
    if display_fields is None:
        display_fields = list(data[0].keys()) if data else []
    for idx, item in enumerate(data):
        cols = st.columns([2] * len(display_fields) + [1, 1])
        for i, field in enumerate(display_fields):
            with cols[i]:
                st.write(item.get(field, ''))
        with cols[-2]:
            if st.button("✏️", key=f"edit_{item_name}_{item[id_field]}"):
                st.session_state[f"editing_{item_name}"] = item
        with cols[-1]:
            if st.button("🗑️", key=f"del_{item_name}_{item[id_field]}"):
                if st.checkbox(f"Confirm delete?", key=f"confirm_{item_name}_{item[id_field]}"):
                    new_data = [d for d in data if d[id_field] != item[id_field]]
                    st.session_state[data_key] = new_data
                    st.success(f"{item_name.capitalize()} deleted!")
                    st.rerun()
        editing_key = f"editing_{item_name}"
        if editing_key in st.session_state and st.session_state[editing_key] is not None:
            editing_item = st.session_state[editing_key]
            if isinstance(editing_item, dict) and editing_item.get(id_field) == item.get(id_field):
                with st.expander(f"Edit {item.get('name', item.get('level', ''))}", expanded=True):
                    with st.form(key=f"edit_{item_name}_form_{item[id_field]}"):
                        edit_values = {}
                        if edit_fields is None:
                            edit_fields = {field: "text" for field in display_fields}
                        for field, input_type in edit_fields.items():
                            if input_type == "text":
                                edit_values[field] = st.text_input(field.capitalize(), value=item.get(field, ''))
                            elif input_type == "number":
                                edit_values[field] = st.number_input(field.capitalize(), value=item.get(field, 0.0), step=0.1)
                            elif input_type == "select":
                                options = item.get('options', [])
                                current = item.get(field, options[0] if options else '')
                                edit_values[field] = st.selectbox(field.capitalize(), options, index=options.index(current) if current in options else 0)
                        if st.form_submit_button("Update"):
                            for d in data:
                                if d[id_field] == item[id_field]:
                                    for k, v in edit_values.items():
                                        d[k] = v
                                    break
                            st.session_state[data_key] = data
                            st.success(f"{item_name.capitalize()} updated!")
                            st.session_state[editing_key] = None
                            st.rerun()
                if st.button("Cancel", key=f"cancel_{item_name}_edit_{item[id_field]}"):
                    st.session_state[editing_key] = None
                    st.rerun()
    with st.expander(f"➕ Add New {item_name.capitalize()}"):
        with st.form(key=f"new_{item_name}_form"):
            add_values = {}
            add_fields_to_use = add_fields if add_fields is not None else edit_fields
            if add_fields_to_use is None:
                add_fields_to_use = {field: "text" for field in display_fields}
            for field, input_type in add_fields_to_use.items():
                if input_type == "text":
                    add_values[field] = st.text_input(field.capitalize())
                elif input_type == "number":
                    add_values[field] = st.number_input(field.capitalize(), value=0.0, step=0.1)
                elif input_type == "select":
                    options = data[0].get('options', []) if data else []
                    add_values[field] = st.selectbox(field.capitalize(), options)
            if st.form_submit_button("Create"):
                new_id = max([d[id_field] for d in data]) + 1 if data else 1
                add_values[id_field] = new_id
                data.append(add_values)
                st.session_state[data_key] = data
                st.success(f"{item_name.capitalize()} created!")
                st.rerun()
