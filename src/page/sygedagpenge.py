import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def get_sygedagpenge_overview():
    try:
        if 'sygedagpenge_data' not in st.session_state:
            with st.spinner('Indlæser sygedagpenge data...'):
                query = (
                    'SELECT "Periode Sygedagpenge", '
                    '"Gnsn. varighed af afsluttede forløb (uger)", "Område" '
                    'FROM jobindsats_y07a07'
                )
                result = db_client.execute_sql(query)
                columns = [
                    "Periode Sygedagpenge",
                    "Gnsn. varighed af afsluttede forløb (uger)",
                    "Område"
                ]
                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state.sygedagpenge_data = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return

        df = st.session_state.sygedagpenge_data

        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
        }

        df["Periode Sygedagpenge"] = pd.to_datetime(df["Periode Sygedagpenge"], errors='coerce')
        df["År"] = df["Periode Sygedagpenge"].dt.year.astype(str)
        df["Måned"] = df["Periode Sygedagpenge"].dt.month
        df["MånedNavn"] = df["Måned"].map(month_map)
        df["Område"] = df["Område"].astype(str)
        df["Værdi"] = pd.to_numeric(df["Gnsn. varighed af afsluttede forløb (uger)"], errors="coerce").round(1)

        available_years = sorted(df["År"].unique())
        selected_year = st.selectbox("Vælg år", available_years, index=len(available_years) - 1)

        chart_df = df[(df["År"] == selected_year)].dropna(subset=["MånedNavn", "Område", "Værdi"])
        chart_df = chart_df[["Måned", "MånedNavn", "Område", "Værdi"]]

        month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
        chart_df["MånedNavn"] = pd.Categorical(chart_df["MånedNavn"], categories=month_order, ordered=True)

        st.header(f"Varighed i afsluttede sygedagpengeforløb - {selected_year}", divider="gray")
        chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
            y=alt.Y('Værdi:Q', title='Gnsn. varighed af afsluttede forløb (uger)'),
            xOffset=alt.XOffset('Område:N', title='Område'),
            color=alt.Color('Område:N', title='Område'),
            tooltip=[
                alt.Tooltip('MånedNavn:N', title='Måned'),
                alt.Tooltip('Område:N', title='Område'),
                alt.Tooltip('Værdi:Q', title='Gnsn. varighed (uger)', format='.1f')
            ]
        ).properties(width=700, height=400)

        st.altair_chart(chart, use_container_width=True)

        export_df = chart_df.copy()
        export_df["Periode"] = export_df["MånedNavn"].astype(str) + " " + selected_year
        export_df = export_df[["Periode", "Område", "Værdi"]]
        export_df = export_df.rename(columns={"Værdi": "Gnsn. varighed af afsluttede forløb (uger)"})
        export_df["Gnsn. varighed af afsluttede forløb (uger)"] = export_df["Gnsn. varighed af afsluttede forløb (uger)"].map(lambda x: str(x).replace('.', ','))

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Sygedagpenge')
        output.seek(0)

        st.download_button(
            label="Eksporter data til Excel",
            data=output,
            file_name=f"sygedagpenge_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            icon=":material/add_chart:"
        )

    except Exception as e:
        st.error(f'Fejl ved hentning af sygedagpenge data: {e}')
    finally:
        db_client.close_connection()
