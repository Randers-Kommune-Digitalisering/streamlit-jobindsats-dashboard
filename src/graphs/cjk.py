import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from utils.database_connection import get_jobindsats_db
from matplotlib.ticker import FuncFormatter

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

    ## Mål 1.a og 1.b 
    query = (
        'SELECT "Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år" FROM jobindsats_y25i01 where "Område" IN (\'Randers\', \'Aarhus\', \'Favrskov\', \'Horsens\', \'Norddjurs\', \'Odder\', \'Samsø\',  \'Skanderborg\',  \'Syddjurs\') order by "Periode" desc;'
    )

    result = db_client.execute_sql(query)

    df = pd.DataFrame(result, columns=["Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år"])

    with st.container():
        
        col1, col2 = st.columns([1,3], vertical_alignment="top", gap="large")
        with col1:
            st.subheader("1.a Sæsonkorrigeret ledighedsudvikling i pct. af arbejdsstyrken 16-66 år")
            st.markdown("""
                | Forklaringer  |  |
                |---------------|------------------------|  
                | **Mål:**      | ... |  
                | **Kilde:**    | Jobindsats - y25i01 | 
                | **Noter:**    | Østjylland: Aarhus, Favrskov, Horsens, Norddjurs, Odder, Samsø, Skanderborg og Syddjurs | 
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

            import matplotlib.pyplot as plt

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
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)
        
    with st.container():
        
        col1, col2 = st.columns([1,3], vertical_alignment="top", gap="large")
        with col1:
            st.subheader("1.b Sæsonkorrigeret ledighedsudvikling i pct. af befolkningen 16-66 år")
            st.markdown("""
                | Forklaringer  |  |
                |---------------|------------------------|
                | **Mål:**      | ... |    
                | **Kilde:**    | Jobindsats - y25i01 | 
                | **Noter:**    | Østjylland: Aarhus, Favrskov, Horsens, Norddjurs, Odder, Samsø, Skanderborg og Syddjurs | 
            """)

        with col2: 

            chart_df1 = df[["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år"]]
            chart_df1["Ledige fuldtidspersoner i pct. af befolkningen16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen16-66 år"], errors='coerce')

            date_parser(chart_df1, "Periode")

            chart_df1["År"] = chart_df1["Periode"].dt.year
            chart_df1["Måned"] = chart_df1["Periode"].dt.month

            chart_df1 = chart_df1[chart_df1["År"] >= today.year - 2 ]

            chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else "Østjylland")
            grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen16-66 år'].mean().reset_index()

            # Pyplot chart for the same data
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Randers': '#00B050', 'Østjylland': '#FFC000'}
            for område, group in grouped_df1.groupby("Område_split"):
                ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen16-66 år'], label=område, color=colors.get(område, 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Procent')
            ax.set_title('Ledige fuldtidspersoner i pct. af befolkningen 16-66 år')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    ## Mål 2:

    ### Dagpenge
    query_dp = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y01a02 where "Område" IN (\'Randers\') order by "Periode" desc;'
    )

    result_dp = db_client.execute_sql(query_dp)

    df_dp = pd.DataFrame(result_dp, columns=["Periode", "Antal fuldtidspersoner"])
    df_dp["Ydelse"]="Dagpengemodtagere"
    

    ### Jobparate kontanthjælpsmodtagere
    query_jpkh = (
        'SELECT "Periode", "Antal fuldtidspersoner" FROM jobindsats_y60a02 where "Område" IN (\'Randers\') and "Visitationskategori" IN (\'Jobparat\') order by "Periode" desc;'
    )

    result_jpkh = db_client.execute_sql(query_jpkh)
    df_jpkh = pd.DataFrame(result_jpkh, columns=["Periode", "Antal fuldtidspersoner"])
    df_jpkh["Ydelse"]="Jobparate kontanthjælpsmodtagere"

    ### Samlet dataframe
    df = pd.concat([df_dp, df_jpkh], ignore_index=True)

    with st.container():
        
        col1, col2 = st.columns([1,3], vertical_alignment="top", gap="large")
        with col1:
            st.subheader("2.a Antal på offentlig forsørgelse i CJK")
            st.markdown("""
                | Forklaringer  |  |
                |---------------|------------------------|
                | **Mål:**      | Reduktion ift. baseline |    
                | **Kilde:**    | Jobindsats: y01a02 (dagpenge), kontanthjælp (y60a02)| 
                | **Noter:**    | Ydelsesgrupper: A-dagpengemodtagere, jobparate kontakthjælpsmodtagere, integrationsborgere, ledighedsydelsesmodtagere | 
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
            ax.plot(chart_df['Periode'], chart_df['Antal fuldtidspersoner'], label='Antal', color=colors.get('Randers', 'black'))
            ax.set_xlabel('Tid')
            ax.set_ylabel('Fuldtidspersoner')
            ax.set_title('Antal fuldtidspersoner på offentlig forsørgelse i CJK')
            ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.set_major_formatter(FuncFormatter(thousands_dot))
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
            fig.autofmt_xdate()
            st.pyplot(fig, use_container_width=False)

    with st.container(border=1):
        st.subheader("2.b Antal på offentlig forsørgelse i CJK opdelt på målgruppe")
        col1, col2 = st.columns([1,3], vertical_alignment="top", gap="large")
        
        with col1:
            st.markdown(""" 
                #### Mål 
                Reduktion ift. baseline

                #### Noter
                Ydelsesgrupper er a-dagpengemodtagere, jobparate kontanthjælpsmodtagere, integrationsborgere, ledighedsydelsesmodtagere 

                #### Kilde 
                Jobindsats.dk
          
                    y01a02 (dagpenge)
                    y60a02 (kontanthjælp)        

            """)

        with col2:
            chart_df = df[["Periode", "Antal fuldtidspersoner", "Ydelse"]]
            chart_df["Antal fuldtidspersoner"] = pd.to_numeric(chart_df["Antal fuldtidspersoner"], errors='coerce')

            date_parser(chart_df, "Periode")

            chart_df["År"] = chart_df["Periode"].dt.year
            chart_df["Måned"] = chart_df["Periode"].dt.month

            chart_df = chart_df[chart_df["År"] >= today.year - 2 ]
            grouped_df = chart_df.groupby(['Periode', 'Ydelse'])['Antal fuldtidspersoner'].mean().reset_index()

            # Pyplot chart for the same data
            fig, ax = plt.subplots(figsize=(8, 4))
            colors = {'Dagpengemodtagere': '#00B050', 'Jobparate kontanthjælpsmodtagere': '#FFC000'}
            for ydelse, group in grouped_df.groupby("Ydelse"): 
                ax.plot(group['Periode'], group['Antal fuldtidspersoner'], label=ydelse, color=colors.get(ydelse, 'black'))
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

