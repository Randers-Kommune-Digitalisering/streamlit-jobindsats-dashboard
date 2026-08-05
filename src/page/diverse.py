import streamlit as st
from utils.database_connection import get_jobindsats_db
import streamlit_antd_components as sac
from graphs.aarshjul import aarshjul
from graphs.arbejdspligt import arbejdspligt

db_client = get_jobindsats_db()


def get_politisk_betjening_overview():
    st.title("Diverse statistikker")

    with st.sidebar:
        st.markdown("## Diverse statistikker")

        samling = sac.tree(
            items=[
                sac.TreeItem("Årshjulsdokumenter"),
                sac.TreeItem("Arbejdspligt")
            ],
            index=0,
            size="lg",
            open_all=False,
            checkbox=False,
            show_line=False,
            icon=None,
            color='#4a4a4a'
        )

    if samling is None:
        st.subheader("Vælg en underside i menuen til venstre")
    elif samling == "Årshjulsdokumenter":
            aarshjul()
    elif samling == "Arbejdspligt":
            arbejdspligt()