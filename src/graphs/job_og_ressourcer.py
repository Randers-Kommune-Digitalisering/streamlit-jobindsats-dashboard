import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db


db_client = get_jobindsats_db()


def show_job_og_ressourcer_graph():
    try:
        if "y07a02_data" not in st.session_state:
            with st.spinner("Indlæser jobindsats_y07a02 data..."):

                query = (
                'SELECT "Område", "Periode", '
                '"Antal personer", "Antal fuldtidspersoner", '
                '"Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", '
                '"Fuldtidspersoner i pct. af befolkningen 16-66 år" '
                'FROM jobindsats_y07a02'
                )

                columns = [
                "Område",
                "Periode",
                "Antal personer",
                "Antal fuldtidspersoner",
                "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
                "Fuldtidspersoner i pct. af befolkningen 16-66 år"
                ]

                result = db_client.execute_sql(query)

                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state.y07a02_data = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return

        df = st.session_state.y07a02_data

# Convert numeric columns
        numeric_cols = [
            "Antal personer",
            "Antal fuldtidspersoner",
            "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
            "Fuldtidspersoner i pct. af befolkningen 16-66 år"
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

# Filter for Randers
        df_randers = df[df["Område"] == "Randers"].copy()

        if df_randers.empty:
            st.warning("Ingen data fundet for Randers.")
            return

# Sort by period
        df_randers = df_randers.sort_values("Periode")

        st.subheader("Sygedagpenge Randers ")

        metric_options = [
            "Antal personer",
            "Antal fuldtidspersoner",
            "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
            "Fuldtidspersoner i pct. af befolkningen 16-66 år"
        ]

        selected_metric = st.selectbox("Vælg måling", metric_options)

        fig = px.line(
            df_randers,
            x="Periode",
            y=selected_metric,
            markers=True,
            title=f"{selected_metric} – Randers"
        )

        fig.update_layout(
            xaxis_title="Periode",
            yaxis_title=selected_metric
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Fejl: {e}")
        return
