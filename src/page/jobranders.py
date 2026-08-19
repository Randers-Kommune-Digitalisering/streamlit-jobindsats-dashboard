import streamlit as st
from utils.database_connection import get_jobindsats_db
from graphs.cjk import cjk_page
from graphs.cju import cju_page
from graphs.job_og_ressourcer import show_job_og_ressourcer_graph
from graphs.job_og_sundhed import show_job_og_sundhed_graph
from graphs.UUR import show_UUR_graph
from graphs.Job_og_lontimer import show_job_og_lontimer_graph
import streamlit_antd_components as sac

db_client = get_jobindsats_db()

def get_jobranders(afdeling):

    if afdeling is None:
        st.subheader("Vælg en afdeling i venstre side")
    else:
        if afdeling in ["Center for Job og Udvikling", "CJU - fælles mål"]:
            cju_page(afdeling)
        if afdeling == "CJK - fælles mål":
            cjk_page(afdeling)
        if afdeling == "Job og ressourcer":
            show_job_og_ressourcer_graph()

        elif afdeling == "UUR":
            show_UUR_graph()

        elif afdeling == "Job og løntimer":
            show_job_og_lontimer_graph()

        elif afdeling == "Job og sundhedd":
            show_job_og_sundhed_graph()
