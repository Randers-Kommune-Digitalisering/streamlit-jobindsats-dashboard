import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from streamlit_option_menu import option_menu
from utils.database_connection import get_jobindsats_db
import streamlit_antd_components as sac

db_client = get_jobindsats_db()


def get_jobcenter_randers_overview():
    with st.sidebar:
        st.markdown("## Jobcenter Randers")
        afdeling=sac.tree(items=[
                sac.TreeItem("Center for Job og Udvikling", children=[
                    sac.TreeItem("Job og løntimer"),
                    sac.TreeItem("Job og ressourcer"),
                    sac.TreeItem( "Job og sundhedd"),
                    sac.TreeItem( "UUR")
                ]),
                sac.TreeItem("Center for Job og Kompetencer")
            ], index=0, size='lg', icon=None, open_all=False, color='#4a4a4a', checkbox=False, show_line=False)
        
    st.title("Jobcenter Randers")
    if afdeling is None:
        st.subheader("Vælg en afdeling i venstre side")
    else:
        st.subheader(afdeling)



    
