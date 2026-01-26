import streamlit as st
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def show_job_og_lontimer_graph():
    st.write("This is job og løntimer!")
    try:
#   Your code for fetching data and displaying the graph goes here
        pass

    except Exception as e:
        st.error(f"Der opstod en fejl: {e}")
