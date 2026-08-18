import streamlit as st
import plotly.graph_objects as go

fig = go.Figure()
fig.add_scatter(y=[1, 2, 3, 4])

st.title("Plotly Test")
st.plotly_chart(fig)
