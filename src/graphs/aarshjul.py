import streamlit as st
import pandas as pd
import datetime as dt
from utils.database_connection import get_jobindsats_db
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import math
from io import BytesIO

db_client = get_jobindsats_db()

MONTHS_DA = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'Maj',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Okt',
    11: 'Nov',
    12: 'Dec',
}
TITLE_X_WITH_RIGHT_LEGEND = 0.62

def percent_comma(x, pos):
    return f"{x:,.2f}%".replace('.', ',')

def month_year_da(x, pos):
    dt = mdates.num2date(x)
    return f"{MONTHS_DA.get(dt.month, '')} {dt.year}"

def format_date_ddmmyyyy(value):
    parsed = pd.to_datetime(value, errors='coerce')
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime('%d-%m-%Y')

def LastUpdate(table_id):
    query = 'SELECT "LatestUpdate" FROM jobindsats_table_updates WHERE "TableID" = %s;'
    result = db_client.execute_sql(query, (table_id,))
    if not result:
        return "Ukendt"
    return format_date_ddmmyyyy(result[0][0])

def NextUpdate(table_id):
    query = 'SELECT "NextUpdate" FROM jobindsats_table_updates WHERE "TableID" = %s;'
    result = db_client.execute_sql(query, (table_id,))
    if not result:
        return "Ukendt"
    return format_date_ddmmyyyy(result[0][0])

def render_vector_downloads(fig, filename_prefix):
    svg_buffer = BytesIO()
    fig.savefig(svg_buffer, format='svg', bbox_inches='tight')

    spacer, col1 = st.columns([4, 1])
    with col1:
        st.download_button(
            label='Download SVG',
            data=svg_buffer.getvalue(),
            file_name=f'{filename_prefix}.svg',
            mime='image/svg+xml',
            icon=':material/download:',
            use_container_width=True
        )

