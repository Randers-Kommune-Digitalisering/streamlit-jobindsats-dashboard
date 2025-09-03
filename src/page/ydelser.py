import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from utils.database_connection import get_jobindsats_db
from utils.jobindsats_utils import ydelser_udfaldsmål_options, ydelser
import streamlit_antd_components as sac

db_client = get_jobindsats_db()


def get_ydelser_overview():
    ydelses_name = st.selectbox("Ydelsesnavn", list(ydelser.keys()), index=0)
    ydelse_info = ydelser[ydelses_name]
    periode_col = ydelse_info["periode_col"]
    table = ydelse_info["table"]

    content_tabs = sac.tabs([
        sac.TabsItem(ydelses_name, tag=ydelses_name, icon='bar-chart-line'),
    ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        session_key = f"{table}_data"
        if session_key not in st.session_state:
            with st.spinner(f'Indlæser {ydelses_name} data...'):
                query = (
                    f'SELECT "{periode_col}", "Område", '
                    '"Antal personer", "Antal fuldtidspersoner", '
                    '"Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", '
                    '"Fuldtidspersoner i pct. af befolkningen 16-66 år" '
                    f'FROM {table}'
                )
                columns = [
                    periode_col,
                    "Område",
                    "Antal personer",
                    "Antal fuldtidspersoner",
                    "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
                    "Fuldtidspersoner i pct. af befolkningen 16-66 år"
                ]
                result = db_client.execute_sql(query)
                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state[session_key] = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return

        df = st.session_state[session_key]

        df[periode_col] = pd.to_datetime(df[periode_col], errors='coerce')
        df["År"] = df[periode_col].dt.year.astype(str)
        df["Måned"] = df[periode_col].dt.month
        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
        }
        df["MånedNavn"] = df["Måned"].map(month_map)

        if content_tabs == ydelses_name:
            col1, col2 = st.columns([1, 2], gap="large")
            with col1:
                st.subheader("Filtrering")
                selected_udfaldsmål = st.selectbox("Udfaldsmål", ydelser_udfaldsmål_options, index=1)
                available_years = sorted(df["År"].unique())
                selected_year = st.selectbox("År", available_years, index=len(available_years) - 1)

            with col2:
                df_filtered = df[
                    (df["Område"] == "Randers") &
                    (df["År"] == selected_year)
                ].copy()

                df_filtered["Værdi"] = pd.to_numeric(df_filtered[selected_udfaldsmål], errors="coerce")
                chart_df = df_filtered.dropna(subset=["MånedNavn", "Værdi"])
                chart_df = chart_df[["Måned", "MånedNavn", "Værdi"]]

                month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
                chart_df["MånedNavn"] = pd.Categorical(chart_df["MånedNavn"], categories=month_order, ordered=True)

                st.header(f"{ydelses_name}: {selected_udfaldsmål} i Randers pr. måned - {selected_year}", divider="gray")
                chart = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                    y=alt.Y('Værdi:Q', title=selected_udfaldsmål),
                    color=alt.Color('Værdi:Q', scale=alt.Scale(scheme='blues'), legend=None),
                    tooltip=[
                        alt.Tooltip('MånedNavn:N', title='Måned'),
                        alt.Tooltip('Værdi:Q', title=selected_udfaldsmål, format='.2f')
                    ]
                ).properties(width=900, height=400)

                st.altair_chart(chart, use_container_width=True)

                export_df = chart_df.copy()
                export_df = export_df.rename(columns={"Værdi": selected_udfaldsmål})
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    export_df.to_excel(writer, index=False, sheet_name='Randers')
                output.seek(0)

                st.download_button(
                    label=f"Eksporter {ydelses_name} data til Excel",
                    data=output,
                    file_name=f"randers_{table}_{selected_year}_{selected_udfaldsmål}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    icon=":material/add_chart:"
                )

    except Exception as e:
        st.error(f'Fejl ved hentning af Ydelser: {e}')
    finally:
        db_client.close_connection()
