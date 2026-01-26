import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def show_job_og_sundhed_graph():
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


        
        #second graph

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