def aarshjul():
    try:
        st.header("Ressourcer til årshjulsdokumenter")
        st.subheader("Budgetopfølgninger")
        today = pd.to_datetime("today")

        # Helårspersoner - A-dagpenge
        query = (
            'SELECT "Periode", "Område", "Periode A-Dagpenge", "Antal fuldtidspersoner" FROM jobindsats_y01a02 where "Område" IN (\'Randers\', \'Hele landet\') order by "Periode" asc;'
        ) 

        result = db_client.execute_sql(query)

        df = pd.DataFrame(result, columns=["Periode", "Område", "Periode A-Dagpenge", "Antal fuldtidspersoner"])

        df["år"] = df["Periode A-Dagpenge"].dt.year
        df["måned"] = df["Periode A-Dagpenge"].dt.month

        df1 = df[(df["Område"] == "Randers") & (df["år"] >= today.year - 2)]
        

        with st.container(border=1):    
            st.subheader("A-dagpenge")
            col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")
            with col1:
                st.markdown(f"""
                    #### Noter
                    Udvikling i antal helårspersoner seneste tre år. Budgetpersoner for indeværende år er markeret med stiplet linje.

                    #### Kilde
                    Jobindsats.dk

                        y01a02
                        - Sidst opdateret:  {LastUpdate('y01a02')}
                        - Næste opdatering: {NextUpdate('y01a02')}
                            
                """)
                

            with col2:
                fig, ax = plt.subplots(figsize=(8, 4))

                colors = {
                    str(today.year): '#00B050',
                    str(today.year - 1): '#FFC000',
                    str(today.year - 2): '#FF0000',
                }
                budgetpersoner = 1283
                måneder = MONTHS_DA
                budget_x = list(måneder.keys())
                budget_y = [budgetpersoner] * len(budget_x)
                ax.plot(budget_x, budget_y, color='#C0C0C0', linestyle='--', linewidth=2, label=f'Budgetpersoner {today.year}')
                for år, group in df1.groupby("år"):
                    ax.plot(group["måned"], group["Antal fuldtidspersoner"], label=år, linewidth=2, color=colors.get(str(år), 'black'))
                
                ax.set_xticks(list(måneder.keys()))
                ax.set_xticklabels(list(måneder.values()))
                ax.set_ylabel('Helårspersoner')
                ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{int(x):,}".replace(",", ".")))
                ax.set_title('A-dagpengemodtagere - seneste tre år', x=TITLE_X_WITH_RIGHT_LEGEND)
                ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                handles, labels = ax.get_legend_handles_labels()
                sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: 0 if x[1] == "Randers" else 1)
                handles, labels = zip(*sorted_handles_labels)
                labels = [f"Helårspersoner {label}" if str(label).isdigit() else label for label in labels]
                # set legend to the right of the plot   
                ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1.02, 0.5), ncol=1, frameon=False)
                fig.autofmt_xdate()
                st.pyplot(fig, use_container_width=False)
                render_vector_downloads(fig, f"a-dagpenge-{today.year}")

        # Ledighedsandel

        # Helårspersoner - A-dagpenge
        query = (
            'SELECT "Periode", "Område", "Periode Ledighed: Faktiske antal ledige og fuldtidspersoner", "Antal ledige fuldtidspersoner" FROM jobindsats_y25i01 where "Område" IN (\'Randers\', \'Hele landet\') order by "Periode" asc;'
        ) 

        result = db_client.execute_sql(query)

        df = pd.DataFrame(result, columns=["Periode", "Område", "Periode Ledighed: Faktiske antal ledige og fuldtidspersoner", "Antal ledige fuldtidspersoner"])
        
        df["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"] = pd.to_datetime(df["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"], errors='coerce')

        df["år"] = df["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"].dt.year
        df["måned"] = df["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"].dt.month

        df2 = df[df["år"] >= today.year - 1]

        # Unstack data to have separate columns for Randers and Hele landet
        df2 = df2.pivot(index="Periode Ledighed: Faktiske antal ledige og fuldtidspersoner", columns="Område", values="Antal ledige fuldtidspersoner")

        df2["Ledighedsandel"] = df2["Randers"] / df2["Hele landet"] * 100
        df2 = df2.reset_index()

        with st.container(border=1):
            st.subheader("Ledighedsandel")
            col1, col2 = st.columns([2, 5], vertical_alignment="top", gap="large")       

            with col1:
                st.markdown(f"""
                    #### Noter
                    Ledighedsandel i Randers i forhold til hele landet seneste to år.

                    #### Kilde
                    Jobindsats.dk

                        y25i01
                        - Sidst opdateret:  {LastUpdate('y25i01')}
                        - Næste opdatering: {NextUpdate('y25i01')}
                            
                    #### Befolkningsandel
                """)

                befolkningsandel = st.number_input("Indtast befolkningsandel i %", min_value=1.0, max_value=2.0, value=1.67, step=0.01, key="befolkningsandel")

            with col2:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(
                    df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"],
                    df2["Ledighedsandel"],
                    marker='o',
                    color='#00B050',
                    linewidth=2,
                    label='Ledighedsandel',
                )
                for x, y in zip(
                    df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"],
                    df2["Ledighedsandel"],
                ):
                    ax.annotate(
                        percent_comma(y, None),
                        (x, y),
                        textcoords='offset points',
                        xytext=(0, 10),
                        ha='center',
                        fontsize=8,
                        color='#000000',
                    )
                ax.plot(
                    df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"],
                    [befolkningsandel] * len(df2),
                    color='#C0C0C0',
                    linestyle='--',
                    linewidth=2,
                    label='Befolkningsandel',
                )
                if not df2.empty:
                    sidste_x = df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"].iloc[-1]
                    ax.annotate(
                        percent_comma(befolkningsandel, None),
                        (sidste_x, befolkningsandel),
                        textcoords='offset points',
                        xytext=(0, 10),
                        ha='center',
                        fontsize=8,
                        color='#000000',
                    )
                ax.set_ylabel('Ledighedsandel (%)')
                ax.set_title(
                    f'Ledighedsandel i Randers Kommune {df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"].dt.year.min()}-{df2["Periode Ledighed: Faktiske antal ledige og fuldtidspersoner"].dt.year.max()}',
                    x=TITLE_X_WITH_RIGHT_LEGEND,
                )
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                ax.xaxis.set_major_formatter(FuncFormatter(month_year_da))
                ax.grid(axis='y', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                min_val = min(df2["Ledighedsandel"].min(), befolkningsandel)
                max_val = max(df2["Ledighedsandel"].max(), befolkningsandel)
                y_min = math.floor(min_val * 100) / 100 - 0.03  
                y_max = math.ceil(max_val * 100) / 100 + 0.03
                if y_min == y_max:
                    y_max = y_min + 0.01
                ax.set_ylim(y_min, y_max)
                ax.yaxis.set_major_locator(MultipleLocator(0.02))
                ax.yaxis.set_major_formatter(FuncFormatter(percent_comma))
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                handles, labels = ax.get_legend_handles_labels()
                # set legend to the right of the plot   
                ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1.02, 0.5), ncol=1, frameon=False)
                fig.autofmt_xdate()
                st.pyplot(fig, use_container_width=False)  
        
                render_vector_downloads(fig, f"ledighedsandel-{today.year}")
    except Exception as e:
        st.exception(e)
        return
    finally:
        db_client.close_connection()
                