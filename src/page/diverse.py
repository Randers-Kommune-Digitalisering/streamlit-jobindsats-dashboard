import streamlit as st
from utils.database_connection import get_jobindsats_db
import streamlit_antd_components as sac
from graphs.aarshjul import aarshjul
from graphs.arbejdspligt import arbejdspligt

db_client = get_jobindsats_db()


def get_diverse(samling):
    try:
        if samling is None:
            st.subheader("Vælg en underside i menuen til venstre")
        elif samling == "Årshjulsdokumenter":
                aarshjul()
        elif samling == "Arbejdspligt":
                arbejdspligt()

    except Exception as e:
        st.error(f'Fejl ved loading: {e}')