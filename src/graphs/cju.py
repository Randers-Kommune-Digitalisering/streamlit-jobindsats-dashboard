import streamlit as st
import pandas as pd
from utils.database_connection import get_jobindsats_db
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from utils.func import LastUpdate, NextUpdate

db_client = get_jobindsats_db()

def percent_comma(x, pos):
    return f"{x:,.1f}%".replace('.', ',')

def date_parser(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column].str.replace('M', '-'), format='%Y-%m')
    return df

def cju_page(afdeling):
    if afdeling == "CJU - fælles mål":
        try:
            st.header("Overordnede mål")
            today = pd.to_datetime("today")



            with st.container(border=1):
                st.subheader("1.a - Sygedagpenge: Arbejdsmarkedsstatus 3 måneder efter afsluttet forløb")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                with col1:
                    st.markdown("""
                        #### Mål
                        ...

                        #### Noter
                        Grafen viser gennemsnit seneste 4 kvartaler

                        #### Kilde
                        Jobindsats.dk

                            y07b15
                    """)
                with col2:

                    query = (
                        'SELECT "Område", "Periode", "Arbejdsmarkedsstatus", "Status 3 mdr. efter afsluttet forløb, pct." FROM jobindsats_y07b15 where "Område" IN (\'Randers\') order by "Periode" asc;'
                    ) 

                    result = db_client.execute_sql(query)

                    if not result:
                        st.warning("Data ikke tilgængelige")
                    else:
                        df = pd.DataFrame(result, columns=["Område", "Periode", "Arbejdsmarkedsstatus", "Status 3 mdr. efter afsluttet forløb, pct."])
                        df["Status 3 mdr. efter afsluttet forløb, pct."] = pd.to_numeric(df["Status 3 mdr. efter afsluttet forløb, pct."], errors='coerce')
                        df["Periode"] = df["Periode"].str.replace('QMAT0', '-K')
                        df["År"] = df["Periode"].str[:4].astype(int)
                        df = df[df["År"] >= today.year - 4]
                        fig, ax = plt.subplots(figsize=(8, 4))
                        colors = {'Lønmodtagerbeskæftigelse': '#00B050', 'Uddannelse': '#FFC000', 'Fleksjob': '#FF0000', 'Selvforsørgelse': '#00B0F0'}
                        for Arbejdsmarkedsstatus, group in df.groupby("Arbejdsmarkedsstatus"):
                            ax.plot(group['Periode'], group['Status 3 mdr. efter afsluttet forløb, pct.'], label=Arbejdsmarkedsstatus, color=colors.get(Arbejdsmarkedsstatus, 'black'))
                        ax.set_xlabel('Tid')
                        ax.set_ylabel('Procent')
                        ax.set_title('Sygedagpangemodtagere: Status 3 mdr. efter afsluttet forløb, pct.')
                        ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                        ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        handles, labels = ax.get_legend_handles_labels()
                        sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: 0 if x[1] == "Randers" else 1)
                        handles, labels = zip(*sorted_handles_labels)
                        ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                        fig.autofmt_xdate()
                        st.pyplot(fig, use_container_width=False)


            with st.container(border=1):
                st.subheader("1.b - Aktivitetsparate kontanthjælpsmodtagere: Arbejdsmarkedsstatus 3 måneder efter afsluttet forløb")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                with col1:
                    st.markdown(f"""
                        #### Mål
                        ...

                        #### Noter
                        Grafen viser gennemsnit seneste 4 kvartaler

                        #### Kilde
                        Jobindsats.dk

                            y60b15
                                - Sidst opdateret:  {LastUpdate('y60b15')}
                                - Næste opdatering: {NextUpdate('y60b15')}
                    """)
                with col2:

                    query = (
                        'SELECT "Område", "Periode", "Arbejdsmarkedsstatus", "Status 3 mdr. efter afsluttet forløb, pct." FROM jobindsats_y60b15 where "Område" IN (\'Randers\') order by "Periode" asc;'
                    ) 

                    result = db_client.execute_sql(query)

                    if not result: 
                        st.warning("Data ikke tilgængelige")
                    else:

                        df = pd.DataFrame(result, columns=["Område", "Periode", "Arbejdsmarkedsstatus", "Status 3 mdr. efter afsluttet forløb, pct."])
                        df["Status 3 mdr. efter afsluttet forløb, pct."] = pd.to_numeric(df["Status 3 mdr. efter afsluttet forløb, pct."], errors='coerce')
                        df["Periode"] = df["Periode"].str.replace('QMAT0', '-K')
                        df["År"] = df["Periode"].str[:4].astype(int)
                        df = df[df["År"] >= today.year - 4]


                        fig, ax = plt.subplots(figsize=(8, 4))
                        colors = {'Lønmodtagerbeskæftigelse': '#00B050', 'Uddannelse': '#FFC000', 'Fleksjob': '#FF0000', 'Selvforsørgelse': '#00B0F0'}
                        for Arbejdsmarkedsstatus, group in df.groupby("Arbejdsmarkedsstatus"):
                            ax.plot(group['Periode'], group['Status 3 mdr. efter afsluttet forløb, pct.'], label=Arbejdsmarkedsstatus, color=colors.get(Arbejdsmarkedsstatus, 'black'))
                        ax.set_xlabel('Tid')
                        ax.set_ylabel('Procent')
                        ax.set_title('Aktivitetsparate kontanthjælpsmodtagere: Status 3 mdr. efter afsluttet forløb, pct.')
                        ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                        ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        handles, labels = ax.get_legend_handles_labels()
                        sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: 0 if x[1] == "Randers" else 1)
                        handles, labels = zip(*sorted_handles_labels)
                        ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                        fig.autofmt_xdate()
                        st.pyplot(fig, use_container_width=False)

            with st.container(border=1):
                st.subheader("2 - Aktivitetsparate kontanthjælpsmodtagere: Varighed af afsluttede aktiveringsforløb")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                with col1:
                    st.markdown(f"""
                        #### Mål
                        ...

                        #### Noter
                        ...

                        #### Kilde
                        Jobindsats.dk

                            y60c06
                                - Sidst opdateret:  {LastUpdate('y60c06')}
                                - Næste opdatering: {NextUpdate('y60c06')}
                    """)

                with col2:
                    query = (
                        'SELECT "Område", "Periode", "Gnsn. varighed, afsluttede aktiveringsforløb, uger", "Periode Aktivitetsparate kontanthjælpsmodtagere varighed af af" FROM jobindsats_y60c06 order by "Periode" asc;'
                    ) 

                    result = db_client.execute_sql(query)

                    if not result: 
                        st.warning("Data ikke tilgængelige")
                    else:

                        df = pd.DataFrame(result, columns=["Område", "Periode", "Gnsn. varighed, afsluttede aktiveringsforløb, uger", "Periode (timestamp)"])

                        df["Gnsn. varighed, afsluttede aktiveringsforløb, uger"] = pd.to_numeric(df["Gnsn. varighed, afsluttede aktiveringsforløb, uger"], errors='coerce') 

                        df = date_parser(df, "Periode")    


                        fig, ax = plt.subplots(figsize=(8, 4))
                        colors = {'Randers': '#00B050', 'Hele landet': '#FFC000'}
                        for Område, group in df.groupby("Område"):
                            ax.plot(group['Periode'], group['Gnsn. varighed, afsluttede aktiveringsforløb, uger'], label=Område, color=colors.get(Område, 'black'))
                        ax.set_xlabel('Tid')
                        ax.set_ylabel('Uger')
                        ax.set_title('Aktivitetsparate kontanthjælpsmodtagere: Varighed af afsluttede aktiveringsforløb')
                        ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                        # ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        handles, labels = ax.get_legend_handles_labels()
                        sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: 0 if x[1] == "Randers" else 1)
                        handles, labels = zip(*sorted_handles_labels)
                        ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                        fig.autofmt_xdate()
                        st.pyplot(fig, use_container_width=False)

        except Exception as e:
            st.error(f"""{e}
            """)
            return
        finally:
            db_client.close_connection()
