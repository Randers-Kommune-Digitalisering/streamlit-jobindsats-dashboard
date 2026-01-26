import streamlit as st
import requests
import pandas as pd
import altair as alt
from io import BytesIO
import plotly.express as px
from streamlit_option_menu import option_menu
from utils.database_connection import get_jobindsats_db
import streamlit_antd_components as sac


db_client = get_jobindsats_db()

def show_UUR_graph():
    st.write("This is UUR!")