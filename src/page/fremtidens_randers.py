import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from io import BytesIO
from utils.database_connection import get_jobindsats_db
from utils.jobindsats_utils import ydelsesgrupper_udfaldsmål_options, ydelsesgrupper_målgruppe_options
import streamlit_antd_components as sac

db_client = get_jobindsats_db()




#depends on this function to start the page everything inside is the content
def get_ydelsesgrupper_overview():
    
    content_tabs = sac.tabs([
        sac.TabsItem('Ydelsesgrupper i alt', tag='Ydelsesgrupper i alt', icon='bar-chart'),
        sac.TabsItem('Udvikling', tag='Udvikling', icon='line-chart'),
        sac.TabsItem('Placering', tag='Placering', icon='flag'),
    ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'ydelsesgrupper_data' not in st.session_state:
            with st.spinner('Indlæser ydelsesgrupper data...'):
                query = (
                    'SELECT "Periode Ydelsesgrupper", "Område", '
                    '"Ydelsesgrupper", "Placering på benchmarkranglisten", "Faktisk antal", "Forventet antal", "Forskel mellem forventet og faktisk antal", '
                    '"Forventet andel (pct.)", "Faktisk andel (pct.)" '
                    'FROM jobindsats_y30r21'
                )
                columns = [
                    "Periode Ydelsesgrupper",
                    "Område",
                    "Ydelsesgrupper",
                    "Placering på benchmarkranglisten",
                    "Faktisk antal",
                    "Forventet antal",
                    "Forskel mellem forventet og faktisk antal",
                    "Forventet andel (pct.)",
                    "Faktisk andel (pct.)"
                ]
                result = db_client.execute_sql(query)
                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session_state.ydelsesgrupper_data = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return


        df = st.session_state.ydelsesgrupper_data

        df["Periode Ydelsesgrupper"] = pd.to_datetime(df["Periode Ydelsesgrupper"], errors='coerce')
        df["År"] = df["Periode Ydelsesgrupper"].dt.year.astype(str)
        df["Måned"] = df["Periode Ydelsesgrupper"].dt.month
        month_map = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Maj", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
        }
        df["MånedNavn"] = df["Måned"].map(month_map)

        if content_tabs == 'Ydelsesgrupper i alt':
            col1, col2 = st.columns([1, 2], gap="large")
            with col1:
                st.subheader("Filtrering")

                selected_udfaldsmål = st.selectbox("Udfaldsmål", ydelsesgrupper_udfaldsmål_options, index=1)
                available_years = sorted(df["År"].unique())
                selected_year = st.selectbox("År", available_years, index=len(available_years) - 1)
                available_målgrupper = sorted(df["Ydelsesgrupper"].unique())
                målgruppe_filtered = [m for m in ydelsesgrupper_målgruppe_options if m in available_målgrupper]
                selected_målgruppe = st.selectbox("Målgruppe", målgruppe_filtered, index=målgruppe_filtered.index("Ydelsesgrupper i alt") if "Ydelsesgrupper i alt" in målgruppe_filtered else 0)



            with col2:
                df_filtered = df[
                    (df["Ydelsesgrupper"] == selected_målgruppe) &
                    (df["Område"] == "Randers") &
                    (df["År"] == selected_year)
                ].copy()


 
                df_filtered["Værdi"] = pd.to_numeric(df_filtered[selected_udfaldsmål], errors="coerce")
                chart_df = df_filtered.dropna(subset=["MånedNavn", "Værdi"])
                chart_df = chart_df[["Måned", "MånedNavn", "Værdi"]]


                #initialize a month order list
                month_order = ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]

                # ensure that all montts even even those without data is represented
                months_full = pd.DataFrame({
                    "MånedNavn": month_order,
                    "Måned": list(range(1, 13))
                })

                # combines (merge) the chart list with the months list (months_full) is always the 12 months (these 2 lines are what always shows all months)
                chart_df = months_full.merge(chart_df, on=["Måned", "MånedNavn"], how="left")

                # this detects if udfaldsmål is a percentage column so it can adjust the formating (can be used in many scenarioes)
                is_pct = "pct" in selected_udfaldsmål.lower()
                value_format = ".1f" if is_pct else ",.0f"


                # a small reusable hover function to highlight the hovered over bar
                hover = alt.selection_point(
                    fields=["MånedNavn"],
                    on="mouseover",
                    empty=False
                )
                


                #the headrer just above the chart
                st.header(
                    f"{selected_udfaldsmål} for {selected_målgruppe} i Randers pr. måned - {selected_year}",
                    divider="blue"
                )




                #sets attributes for the x and y axis
                base = alt.Chart(chart_df).encode(
                    x=alt.X(
                        "MånedNavn:N",
                        title="Måned",
                        sort=month_order,

                    ),
                    y=alt.Y(
                        "Værdi:Q",
                        title=selected_udfaldsmål,
                        scale=alt.Scale(zero=True),
                        axis=alt.Axis(format=value_format, grid=True, tickCount=6, titlePadding=12)
                    ),
                )




                bars = base.mark_bar(
                    cornerRadiusTopLeft=5,
                    cornerRadiusTopRight=5
                ).encode(
                    color=alt.condition(
                        hover,
                        alt.value("#1f77b4"),   # hover highlight
                        alt.value("#A9C7E8")    # default calm color
                    )
                ).add_params(hover)


                #all the configurations for the chart such as color and size
                chart = (bars).properties(
                    height=500
                ).configure_axis(
                    gridColor="#B32626"
                ).configure_view(
                    fill="#160000"
                )

                #ensures that the chat fills the entire container width to make it dynamic
                st.altair_chart(chart, use_container_width=True)





     #           export_df = chart_df.copy()
     #           export_df = export_df.rename(columns={"Værdi": selected_udfaldsmål})
     #           output = BytesIO()
     #           with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
     #               export_df.to_excel(writer, index=False, sheet_name='Randers')
     #           output.seek(0)




     #           st.download_button(
     #               label="Eksporter Ydelsesgruppe data til Excel",
     #               data=output,
     #               file_name=f"randers_ydelsesgrupper_{selected_year}_{selected_målgruppe}_{selected_udfaldsmål}.xlsx",
     #               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     #               type="primary",
     #               icon=":material/add_chart:"
     #           )


        elif content_tabs == 'Udvikling':
            col1, col2 = st.columns([1, 2], gap="large")
            with col1:
                st.subheader("Filtrering")
                available_målgrupper = sorted(df["Ydelsesgrupper"].unique())
                målgruppe_filtered = [m for m in ydelsesgrupper_målgruppe_options if m in available_målgrupper]
                selected_målgruppe = st.selectbox("Målgruppe", målgruppe_filtered, index=0)
                andel_options = ["Placering på benchmarkranglisten", "Forventet andel (pct.)", "Faktisk andel (pct.)"]
                selected_andel = st.selectbox("Vælg andel/placering", andel_options, index=0)


            with col2:
                df_udvikling = df[
                    (df["Ydelsesgrupper"] == selected_målgruppe) &
                    (df["Område"] == "Randers")
                ].copy()

                df_udvikling["ÅrMåned"] = df_udvikling["Periode Ydelsesgrupper"].dt.strftime("%Y-%m")

                df_udvikling["Værdi"] = pd.to_numeric(df_udvikling[selected_andel], errors="coerce")
                chart_df = df_udvikling.dropna(subset=["ÅrMåned", "Værdi"])
                chart_df = chart_df[["ÅrMåned", "Værdi"]]

    

                st.header(f"{selected_andel} for {selected_målgruppe} i Randers over tid", divider="gray")

                chart = alt.Chart(chart_df).mark_line(point=alt.OverlayMarkDef(filled=False, fill="white")).encode(
                    x=alt.X('ÅrMåned:N', title='Periode', sort=list(chart_df["ÅrMåned"].unique())),
                    y=alt.Y('Værdi:Q', title=selected_andel),
                    tooltip=[
                        alt.Tooltip('ÅrMåned:N', title='Periode'),
                        alt.Tooltip('Værdi:Q', title=selected_andel, format='.2f')
                    ]
                ).properties(width=900, height=500)

                st.altair_chart(chart, use_container_width=True)



