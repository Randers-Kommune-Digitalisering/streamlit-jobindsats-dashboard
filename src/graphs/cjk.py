import streamlit as st
import pandas as pd
from utils.database_connection import get_jobindsats_db
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt

db_client = get_jobindsats_db()


def date_parser(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column].str.replace('M', '-'), format='%Y-%m')
    return df


def percent_comma(x, pos):
    return f"{x:,.1f}%".replace('.', ',')


def thousands_dot(x, pos):
    return f"{int(x):,}".replace(",", ".")


def cjk_page():
    st.header("Overordnede mål")
    today = pd.to_datetime("today")

    # Mål 1.a og 1.b
    query = (
        'SELECT "Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år" FROM jobindsats_y25i01 where "Område" IN (\'Randers\', \'Aarhus\', \'Favrskov\', \'Horsens\', \'Norddjurs\', \'Odder\', \'Samsø\',  \'Skanderborg\',  \'Syddjurs\') order by "Periode" desc;'
    )

    result = db_client.execute_sql(query)

    df = pd.DataFrame(result, columns=["Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"])

    with st.container(border=1):
        st.subheader("1.a - Sæsonkorrigeret ledighedsudvikling i pct. af arbejdsstyrken 16-66 år")
        col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
        with col1:
            st.markdown("""
                #### Mål
                ...

                #### Noter
                Østjylland: Aarhus, Favrskov, Horsens, Norddjurs, Odder, Samsø, Skanderborg og Syddjurs

                #### Kilde
                Jobindsats.dk

                    y25i01
            """)
        with col2:
            chart_df = df[["Område", "Periode", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år"]]
            chart_df["Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år"] = pd.to_numeric(chart_df["Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år"], errors='coerce')

            date_parser(chart_df, "Periode")

            chart_df["År"] = chart_df["Periode"].dt.year
            chart_df["Måned"] = chart_df["Periode"].dt.month

            chart_df = chart_df[chart_df["År"] >= today.year - 2 ]

            chart_df["Område_split"] = chart_df["Område"].apply(lambda x: "Randers" if x == "Randers" else "Østjylland")
            grouped_df = chart_df.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år'].mean().reset_index()

            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
            for område, group in grouped_df.groupby("Område_split"):
                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år'], label=område, color=colors.get(område, 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Procent')
            ax.set_title('Sæsonkorrigeret ledighed i procent af arbejdsstyrken 16-66 år')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    with st.container(border=1):
        st.subheader("1.b - Sæsonkorrigeret ledighedsudvikling i pct. af befolkningen 16-66 år")
        col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
        with col1:
            st.markdown("""
                #### Mål
                ...

                #### Noter
                Østjylland: Aarhus, Favrskov, Horsens, Norddjurs, Odder, Samsø, Skanderborg og Syddjurs

                #### Kilde
                Jobindsats.dk

                    y25i01
            """)
        with col2:

            chart_df1 = df[["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"]]
            chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"], errors='coerce')

            date_parser(chart_df1, "Periode")

            chart_df1["År"] = chart_df1["Periode"].dt.year
            chart_df1["Måned"] = chart_df1["Periode"].dt.month

            chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

            chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else "Østjylland")
            grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].mean().reset_index()

            # Pyplot chart for the same data
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
            for område, group in grouped_df1.groupby("Område_split"):
                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'], label=område, color=colors.get(område, 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Procent')
            ax.set_title('Ledige fuldtidspersoner i pct. af befolkningen 16-66 år')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    # Mål 2:

    # Dagpenge
    query_dp = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y01a02 where "Område" IN (\'Randers\') order by "Periode" desc;'
    )

    result_dp = db_client.execute_sql(query_dp)

    df_dp = pd.DataFrame(result_dp, columns=["Periode", "Antal fuldtidspersoner"])
    df_dp["Ydelse"]="Dagpengemodtagere"

    # Jobparate kontanthjælpsmodtagere
    query_jpkh = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y60a02jobparat_satser where "Område" IN (\'Randers\') and "Visitationskategori" IN (\'Jobparat\') and "Kontanthjælpssats" IN (\'Forhøjet sats\',\'Grundsats\') order by "Periode" desc;'
    )

    result_jpkh = db_client.execute_sql(query_jpkh)
    df_jpkh = pd.DataFrame(result_jpkh, columns=["Periode", "Antal fuldtidspersoner"])
    df_jpkh["Ydelse"] = "Jobparate kontanthjælpsmodtagere"

    # Integrationsborgere
    query_int = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y60a02satser where "Område" IN (\'Randers\') and "Kontanthjælpssats" IN (\'Mindstesats omfattet af program\',\'Mindstesats øvrige\') order by "Periode" desc;'
    )

    result_int = db_client.execute_sql(query_int)
    df_int = pd.DataFrame(result_int, columns=["Periode", "Antal fuldtidspersoner"])
    df_int["Ydelse"] = "Integrationsborgere"

    # Ledighedsydelsesmodtagere
    query_lyd = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y09a02 where "Område" IN (\'Randers\') order by "Periode" desc;'
    )

    result_lyd = db_client.execute_sql(query_lyd)
    df_lyd = pd.DataFrame(result_lyd, columns=["Periode", "Antal fuldtidspersoner"])
    df_lyd["Ydelse"] = "Ledighedsydelsesmodtagere"

    # Samlet dataframe
    df = pd.concat([df_dp, df_jpkh, df_int, df_lyd], ignore_index=True)

    with st.container(border=1):
        st.subheader("2.a - Antal på offentlig forsørgelse i CJK")
        col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
        with col1:
            st.markdown("""
                #### Mål
                Reduktion ift. baseline

                #### Noter
                Ydelsesgrupperne er:

                * A-dagpengemodtagere
                * Jobparate kontanthjælpsmodtagere
                    * Kontanthjælp forhøjet sats
                    * Kontanthjælp grundsats
                * Integrationsborgere 
                    * Kontanthjælp mindstesats omfattet af program
                    * Kontanthjælp mindstesats øvrige
                * Ledighedsydelsesmodtagere

                #### Kilde
                Jobindsats.dk

                    y01a02 (dagpenge)
                    y60a02 (kontanthjælp)
                    y09a02 (ledighedsydelse)

            """)

        with col2:
            chart_df = df[["Periode", "Antal fuldtidspersoner", "Ydelse"]]
            chart_df["Antal fuldtidspersoner"] = pd.to_numeric(chart_df["Antal fuldtidspersoner"], errors='coerce')

            date_parser(chart_df, "Periode")

            chart_df["År"] = chart_df["Periode"].dt.year
            chart_df["Måned"] = chart_df["Periode"].dt.month

            chart_df = chart_df[chart_df["År"] >= today.year - 2 ]

            chart_df = chart_df.groupby(['Periode'])['Antal fuldtidspersoner'].sum().reset_index()

            # Pyplot chart for the same data
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
            ax.plot(chart_df['Periode'], chart_df['Antal fuldtidspersoner'], label='Fuldtidspersoner', color=colors.get('Randers', 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Fuldtidspersoner')
            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    with st.container(border=1):
        st.subheader("2.b - Antal på offentlig forsørgelse i CJK opdelt på målgruppe")
        col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
        
        with col1:
            st.markdown(""" 
                #### Mål 
                Reduktion ift. baseline

                #### Noter
                Ydelsesgrupperne er:

                * A-dagpengemodtagere
                * Jobparate kontanthjælpsmodtagere
                    * Kontanthjælp forhøjet sats
                    * Kontanthjælp grundsats
                * Integrationsborgere 
                    * Kontanthjælp mindstesats omfattet af program
                    * Kontanthjælp mindstesats øvrige
                * Ledighedsydelsesmodtagere

                #### Kilde
                Jobindsats.dk

                    y01a02 (dagpenge)
                    y60a02 (kontanthjælp)
                    y09a02 (ledighedsydelse)
                        
            """)

        with col2:
            chart_df = df[["Periode", "Antal fuldtidspersoner", "Ydelse"]]
            chart_df["Antal fuldtidspersoner"] = pd.to_numeric(chart_df["Antal fuldtidspersoner"], errors='coerce')

            date_parser(chart_df, "Periode")

            chart_df["År"] = chart_df["Periode"].dt.year
            chart_df["Måned"] = chart_df["Periode"].dt.month

            chart_df = chart_df[chart_df["År"] >= today.year - 2 ]
            grouped_df = chart_df.groupby(['Periode', 'Ydelse'])['Antal fuldtidspersoner'].sum().reset_index()

            # Pyplot chart for the same data
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Dagpengemodtagere': '#00B050', 'Jobparate kontanthjælpsmodtagere': '#FFC000', 'Integrationsborgere': '#FF0000', 'Ledighedsydelsesmodtagere': '#00B0F0'}
            for ydelse, group in grouped_df.groupby("Ydelse"): 
                ax.plot(group['Periode'], group['Antal fuldtidspersoner'], label = ydelse, color=colors.get(ydelse, 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Fuldtidspersoner')
            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    # Mål 3:

    query = (
        'SELECT "Periode", "Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m", "Opdeling af ydelser", "Område" FROM jobindsats_y25i08 where "Område" IN (\'Randers\', \'Hele landet\') order by "Periode" asc;'
    )

    result = db_client.execute_sql(query)

    df = pd.DataFrame(result, columns=["Periode", "Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m", "Opdeling af ydelser", "Område"])
    df["Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m"] = pd.to_numeric(df["Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m"], errors='coerce')
    df["Periode"] = df["Periode"].str.replace('QMAT0', '-K')

    df["År"] = df["Periode"].str[:4].astype(int)
    df = df[df["År"] >= today.year - 4]


    with st.container(border=1):
        st.subheader("3.a - Afgang til beskæftigelse 6 måneder efter nyledighed")
        col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
        
        with col1:
            st.markdown(""" 
                #### Mål 
                Reduktion ift. baseline

                #### Noter
                Ydelsesgrupperne er:

                * A-dagpengemodtagere
                * Kontanthjælpsmodtagere

                Grafen viser gennemsnit seneste 4 kvartaler

                #### Kilde
                Jobindsats.dk

                    y25i08 
               
            """)

        with col2:
            chart_df = df[df["Opdeling af ydelser"] == "I alt"]

            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Randers': '#00B050', 'Hele landet': '#FFC000'}
            for område, group in chart_df.groupby("Område"):
                ax.plot(group['Periode'], group['Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m'], label=område, color=colors.get(område, 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Procent')
            ax.set_title('Andel i beskæftigelse 6 måneder efter nyledighed')
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