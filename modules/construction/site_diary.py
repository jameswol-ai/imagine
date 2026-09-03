"""Site diary and daily field record workspace."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st


class SiteDiaryService:
    @staticmethod
    def create_entry(project_code: str, author: str, notes: str, weather: str = "Not recorded", temperature: float = 0.0) -> dict:
        if not project_code.strip() or not author.strip() or not notes.strip():
            raise ValueError("Project, author and notes are required")
        return {"project_code": project_code.strip(), "author": author.strip(), "notes": notes.strip(), "weather": weather, "temperature": temperature, "created_at": datetime.now(timezone.utc).isoformat()}

    @staticmethod
    def weather_record(condition: str, temperature: float) -> dict:
        return {"weather": condition, "temperature": temperature}


def render() -> None:
    st.subheader("Site Diaries")
    st.caption("Daily site record for field notes, weather and basic project traceability.")
    if "site_diary_rows" not in st.session_state:
        st.session_state.site_diary_rows = []
    with st.form("site_diary_form"):
        a, b = st.columns(2)
        project = a.text_input("Project code", value="IMAGINE-001")
        author = b.text_input("Author")
        notes = st.text_area("Daily notes")
        c, d = st.columns(2)
        weather = c.selectbox("Weather", ["Sunny", "Cloudy", "Rain", "Storm", "Not recorded"])
        temperature = d.number_input("Temperature", value=25.0, step=1.0)
        add = st.form_submit_button("Add diary entry")
    if add:
        if not author.strip() or not notes.strip(): st.error("Author and daily notes are required.")
        else: st.session_state.site_diary_rows.append(SiteDiaryService.create_entry(project, author, notes, weather, temperature)); st.success("Diary entry added.")
    data = pd.DataFrame(st.session_state.site_diary_rows)
    if data.empty:
        st.info("No diary entries recorded yet.")
        return
    st.metric("Recorded entries", len(data))
    st.dataframe(data, use_container_width=True, hide_index=True)
