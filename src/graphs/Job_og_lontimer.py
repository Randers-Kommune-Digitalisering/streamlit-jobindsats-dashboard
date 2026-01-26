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
def show_job_og_lontimer_graph():
    st.write("This is job og løntimer!")
    try:
        if "y07a01_data" not in st.session_state:
            with st.spinner("Indlæser jobindsats_y07a01 data..."):

                query = (
                            'SELECT "Område", "Periode", '
                            '"Antal løntimer", "Antal fuldtidspersoner", '
                            '"Løntimer i pct. af arbejdsstyrken 16-66 år", '
                            '"Løntimer i pct. af befolkningen 16-66 år" '
                            'FROM jobindsats_y07a01'
                        )

                columns = [
                            "Område",
                            "Periode",
                            "Antal løntimer",
                            "Antal fuldtidspersoner",
                            "Løntimer i pct. af arbejdsstyrken 16-66 år",
                            "Løntimer i pct. af befolkningen 16-66 år"
                        ]

                result = db_client.execute_sql(query)

                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state.y07a01_data = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return

        df = st.session_state.y07a01_data

        # Convert numeric columns
        numeric_cols = [
            "Antal løntimer",
            "Antal fuldtidspersoner",
            "Løntimer i pct. af arbejdsstyrken 16-66 år",
            "Løntimer i pct. af befolkningen 16-66 år"
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filter for Randers
        df_randers = df[df["Område"] == "Randers"].copy()

        if df_randers.empty:
            st.warning("Ingen data tilgængelig for Randers i jobindsats_y07a01.")
            return

        # Create Altair line chart
        chart = alt.Chart(df_randers).mark_line(point=True).encode(
            x='Periode:N',
            y=alt.Y('Antal løntimer:Q', title='Antal løntimer'),
            tooltip=['Periode', 'Antal løntimer']
        ).properties(
            title='Udvikling i Antal løntimer for Randers',
            width=700,
            height=400
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Der opstod en fejl: {e}")
        