import streamlit as st
from utils.database_connection import get_jobindsats_db


db_client = get_jobindsats_db()

def show_UUR_graph():
    st.write("This is UUR!")