#                export_df = chart_df.rename(columns={"Værdi": selected_andel})
#                output = BytesIO()
#                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                    export_df.to_excel(writer, index=False, sheet_name='Udvikling')
#                output.seek(0)

#                st.download_button(
#                    label="Eksporter udviklingsdata til Excel",
#                    data=output,
#                    file_name=f"randers_udvikling_{selected_målgruppe}_{selected_andel}.xlsx",
#                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                    type="primary",
#                    icon=":material/add_chart:"
#                )




        elif content_tabs == 'Placering':
            col1, col2 = st.columns([1, 2], gap="large")
            with col1:
                st.subheader("Filtrering")



                selected_udfaldsmål = st.selectbox("Udfaldsmål", ydelsesgrupper_udfaldsmål_options, index=1)
                available_years = sorted(df["År"].unique())
                selected_year = st.selectbox("År", available_years, index=len(available_years) - 1)
                available_målgrupper = sorted(df["Ydelsesgrupper"].unique())
                målgruppe_filtered = [m for m in ydelsesgrupper_målgruppe_options if m in available_målgrupper]
                selected_målgruppe = st.selectbox("Målgruppe", målgruppe_filtered, index=0)


            with col2:
                df_placering = df[
                    (df["År"] == selected_year) &
                    (df["Ydelsesgrupper"] == selected_målgruppe)
                ].copy()


                df_placering["Værdi"] = pd.to_numeric(df_placering[selected_udfaldsmål], errors="coerce")
                df_placering = df_placering.dropna(subset=["Område", "Værdi", "Periode Ydelsesgrupper"])

                df_placering = df_placering.sort_values("Periode Ydelsesgrupper").groupby("Område").tail(1)

                st.header(f"{selected_udfaldsmål} blandt alle kommuner ({selected_målgruppe}, {selected_year})", divider="gray")
                chart = alt.Chart(df_placering).mark_bar().encode(
                    x=alt.X('Område:N', title='Kommune', sort=alt.EncodingSortField(field="Værdi", order="descending")),
                    y=alt.Y('Værdi:Q', title=selected_udfaldsmål),
                    color=alt.condition(
                        alt.datum.Område == "Randers",
                        alt.value("orange"),
                        alt.value("steelblue")
                    ),
                    tooltip=[
                        alt.Tooltip('Område:N', title='Kommune'),
                        alt.Tooltip('Værdi:Q', title=selected_udfaldsmål, format='.2f')
                    ]
                ).properties(width=900, height=500)

                st.altair_chart(chart, use_container_width=True)



#                export_df = df_placering[["Område", "Værdi"]].copy()
#                export_df = export_df.rename(columns={"Værdi": selected_udfaldsmål})
#                output = BytesIO()
#                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                    export_df.to_excel(writer, index=False, sheet_name='Placering')
#                output.seek(0)

#                st.download_button(
#                    label="Eksporter Placering data til Excel",
#                    data=output,
#                    file_name=f"{selected_udfaldsmål.lower().replace(' ', '_')}_kommuner_{selected_year}_{selected_målgruppe}.xlsx",
#                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                    type="primary",
#                    icon=":material/add_chart:"
#                )

    except Exception as e:
        st.error(f'Fejl ved hentning af ydelsesgrupper: {e}')
    finally:
        db_client.close_connection()
