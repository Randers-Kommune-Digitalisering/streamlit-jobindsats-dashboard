import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from utils.database_connection import get_jobindsats_db
from utils.inputs_db_connection import get_inputs_db
from utils.jobindsats_utils import ydelser_udfaldsmål_options, ydelser
import streamlit_antd_components as sac



db_client = get_jobindsats_db()
input_db_client = get_inputs_db()


def fetch_input_series_options():
    rows = input_db_client.execute_sql("""
        SELECT id, name
        FROM app_series
        ORDER BY name;
    """)
    return rows or []


def fetch_input_years_for_series(series_id: int):
    rows = input_db_client.execute_sql("""
        SELECT DISTINCT year
        FROM app_budget_entries
        WHERE series_id = %s
        ORDER BY year;
    """, (series_id,))
    return [int(r[0]) for r in rows] if rows else []


def fetch_input_budget_for_series_year(series_id: int, year: int):
    rows = input_db_client.execute_sql("""
        SELECT month, value
        FROM (
            SELECT DISTINCT ON (month)
                month, value, entered_at
            FROM app_budget_entries
            WHERE series_id = %s AND year = %s
            ORDER BY month, entered_at DESC
        ) x
        ORDER BY month;
    """, (series_id, year))
    return rows or []


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
        df["År"] = df[periode_col].dt.year
        df["Måned"] = df[periode_col].dt.month

        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
        }
        month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]

        df["MånedNavn"] = df["Måned"].map(month_map)

        if content_tabs == ydelses_name:
            col1, col2 = st.columns([1, 2], gap="large")

            with col1:
                st.subheader("Filtrering")

                selected_udfaldsmål = st.selectbox(
                    "Udfaldsmål",
                    ydelser_udfaldsmål_options,
                    index=1
                )

                available_years = sorted(df["År"].dropna().unique())
                selected_year = st.selectbox(
                    "År",
                    available_years,
                    index=len(available_years) - 1
                )

                include_last_two_years = st.checkbox(
                    "Inkluder seneste to år",
                    value=False,
                    key="include_last_two_years"
                )

                overlay_input_series = st.checkbox(
                    "Overlap input-serie",
                    value=False,
                    key="overlay_input_series"
                )

                selected_input_series_id = None
                selected_input_series_name = None
                selected_input_year = None

                if overlay_input_series:
                    input_series_rows = fetch_input_series_options()

                    if input_series_rows:
                        input_series_names = [row[1] for row in input_series_rows]
                        input_series_lookup = {row[1]: row[0] for row in input_series_rows}

                        selected_input_series_name = st.selectbox(
                            "Vælg input-serie",
                            input_series_names,
                            key="selected_input_series_name"
                        )
                        selected_input_series_id = input_series_lookup[selected_input_series_name]

                        input_years = fetch_input_years_for_series(selected_input_series_id)

                        if input_years:
                            default_index = len(input_years) - 1
                            if selected_year in input_years:
                                default_index = input_years.index(selected_year)

                            selected_input_year = st.selectbox(
                                "Vælg input-år",
                                input_years,
                                index=default_index,
                                key="selected_input_year"
                            )
                        else:
                            st.warning("Ingen år fundet for den valgte input-serie.")
                    else:
                        st.warning("Ingen input-serier fundet.")

            with col2:
                df_filtered = df[
                    (df["Område"] == "Randers") &
                    (
                        df["År"].isin([selected_year, selected_year - 1, selected_year - 2])
                        if include_last_two_years
                        else (df["År"] == selected_year)
                    )
                ].copy()

                df_filtered["Værdi"] = pd.to_numeric(df_filtered[selected_udfaldsmål], errors="coerce")

                chart_df = df_filtered.dropna(subset=["MånedNavn", "Værdi", "År"]).copy()
                chart_df = chart_df[["Måned", "MånedNavn", "Værdi", "År"]]
                chart_df["År"] = chart_df["År"].astype(str)
                chart_df["MånedNavn"] = pd.Categorical(
                    chart_df["MånedNavn"],
                    categories=month_order,
                    ordered=True
                )

                overlay_chart_df = pd.DataFrame()
                overlay_target_value = None

                if overlay_input_series and selected_input_series_id is not None and selected_input_year is not None:
                    input_rows = fetch_input_budget_for_series_year(
                        selected_input_series_id,
                        int(selected_input_year)
                    )

                    target_rows = input_db_client.execute_sql("""
                        SELECT target_value
                        FROM app_targets
                        WHERE series_id = %s
                        AND EXTRACT(YEAR FROM entered_at)::INT = %s
                        ORDER BY entered_at DESC
                        LIMIT 1;
                    """, (selected_input_series_id, int(selected_input_year)))

                    if target_rows:
                        overlay_target_value = float(target_rows[0][0])

                    if input_rows:
                        overlay_chart_df = pd.DataFrame(input_rows, columns=["Måned", "Værdi"])
                        overlay_chart_df["År"] = str(selected_input_year)
                        overlay_chart_df["MånedNavn"] = overlay_chart_df["Måned"].map(month_map)
                        overlay_chart_df["Serie"] = f"Input-serie: {selected_input_series_name}"
                        overlay_chart_df["Værdi"] = pd.to_numeric(overlay_chart_df["Værdi"], errors="coerce")
                        overlay_chart_df["MånedNavn"] = pd.Categorical(
                            overlay_chart_df["MånedNavn"],
                            categories=month_order,
                            ordered=True
                        )

                st.header(
                    f"{ydelses_name}: {selected_udfaldsmål} i Randers pr. måned - {selected_year}",
                    divider="gray"
                )

                base_chart = alt.Chart(chart_df).mark_line(point=True).encode(
                    x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                    y=alt.Y('Værdi:Q', title=selected_udfaldsmål),
                    color=alt.Color('År:N', title='År'),
                    tooltip=[
                        alt.Tooltip('År:N', title='År'),
                        alt.Tooltip('MånedNavn:N', title='Måned'),
                        alt.Tooltip('Værdi:Q', title=selected_udfaldsmål, format='.2f')
                    ]
                )

                layers = [base_chart]

                if not overlay_chart_df.empty:
                    overlay_line = alt.Chart(overlay_chart_df).mark_line(
                        point=True,
                        strokeDash=[6, 4],
                        color="#d62728"
                    ).encode(
                        x=alt.X('MånedNavn:N', title='Måned', sort=month_order),
                        y=alt.Y('Værdi:Q', title=selected_udfaldsmål),
                        detail='Serie:N',
                        tooltip=[
                            alt.Tooltip('Serie:N', title='Serie'),
                            alt.Tooltip('År:N', title='År'),
                            alt.Tooltip('MånedNavn:N', title='Måned'),
                            alt.Tooltip('Værdi:Q', title='Input værdi', format='.2f')
                        ]
                    )

                    layers.append(overlay_line)

                if overlay_target_value is not None:
                    target_df = pd.DataFrame({
                        "y": [overlay_target_value],
                        "Label": [f"Mål: {selected_input_series_name} ({selected_input_year})"]
                    })

                    target_rule = alt.Chart(target_df).mark_rule(
                        strokeDash=[2, 2],
                        color="#ff7f0e"
                    ).encode(
                        y='y:Q',
                        tooltip=[
                            alt.Tooltip('Label:N', title='Mål'),
                            alt.Tooltip('y:Q', title='Værdi', format='.2f')
                        ]
                    )

                    layers.append(target_rule)

                chart = alt.layer(*layers).properties(width=900, height=400)

                st.altair_chart(chart, use_container_width=True)

                if not overlay_chart_df.empty:
                    st.caption(f"Rød stiplet linje = Input-serie: {selected_input_series_name}")

                if overlay_target_value is not None:
                    st.caption(f"Orange stiplet linje = Mål for input-serie: {selected_input_series_name} ({selected_input_year})")
              
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
