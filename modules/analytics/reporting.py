"""Project reporting workspace."""
from __future__ import annotations

from datetime import datetime, timezone
import json

import pandas as pd
import streamlit as st


class ReportingService:
    @staticmethod
    def generate_report(title: str, content: str) -> dict[str, str]:
        return {
            "title": title,
            "content": content,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def render() -> None:
    st.subheader("Reporting")
    st.caption("Generate a lightweight project report from current session data. This does not replace controlled project document production.")
    projects = st.session_state.get("projects_data", [])
    title = st.text_input("Report title", value="IMAGINE Project Report")
    default_content = f"Project records available: {len(projects)}."
    content = st.text_area("Executive summary", value=default_content, height=140)
    if st.button("Generate Report", type="primary", use_container_width=True):
        report = ReportingService.generate_report(title.strip() or "IMAGINE Project Report", content.strip())
        st.session_state["latest_imagine_report"] = report
    report = st.session_state.get("latest_imagine_report")
    if report:
        st.success("Report generated.")
        st.markdown(f"### {report['title']}")
        st.write(report["content"])
        st.caption(f"Generated {report['generated_at']}")
        payload = json.dumps(report, indent=2, ensure_ascii=False).encode("utf-8")
        st.download_button("Download JSON report", payload, "imagine_report.json", "application/json", use_container_width=True)
    if projects:
        st.subheader("Project data")
        st.dataframe(pd.DataFrame(projects), hide_index=True, use_container_width=True)


__all__ = ["ReportingService", "render"]
