import streamlit as st
import requests
import pandas as pd
import altair as alt
from io import BytesIO
import plotly.express as px
from streamlit_option_menu import option_menu
from utils.database_connection import get_jobindsats_db
from graphs.job_og_ressourcer import show_job_og_ressourcer_graph
from graphs.job_og_sundhed import show_job_og_sundhed_graph
from graphs.UUR import show_UUR_graph
from graphs.Job_og_lontimer import show_job_og_lontimer_graph
import streamlit_antd_components as sac

db_client = get_jobindsats_db()


def get_jobcenter_randers_overview():
    with st.sidebar:
        st.markdown("## Jobcenter Randers")

        afdeling = sac.tree(
            items=[
                sac.TreeItem("Center for Job og Udvikling", children=[
                    sac.TreeItem("Job og løntimer"),
                    sac.TreeItem("Job og ressourcer"),
                    sac.TreeItem("Job og sundhedd"),
                    sac.TreeItem("UUR")
                ]),
                sac.TreeItem("Center for Job og Kompetencer")
            ],
            index=0,
            size="lg",
            open_all=False,
            checkbox=False,
            show_line=False,
            icon=None,
            color='#4a4a4a'
        )




    st.title("Jobcenter Randers")
    if afdeling is None:
        st.subheader("Vælg en afdeling i venstre side")
    else:
        st.subheader(afdeling)
        if afdeling == "Job og ressourcer":
            show_job_og_ressourcer_graph()
            

        elif afdeling == "UUR":
            show_UUR_graph()

        elif afdeling == "Job og løntimer":
            show_job_og_lontimer_graph()

        elif afdeling == "Job og sundhedd":
            show_job_og_sundhed_graph()