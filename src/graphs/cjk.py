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

def cjk_page():

    st.header("Overordnede mål")
    

    # querytest = (
    #     'SELECT * from jobindsats_y25i01'
    # )
    # resulttest = db_client.execute_sql(querytest)
    # dftest = pd.DataFrame(resulttest)

    # st.write(dftest)

    # i dag
    today = pd.to_datetime("today")

    query = (
        'SELECT "Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år" FROM jobindsats_y25i01 where "Område" IN (\'Randers\', \'Aarhus\', \'Favrskov\', \'Horsens\', \'Norddjurs\', \'Odder\', \'Samsø\',  \'Skanderborg\',  \'Syddjurs\') order by "Periode" desc;'
    )

    result = db_client.execute_sql(query)

    df = pd.DataFrame(result, columns=["Område", "Periode", "Antal ledige personer", "Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år"])

    with st.container():
        
        col1, col2 = st.columns([1,3], vertical_alignment="top")
        # st.write(df)
        with col1:
            st.subheader("1. Sæsonkorrigeret ledighedsudvikling")
            st.markdown("""
                | Forklaringer  |  |
                |---------------|------------------------|    
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

            # st.write(chart_df)

            # chart = alt.Chart(chart_df).mark_line(point=True).encode(
            # x=alt.X('Periode:T', title='Måned'),  # Use temporal type for dates
            # y=alt.Y('Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år:Q', title="Sæsonkorrigeret ledighedsprocent"),
            # tooltip=[
            #     alt.Tooltip('Periode:T', title='Måned', format='%Y-%m'),
            #     alt.Tooltip('Ledige fuldtidspersoner i pct. af arbejdsstyrken 16-66 år:Q', title="Sæsonkorrigeret ledighedsprocent", format='.2f')
            # ]
            # )

            # st.altair_chart(chart)

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
        


        chart_df1 = df[["Område", "Periode", "Ledige fuldtidspersoner i pct. af befolkningen16-66 år"]]
        chart_df1["Ledige fuldtidspersoner i pct. af befolkningen16-66 år"] = pd.to_numeric(chart_df1["Ledige fuldtidspersoner i pct. af befolkningen16-66 år"], errors='coerce')

        date_parser(chart_df1, "Periode")

        chart_df1["År"] = chart_df1["Periode"].dt.year
        chart_df1["Måned"] = chart_df1["Periode"].dt.month

        chart_df1["Område_split"] = chart_df1["Område"].apply(lambda x: "Randers" if x == "Randers" else "Østjylland")
        grouped_df1 = chart_df1.groupby(['Periode', 'Område_split'])['Ledige fuldtidspersoner i pct. af befolkningen16-66 år'].mean().reset_index()

        # Pyplot chart for the same data
        fig, ax = plt.subplots(figsize=(6, 4))
        for område, group in grouped_df1.groupby("Område_split"):
            ax.plot(group['Periode'], group['Ledige fuldtidspersoner i pct. af befolkningen16-66 år'], label=område)

        ax.set_xlabel('Tid')
        ax.set_ylabel('Procent')
        ax.set_title('Sæsonkorrigeret ledighed i procent af befolkningen 16-66 år')
        ax.grid(True)
        ax.legend(title="Område", loc='center left', bbox_to_anchor=(1, 0.5))
        fig.autofmt_xdate()
        st.pyplot(fig, use_container_width=False)