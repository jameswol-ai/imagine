import streamlit as st

def render():
    st.subheader("Site Planning")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Site Area (m²)", value=5000)
        st.slider("Slope (%)", 0, 20, 5)
    with col2:
        st.selectbox("Soil Type", ["Clay", "Sand", "Rock"])
        st.selectbox("Orientation", ["North", "South", "East", "West"])
    if st.button("Generate Site Layout"):
        st.success("Site layout generated (mock).")
        st.info("Visualization placeholder – would show site plan.")