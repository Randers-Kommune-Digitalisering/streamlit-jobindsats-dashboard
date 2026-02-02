import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def show_job_og_lontimer_graph():
    try:
        if "ptva02_data" not in st.session_state:
            with st.spinner("Loading jobindsats_ptva02 data..."):
                query = (
                    'SELECT "Område", "Periode", "Ydelsesgrupper", '
                    '"Antal personer", "Antal fuldtidspersoner", '
                    '"Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", '
                    '"Fuldtidspersoner i pct. af befolkningen 16-66 år", '
                    '"Periode Offentligt forsørgede" '
                    'FROM jobindsats_ptva02'
                )

                columns = [
                    "Område",
                    "Periode",
                    "Ydelsesgrupper",
                    "Antal personer",
                    "Antal fuldtidspersoner",
                    "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
                    "Fuldtidspersoner i pct. af befolkningen 16-66 år",
                    "Periode Offentligt forsørgede",
                ]

                result = db_client.execute_sql(query)
                if result is None:
                    st.error("Could not fetch data from the database.")
                    return

                st.session_state.ptva02_data = pd.DataFrame(result, columns=columns)

        df = st.session_state.ptva02_data.copy()

        numeric_cols = [
            "Antal personer",
            "Antal fuldtidspersoner",
            "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
            "Fuldtidspersoner i pct. af befolkningen 16-66 år",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df[df["Område"] == "Randers"].copy()
        if df.empty:
            st.warning("No data found for Randers.")
            return

        df = df.sort_values("Periode")

        st.subheader("Overall reduction in citizens on public support – Randers")

        ydelses_options = sorted(df["Ydelsesgrupper"].dropna().unique().tolist())
        ydelses_options = ["All (total)"] + ydelses_options
        selected_ydelse = st.selectbox("Select benefit group (Ydelsesgrupper)", ydelses_options)

        baseline_value = st.number_input(
            "Baseline (full-time persons)",
            min_value=0,
            value=4086,
            step=1
        )

        show_difference = st.checkbox("Show difference vs baseline", value=True)

        if selected_ydelse != "All (total)":
            df_plot = df[df["Ydelsesgrupper"] == selected_ydelse].copy()
        else:
            df_plot = df.copy()

        df_plot = (
            df_plot.groupby("Periode", as_index=False)["Antal fuldtidspersoner"]
            .sum()
        )

        df_plot["Difference vs baseline"] = df_plot["Antal fuldtidspersoner"] - float(baseline_value)

        # -----------------------------
        # 6) Main line chart
        # -----------------------------
        title = f"Full-time persons – {selected_ydelse} (Randers)"
        fig = px.line(
            df_plot,
            x="Periode",
            y="Antal fuldtidspersoner",
            markers=True,
            title=title
        )

        fig.add_hline(
            y=float(baseline_value),
            line_dash="dash",
            annotation_text=f"Baseline: {baseline_value}",
            annotation_position="top left"
        )

        fig.update_layout(
            xaxis_title="Period",
            yaxis_title="Full-time persons"
        )

        st.plotly_chart(fig, use_container_width=True, key="ptva02_main")

        if show_difference:
            fig2 = px.line(
                df_plot,
                x="Periode",
                y="Difference vs baseline",
                markers=True,
                title="Difference vs baseline (negative = reduction)"
            )
            fig2.add_hline(y=0, line_dash="dot")
            fig2.update_layout(
                xaxis_title="Period",
                yaxis_title="Difference"
            )
            st.plotly_chart(fig2, use_container_width=True, key="ptva02_diff")

    except Exception as e:
        st.exception(e)
        return
