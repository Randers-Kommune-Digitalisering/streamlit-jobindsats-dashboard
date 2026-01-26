import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db



db_client = get_jobindsats_db()

def show_UUR_graph():
    st.write("This is UUR!")