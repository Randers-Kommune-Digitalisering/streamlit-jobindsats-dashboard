import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db
import os


db_client = get_jobindsats_db()


@st.cache_data
def load_baseline_from_excel(excel_path: str) -> pd.DataFrame:
    dfb = pd.read_excel(excel_path,)

    # normalize column names (so Metric/Baseline also works)
    dfb.columns = [c.strip().lower() for c in dfb.columns]

    # expected columns after lowercase: metric, baseline_value
    # but if your excel uses "baseline" instead of "baseline_value", map it
    if "baseline_value" not in dfb.columns and "baseline" in dfb.columns:
        dfb = dfb.rename(columns={"baseline": "baseline_value"})

    dfb["metric"] = dfb["metric"].astype(str).str.strip()
    dfb["baseline_value"] = pd.to_numeric(dfb["baseline_value"], errors="coerce")

    return dfb


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

        df_randers = df_randers.sort_values("Periode")

        st.subheader("Sygedagpenge Randers ")

        metric_options = [
            "Antal personer",
            "Antal fuldtidspersoner",
            "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
            "Fuldtidspersoner i pct. af befolkningen 16-66 år"
        ]

        selected_metric = st.selectbox("Vælg måling", metric_options)

        # ✅ Baseline UI
        show_excel_baseline = st.checkbox("Vis baseline fra Excel", value=True)
        show_auto_baseline = st.checkbox("Vis auto-baseline (gennemsnit)", value=False)
        show_percentile_baseline = st.checkbox("Vis percentile baseline", value=False)

        percentile_value = None
        baseline_percentile = None

        if show_percentile_baseline:
            percentile_value = st.slider("Vælg percentile", 1, 99, 50)

            baseline_percentile = float(
                df_randers[selected_metric].dropna().quantile(percentile_value / 100)
            )

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

        # 1) Excel baseline (default ON)
        if show_excel_baseline:
            excel_path = os.path.join(os.path.dirname(__file__), "..", "assets", "excelDocs", "baseline.xlsx")
            excel_path = os.path.normpath(excel_path)

            try:
                baseline_df = load_baseline_from_excel(excel_path)

                match = baseline_df[
                    baseline_df["metric"].str.strip().str.lower() == selected_metric.strip().lower()
                ]
                if match.empty or pd.isna(match["baseline_value"].iloc[0]):
                    st.warning(f"Ingen Excel-baseline fundet for: {selected_metric}")
                else:
                    excel_baseline_value = float(match["baseline_value"].iloc[0])
                    fig.add_hline(
                        y=excel_baseline_value,
                        line_dash="dash",
                        annotation_text=f"Baseline (Excel): {excel_baseline_value:.2f}",
                        annotation_position="top left"
                    )
            except Exception as e:
                st.warning(f"Kunne ikke læse Excel baseline: {e}")

        # 2) Mean baseline
        if show_auto_baseline:
            mean_value = float(df_randers[selected_metric].dropna().mean())
            fig.add_hline(
                y=mean_value,
                line_dash="dash",
                annotation_text=f"Gennemsnit: {mean_value:.2f}",
                annotation_position="top left"
            )

        # 3) Percentile baseline
        if baseline_percentile is not None:
            fig.add_hline(
                y=baseline_percentile,
                line_dash="dot",
                annotation_text=f"{percentile_value}%-percentile: {baseline_percentile:.2f}",
                annotation_position="bottom left"
            )

        st.plotly_chart(fig, use_container_width=True)
        if "qtij01_data" not in st.session_state:
            with st.spinner("Indlæser jobindsats_qtij01 data..."):
                query = (
                    'SELECT "Område", "Ydelsesgrupper", "Periode", "Målgruppe",'
                    ' "Antal personer i alt", "antal personer med ordinære timer", '
                    '"Andel personer med ordinære timer." '
                    "Gennemsnitlig timetal pr person med ordinære timer '"
                    "Gennemsnitlig antal ordinære timer  pr. måned"
                    'FROM jobindsats_qtij01'
                )
                columns = [
                    "Område",
                    "Ydelsesgrupper",
                    "Periode",
                    "Målgruppe",
                    "Antal personer i alt",
                    "antal personer med ordinære timer",
                    "Andel personer med ordinære timer.",
                    "gennemsnitlig atimetalpr perso med ordinære ",
                    "gennemsnitlig antal ordinære timer  pr. måned"
                ]
                
                result = db_client.execute_sql(query)

                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state.qtij01_data = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return
                
        df = st.session_state.qtij01_data
        
        numeric_cols = [
            "Antal personer i alt",
            "antal personer med ordinære timer",
            "Andel personer med ordinære timer.",
            "gennemsnitlig atimetalpr perso med ordinære ",
            "gennemsnitlig antal ordinære timer  pr. måned"
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            

# filter for Randers
        df_randers = df[df["Område"] == "Randers"].copy()

        if df_randers.empty:
            st.warning("Ingen data fundet for Randers.")
            return
        
        df_randers = df_randers.sort_values("Periode")

        st.subheader("Ordinære timer – Randers ")

        metric_options = [
            "Antal personer i alt",
            "antal personer med ordinære timer",
            "Andel personer med ordinære timer.",
            "gennemsnitlig atimetalpr perso med ordinære ",
            "gennemsnitlig antal ordinære timer  pr. måned"
        ]

        selected_metric = st.selectbox("Vælg måling", metric_options)

        show_auto_baseline = st.checkbox("Vis auto-baseline (gennemsnit)", value=True)
        show_percentile_baseline = st.checkbox("Vis percentile baseline", value=False)

        percentile_value = None
        baseline_percentile = None

        if show_percentile_baseline:
            percentile_value = st.slider("Vælg percentile", 1, 99, 50)

            baseline_percentile = float(
                df_randers[selected_metric].dropna().quantile(percentile_value / 100)
            )

        fig = px.line(
            df_randers,
            x="Periode",
            y=selected_metric,
            markers=True,
            title=f"{selected_metric} – Randers"
        )

    except Exception as e:
        st.exception(e)
        return
