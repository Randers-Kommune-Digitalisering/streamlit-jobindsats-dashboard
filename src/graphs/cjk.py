import streamlit as st
import pandas as pd
from utils.database_connection import get_jobindsats_db
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from utils.func import LastUpdate, NextUpdate, ComparisonGroupDropdown, render_vector_downloads, render_vector_downloads_nocol

db_client = get_jobindsats_db()

def date_parser(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column].str.replace('M', '-'), format='%Y-%m')
    return df

def percent_comma(x, pos):
    return f"{x:,.1f}%".replace('.', ',')

def thousands_dot(x, pos):
    return f"{int(x):,}".replace(",", ".")

def cjk_page(afdeling):

    comparison_groups = {
        "Hele landet": ["Randers", "Hele landet"],
        "Østjylland": ["Randers", "Aarhus", "Favrskov", "Horsens", "Norddjurs", "Odder", "Samsø", "Skanderborg", "Syddjurs"]
    }

    if afdeling == "CJK - fælles mål":
        try:
            st.header("Overordnede mål")
            today = pd.to_datetime("today")

            with st.container(border=1):
                st.subheader("1 - Ledighedsudvikling i pct. af befolkningen 16-66 år")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                with col1:
                    st.markdown(f"""
                        #### Mål
                        Følge udviklingen i Østjylland 

                        #### Noter
                        Østjylland: Aarhus, Favrskov, Horsens, Norddjurs, Odder, Samsø, Skanderborg og Syddjurs

                        #### Kilde
                        Jobindsats.dk

                            y25i01
                            - Sidst opdateret:  {LastUpdate('y25i01')}
                            - Næste opdatering: {NextUpdate('y25i01')}

                        #### Vælg sammenligningsgruppe
                    """)
                    ComparisonGroup, ComparisonGroupName = ComparisonGroupDropdown("Vælg sammenligningsgruppe", comparison_groups, key="comparison_group", default=1, visible=False)


                with col2:
                    # Mål 1
                    query = (
                        'SELECT "Område", "Periode", "Antal ledige personer", "Alder", "Ydelsesgrupper", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år" FROM jobindsats_y25i01 where "Område" = ANY(%s) order by "Periode" desc;'
                    )

                    result = db_client.execute_sql(query, (ComparisonGroup,))

                    if not result:
                        st.warning("Data ikke tilgængelige")
                    else:

                        df = pd.DataFrame(result, columns=["Område", "Periode", "Antal ledige personer", "Alder", "Ydelsesgrupper", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"])

                        # Select where Alder="Alder i alt", ydelsegrupper="I alt" and Område in Randers, Østjylland
                        chart_df1 = df[(df["Alder"] == "Alder i alt") & (df["Ydelsesgrupper"] == "Ydelsesgrupper i alt")][["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"]]
                        chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"], errors='coerce')

                        date_parser(chart_df1, "Periode")

                        chart_df1["År"] = chart_df1["Periode"].dt.year
                        chart_df1["Måned"] = chart_df1["Periode"].dt.month

                        chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

                        chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else ComparisonGroupName)
                        grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].mean().reset_index()

                        # Pyplot chart for the same data
                        fig, ax = plt.subplots(figsize=(8, 4))
                        colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                        for område, group in grouped_df1.groupby("Område_split"):
                            ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'], label=område, color=colors.get(område, 'black'))
                        ax.set_xlabel('Tid')
                        ax.set_ylabel('Procent af befolkningen 16-66 år')
                        ax.set_title('Ledige fuldtidspersoner')
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
                        render_vector_downloads_nocol(fig, f"Ledighedsudvikling - Ledige fuldtidspersoner")

                        col21, col22 = st.columns([1, 1], vertical_alignment="top", gap="small")
                        with col21:

                            grouped_df1_pivot = grouped_df1.pivot(index='Periode', columns='Område_split', values='Ledige fuldtidspersoner i pct. af befolkningen 16-66 år').reset_index()
                            grouped_df1_pivot['Difference'] = grouped_df1_pivot['Randers'] - grouped_df1_pivot[ComparisonGroupName]
                            fig, ax = plt.subplots(figsize=(8, 4))

                            colors = {f'Difference: Randers - {ComparisonGroupName}': '#00B0F0'}
                            ax.plot(grouped_df1_pivot['Periode'], grouped_df1_pivot['Difference'], label=f'Difference: Randers - {ComparisonGroupName}', color=colors.get(f'Difference: Randers - {ComparisonGroupName}', 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent af befolkningen 16-66 år')
                            ax.set_title(f'Ledige fuldtidspersoner: Difference Randers vs {ComparisonGroupName}')
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
                            render_vector_downloads_nocol(fig, f"Ledighedsudvikling - Ledige fuldtidspersoner - Difference Randers vs {ComparisonGroupName}")

                        with col22:
                            chart_df1 = df[(df["Alder"] != "Alder i alt") & (df["Ydelsesgrupper"] == "Ydelsesgrupper i alt")][["Område", "Periode", "Alder", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"]]
                            chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"], errors='coerce')

                            date_parser(chart_df1, "Periode")

                            chart_df1["År"] = chart_df1["Periode"].dt.year
                            chart_df1["Måned"] = chart_df1["Periode"].dt.month

                            chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

                            chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else ComparisonGroupName)
                            grouped_df1 = chart_df1.groupby(['Periode', 'Alder', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].mean().reset_index()

                            grouped_df1 = grouped_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].sum().reset_index()

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                            for område, group in grouped_df1.groupby("Område_split"):
                                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'], label=område, color=colors.get(område, 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent af befolkningen 16-66 år')
                            ax.set_title('Ledige fuldtidspersoner: Unge 16-29 år')
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
                            render_vector_downloads_nocol(fig, f"Ledighedsudvikling - Ledige fuldtidspersoner - Unge 16-29 år")

                        col21, col22 = st.columns([1, 1], vertical_alignment="top", gap="small")
                        with col21:
                            chart_df1 = df[(df["Alder"] == "Alder i alt") & (df["Ydelsesgrupper"] == "A-dagpenge")][["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"]]
                            chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"], errors='coerce')

                            date_parser(chart_df1, "Periode")

                            chart_df1["År"] = chart_df1["Periode"].dt.year
                            chart_df1["Måned"] = chart_df1["Periode"].dt.month

                            chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

                            chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else ComparisonGroupName)
                            grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].mean().reset_index()


                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                            for område, group in grouped_df1.groupby("Område_split"):
                                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'], label=område, color=colors.get(område, 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent af befolkningen 16-66 år')
                            ax.set_title('Ledige fuldtidspersoner: A-dagpenge')
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
                            render_vector_downloads_nocol(fig, f"Ledighedsudvikling - Ledige fuldtidspersoner - A-dagpenge")

                        with col22:
                            chart_df1 = df[(df["Alder"] == "Alder i alt") & (df["Ydelsesgrupper"] == "Kontanthjælp")][["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"]]
                            chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen 16-66 år"], errors='coerce')

                            date_parser(chart_df1, "Periode")

                            chart_df1["År"] = chart_df1["Periode"].dt.year
                            chart_df1["Måned"] = chart_df1["Periode"].dt.month

                            chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

                            chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else ComparisonGroupName)
                            grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'].mean().reset_index()


                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                            for område, group in grouped_df1.groupby("Område_split"):
                                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen 16-66 år'], label=område, color=colors.get(område, 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent af befolkningen 16-66 år')
                            ax.set_title('Ledige fuldtidspersoner: Kontanthjælp')
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
                            render_vector_downloads_nocol(fig, f"Ledighedsudvikling - Ledige fuldtidspersoner - Kontanthjælp")


            # Mål 2:
            with st.container(border=1):
                st.subheader("2 - Antal på offentlig forsørgelse i CJK")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                with col1:
                    st.markdown(f"""
                        #### Mål
                        Reduktion ift. baseline

                        #### Noter
                        Ydelsesgrupperne er:

                        * A-dagpengemodtagere
                        * Jobparate kontanthjælpsmodtagere
                            * Kontanthjælp forhøjet sats
                            * Kontanthjælp grundsats
                            * Kontanthjælp mindstesats øvrige
                        * Integrationsborgere 
                            * Kontanthjælp mindstesats omfattet af program
                        * Ledighedsydelsesmodtagere

                        #### Kilde
                        Jobindsats.dk

                            y01a02 (dagpenge)
                                - Sidst opdateret:  {LastUpdate('y01a02')}
                                - Næste opdatering: {NextUpdate('y01a02')}
                            y60a02 (kontanthjælp)
                                - Sidst opdateret:  {LastUpdate('y60a02')}
                                - Næste opdatering: {NextUpdate('y60a02')}
                            y09a02 (ledighedsydelse)
                                - Sidst opdateret:  {LastUpdate('y09a02')}
                                - Næste opdatering: {NextUpdate('y09a02')}

                    """)

                with col2:
                    # Dagpenge
                    query_dp = ('SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y01a02 where "Område" IN (\'Randers\') order by "Periode" desc;')
                    result_dp = db_client.execute_sql(query_dp)

                    # Jobparate kontanthjælpsmodtagere
                    query_jpkh = ('SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y60a02jobparat_satser where "Område" IN (\'Randers\') and "Visitationskategori" IN (\'Jobparat\') and "Kontanthjælpssats" IN (\'Forhøjet sats\',\'Grundsats\',\'Mindstesats øvrige\') order by "Periode" desc;')
                    result_jpkh = db_client.execute_sql(query_jpkh)

                    # Integrationsborgere
                    query_int = ('SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y60a02satser where "Område" IN (\'Randers\') and "Kontanthjælpssats" IN (\'Mindstesats omfattet af program\') order by "Periode" desc;')
                    result_int = db_client.execute_sql(query_int)

                    # Ledighedsydelsesmodtagere
                    query_lyd = ('SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y09a02 where "Område" IN (\'Randers\') order by "Periode" desc;')
                    result_lyd = db_client.execute_sql(query_lyd)

                    if not (result_dp and result_jpkh and result_int and result_lyd):
                        st.warning("Data ikke tilgængelige")
                    else:
                        # Samlet dataframe
                        df_dp = pd.DataFrame(result_dp, columns=["Periode", "Antal fuldtidspersoner"])
                        df_dp["Ydelse"]="Dagpengemodtagere"

                        df_jpkh = pd.DataFrame(result_jpkh, columns=["Periode", "Antal fuldtidspersoner"])
                        df_jpkh["Ydelse"] = "Jobparate kontanthjælpsmodtagere"

                        df_int = pd.DataFrame(result_int, columns=["Periode", "Antal fuldtidspersoner"])
                        df_int["Ydelse"] = "Integrationsborgere"

                        df_lyd = pd.DataFrame(result_lyd, columns=["Periode", "Antal fuldtidspersoner"])
                        df_lyd["Ydelse"] = "Ledighedsydelsesmodtagere"

                        df = pd.concat([df_dp, df_jpkh, df_int, df_lyd], ignore_index=True)

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
                        render_vector_downloads_nocol(fig, f"Antal fuldtidspersoner på offentlig forsørgelse i CJK")

                        col21, col22 = st.columns([1, 1], vertical_alignment="top", gap="small")
                        with col21:
                            chart_df = df[["Periode", "Antal fuldtidspersoner", "Ydelse"]]
                            chart_df["Antal fuldtidspersoner"] = pd.to_numeric(chart_df["Antal fuldtidspersoner"], errors='coerce')

                            date_parser(chart_df, "Periode")

                            chart_df["År"] = chart_df["Periode"].dt.year
                            chart_df["Måned"] = chart_df["Periode"].dt.month

                            chart_df = chart_df[chart_df["År"] >= today.year - 2 ]
                            grouped_df = chart_df.groupby(['Periode', 'Ydelse'])['Antal fuldtidspersoner'].sum().reset_index()

                            chart1_df = grouped_df[grouped_df["Ydelse"] == "Dagpengemodtagere"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
                            ax.plot(chart1_df['Periode'], chart1_df['Antal fuldtidspersoner'], label='Fuldtidspersoner', color=colors.get('Randers', 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Fuldtidspersoner')
                            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK:\n Dagpengemodtagere')
                            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
                            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                            fig.autofmt_xdate()
                            st.pyplot(fig, use_container_width=False)
                            render_vector_downloads_nocol(fig, f"Antal fuldtidspersoner på offentlig forsørgelse i CJK - Dagpengemodtagere")

                        with col22:
                            chart1_df = grouped_df[grouped_df["Ydelse"] == "Jobparate kontanthjælpsmodtagere"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
                            ax.plot(chart1_df['Periode'], chart1_df['Antal fuldtidspersoner'], label='Fuldtidspersoner', color=colors.get('Randers', 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Fuldtidspersoner')
                            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK:\n Jobparate kontanthjælpsmodtagere')
                            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
                            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                            fig.autofmt_xdate()
                            st.pyplot(fig, use_container_width=False)
                            render_vector_downloads_nocol(fig, f"Antal fuldtidspersoner på offentlig forsørgelse i CJK - Jobparate kontanthjælpsmodtagere")

                        col21, col22 = st.columns([1, 1], vertical_alignment="top", gap="small")
                        with col21:
                            chart1_df = grouped_df[grouped_df["Ydelse"] == "Integrationsborgere"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
                            ax.plot(chart1_df['Periode'], chart1_df['Antal fuldtidspersoner'], label='Fuldtidspersoner', color=colors.get('Randers', 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Fuldtidspersoner')
                            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK:\n Integrationsborgere')
                            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
                            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                            fig.autofmt_xdate()
                            st.pyplot(fig, use_container_width=False)
                            render_vector_downloads_nocol(fig, f"Antal fuldtidspersoner på offentlig forsørgelse i CJK - Integrationsborgere")

                        with col22:
                            chart1_df = grouped_df[grouped_df["Ydelse"] == "Ledighedsydelsesmodtagere"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
                            ax.plot(chart1_df['Periode'], chart1_df['Antal fuldtidspersoner'], label='Fuldtidspersoner', color=colors.get('Randers', 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Fuldtidspersoner')
                            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK:\n Ledighedsydelsesmodtagere')
                            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
                            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)
                            fig.autofmt_xdate()
                            st.pyplot(fig, use_container_width=False)
                            render_vector_downloads_nocol(fig, f"Antal fuldtidspersoner på offentlig forsørgelse i CJK - Ledighedsydelsesmodtagere")

            # Mål 3:
            with st.container(border=1):
                st.subheader("3 - Afgang til beskæftigelse 6 måneder efter nyledighed")
                col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
                
                with col1:
                    st.markdown(f""" 
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
                                - Sidst opdateret:  {LastUpdate('y25i08')}
                                - Næste opdatering: {NextUpdate('y25i08')} 
                    
                        #### Vælg sammenligningsgruppe
                    """)
                    ComparisonGroup, ComparisonGroupName = ComparisonGroupDropdown("Vælg sammenligningsgruppe", comparison_groups, key="comparison_group1", default=1, visible=False)


                with col2:
                    query = ('SELECT "Periode", "Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m", "Opdeling af ydelser", "Område" FROM jobindsats_y25i08 where "Område" = ANY(%s) order by "Periode" asc;')
                    result = db_client.execute_sql(query, (ComparisonGroup,))

                    if result is None:
                        st.warning("Data ikke tilgængelige")
                    else:
                        df = pd.DataFrame(result, columns=["Periode", "Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m", "Opdeling af ydelser", "Område"])
                        df["Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m"] = pd.to_numeric(df["Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m"], errors='coerce')
                        df["Periode"] = df["Periode"].str.replace('QMAT0', '-K')
                        df["År"] = df["Periode"].str[:4].astype(int)
                        df = df[df["År"] >= today.year - 4]
                        df["Område_split"] = df["Område"].apply(lambda x: "Randers" if x == "Randers" else ComparisonGroupName)

                        grouped_df = df.groupby(['Periode', 'Område_split', 'Opdeling af ydelser'])['Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m'].mean().reset_index()
                        chart_df = grouped_df[grouped_df["Opdeling af ydelser"] == "I alt"]

                        fig, ax = plt.subplots(figsize=(8, 4))
                        colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                        for område, group in chart_df.groupby("Område_split"):
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
                        render_vector_downloads_nocol(fig, f"Andel i beskæftigelse 6 måneder efter nyledighed")

                        col21, col22 = st.columns([1, 1], vertical_alignment="top", gap="small")
                        with col21:
                            chart_df = grouped_df[grouped_df["Opdeling af ydelser"] == "A-dagpenge"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                            for område, group in chart_df.groupby("Område_split"):
                                ax.plot(group['Periode'], group['Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m'], label=område, color=colors.get(område, 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent')
                            ax.set_title('Andel i beskæftigelse 6 måneder efter nyledighed:\n A-dagpenge')
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
                            render_vector_downloads_nocol(fig, f"Andel i beskæftigelse 6 måneder efter nyledighed - A-dagpenge")

                        with col22:
                            chart_df = grouped_df[grouped_df["Opdeling af ydelser"] == "Kontanthjælp"]

                            fig, ax = plt.subplots(figsize=(8, 4))
                            colors = {'Randers': '#00B050', ComparisonGroupName: '#FFC000'}
                            for område, group in chart_df.groupby("Område_split"):
                                ax.plot(group['Periode'], group['Andel i beskæftigelse 3, 6, 9 og 12 mdr. efter nyledighed: 6 m'], label=område, color=colors.get(område, 'black'))
                            ax.set_xlabel('Tid')
                            ax.set_ylabel('Procent')
                            ax.set_title('Andel i beskæftigelse 6 måneder efter nyledighed:\n Kontanthjælp')
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
                            render_vector_downloads_nocol(fig, f"Andel i beskæftigelse 6 måneder efter nyledighed - Kontanthjælp")



        except Exception as e:
            st.exception(e)
            return
        finally:
            db_client.close_connection()