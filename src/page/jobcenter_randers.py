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



        elif afdeling == "UUR":
            st.write("This is UUR!")



        elif afdeling == "Job og løntimer":
            st.write("This is job og løntimer!")

        elif afdeling == "Job og sundhedd":
            try:
                if "y14d03_data" not in st.session_state:
                    with st.spinner("Indlæser jobindsats_y14d03 data..."):

                        query = (
                            'SELECT "Område", "Periode", "Ydelsesgrupper", "Målgruppe", '
                            '"Efterfølgende beskæftigelse: I anden virksomhed i anden branche", '
                            '"Efterfølgende beskæftigelse: I anden virksomhed i samme branche", '
                            '"Efterfølgende beskæftigelse: I samme virksomhed", '
                            '"Efterfølgende beskæftigelse: Ingen beskæftigelse" '
                            'FROM jobindsats_y14d03'
                        )

                        columns = [
                            "Område",
                            "Periode",
                            "Ydelsesgrupper",
                            "Målgruppe",
                            "Efterfølgende beskæftigelse: I anden virksomhed i anden branche",
                            "Efterfølgende beskæftigelse: I anden virksomhed i samme branche",
                            "Efterfølgende beskæftigelse: I samme virksomhed",
                            "Efterfølgende beskæftigelse: Ingen beskæftigelse",
                        ]

                        result = db_client.execute_sql(query)

                        if result is not None:
                            df = pd.DataFrame(result, columns=columns)
                            st.session_state.y14d03_data = df
                        else:
                            st.error("Kunne ikke hente jobindsats_y14d03 data fra databasen.")
                            return

                df = st.session_state.y14d03_data

                numeric_cols = [
                    "Efterfølgende beskæftigelse: I anden virksomhed i anden branche",
                    "Efterfølgende beskæftigelse: I anden virksomhed i samme branche",
                    "Efterfølgende beskæftigelse: I samme virksomhed",
                    "Efterfølgende beskæftigelse: Ingen beskæftigelse",
                ]

                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

                df_randers = df[df["Område"] == "Randers"].copy()

                if df_randers.empty:
                    st.warning("Ingen data fundet for Randers i jobindsats_y14d03.")
                    return

                st.subheader("Efterfølgende beskæftigelse (3 mdr.) – Randers")

                ydelsesgrupper = sorted(df_randers["Ydelsesgrupper"].dropna().unique())
                selected_ydelsesgruppe = st.selectbox("Vælg Ydelsesgruppe", ydelsesgrupper)

                outcome_options = [
                    "Efterfølgende beskæftigelse: I anden virksomhed i anden branche",
                    "Efterfølgende beskæftigelse: I anden virksomhed i samme branche",
                    "Efterfølgende beskæftigelse: I samme virksomhed",
                    "Efterfølgende beskæftigelse: Ingen beskæftigelse",
                ]

                selected_outcome = st.selectbox("Vælg outcome", outcome_options)

                include_last_2_years = st.checkbox("Inkluder seneste 2 år", value=False)

                df_plot_base = df_randers[df_randers["Ydelsesgrupper"] == selected_ydelsesgruppe].copy()

                # Extract year from Periode like "2024QMAT03"
                df_plot_base["År"] = df_plot_base["Periode"].astype(str).str[:4]
                available_years = sorted(df_plot_base["År"].dropna().unique())

                # latest year cuss we go index list -1
                selected_year = available_years[-1]   

                years_to_show = [selected_year]
                if include_last_2_years:
                    try:
                        y = int(selected_year)
                        years_to_show = [str(y - 2), str(y - 1), str(y)]
                    except:
                        years_to_show = [selected_year]

                df_plot = df_plot_base[df_plot_base["År"].isin(years_to_show)].copy()

                # Aggregate so we get 1 value per period (removes the weird vertical jumps)
                df_plot = (
                    df_plot.groupby(["År", "Periode"], as_index=False)[selected_outcome]
                    .mean()
                )

                fig = px.line(
                    df_plot,
                    x="Periode",
                    y=selected_outcome,
                    color="År",
                    markers=True,
                    title=f"{selected_outcome} – {selected_ydelsesgruppe} (Randers)"
                )

                fig.update_layout(
                    xaxis_title="Periode",
                    yaxis_title=selected_outcome
                )

                config = {
                    "displaylogo": False,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": "jobindsats_graf",
                        "height": 600,
                        "width": 1200,
                        "scale": 2
                    }
                }

                st.plotly_chart(fig, use_container_width=True, config=config)

                
                df_plot = df_randers[df_randers["Ydelsesgrupper"] == selected_ydelsesgruppe].copy()

                df_plot = (
                    df_plot
                    .groupby("Periode", as_index=False)[selected_outcome]
                    .mean()
                )


                fig = px.line(
                    df_plot,
                    x="Periode",
                    y=selected_outcome,
                    markers=True,
                    title=f"{selected_outcome} – {selected_ydelsesgruppe} (Randers)"
                )

                fig.update_layout(
                    xaxis_title="Periode",
                    yaxis_title=selected_outcome
                )

                st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Fejl: {e}")
                return





    
