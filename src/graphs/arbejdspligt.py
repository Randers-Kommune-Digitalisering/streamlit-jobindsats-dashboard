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

def arbejdspligt():
    st.header("Arbejdspligt")
    st.subheader("Løbende udvikling")

    # Query the database for arbejdspligt data
    query = """
        SELECT
            "Periode",
            "Område",
            "Antal personer omfattet af arbejdspligt (brutto)",
            "Antal personer fritaget for beskæftigelsesrettet indsats",
            "Antal personer fritaget for beskæftigelsesrettet indsats i fø",
            "Antal personer omfattet af arbejdspligt (netto)",
            "Antal personer med beskæftigelsesrettet indsats",
            "Andel personer med beskæftigelsesrettet indsats",
            "Periode Antal og andel ydelsesmodtagere omfattet af arbejdsplig"
        FROM jobindsats_y31ap01
        WHERE "Område" IN ('Randers', 'Hele landet')
        ORDER BY "Periode" ASC;
    """

    result = db_client.execute_sql(query)

    df = pd.DataFrame(result, columns=[
        "Periode",
        "Område",
        "Antal personer omfattet af arbejdspligt (brutto)",
        "Antal personer fritaget for beskæftigelsesrettet indsats",
        "Antal personer fritaget for beskæftigelsesrettet indsats i fø",
        "Antal personer omfattet af arbejdspligt (netto)",
        "Antal personer med beskæftigelsesrettet indsats",
        "Andel personer med beskæftigelsesrettet indsats",
        "Periode (dt)"
    ])

    df["Periode (dt)"] = pd.to_datetime(df["Periode (dt)"])

    df["år"] = df["Periode (dt)"].dt.year
    df["måned"] = df["Periode (dt)"].dt.month

    st.markdown("### Randers Kommune")

    randers_df = df[df["Område"] == "Randers"].sort_values("Periode (dt)")

    brutto_series = randers_df["Antal personer omfattet af arbejdspligt (brutto)"]
    netto_series = randers_df["Antal personer omfattet af arbejdspligt (netto)"]
    antal_indsatsrettet_series = randers_df["Antal personer med beskæftigelsesrettet indsats"]
    andel_indsatsrettet_series = randers_df["Andel personer med beskæftigelsesrettet indsats"]
    periode_series = randers_df["Periode"]

    seneste_antal_brutto = int(brutto_series.iloc[-1])
    seneste_antal_netto = int(netto_series.iloc[-1])
    seneste_antal_indsatsrettet = int(antal_indsatsrettet_series.iloc[-1])
    seneste_andel_indsatsrettet = float(andel_indsatsrettet_series.iloc[-1]) 

    Seneste_periode = periode_series.iloc[-1]

    seneste_antal_brutto_delta = (
        int(brutto_series.iloc[-1] - brutto_series.iloc[-2])
        if len(brutto_series) > 1
        else None
    )
    seneste_antal_netto_delta = (
        int(netto_series.iloc[-1] - netto_series.iloc[-2])
        if len(netto_series) > 1
        else None
    )
    seneste_antal_indsatsrettet_delta = (
        int(antal_indsatsrettet_series.iloc[-1] - antal_indsatsrettet_series.iloc[-2])
        if len(antal_indsatsrettet_series) > 1
        else None
    )
    seneste_andel_indsatsrettet_delta = (
        float(andel_indsatsrettet_series.iloc[-1] - andel_indsatsrettet_series.iloc[-2])
        if len(andel_indsatsrettet_series) > 1
        else None
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            f"Antal personer omfattet af arbejdspligt (brutto) pr. {Seneste_periode}",
            seneste_antal_brutto,
            delta=seneste_antal_brutto_delta,
            border=True
        )
    with col2:
        st.metric(
            f"Antal personer omfattet af arbejdspligt (netto) pr. {Seneste_periode}",
            seneste_antal_netto,
            delta=seneste_antal_netto_delta,
            border=True
        )
    with col3:
        st.metric(
            f"Antal personer med beskæftigelsesrettet indsats pr. {Seneste_periode}",
            seneste_antal_indsatsrettet,
            delta=seneste_antal_indsatsrettet_delta,
            border=True
        )   
    with col4:
        st.metric(
            f"Andel personer med beskæftigelsesrettet indsats pr. {Seneste_periode}",
            f"{seneste_andel_indsatsrettet:.2f}%",
            delta=f"{seneste_andel_indsatsrettet_delta:.2f}%" if seneste_andel_indsatsrettet_delta is not None else None,
            border=True
        )

    st.markdown("### Hele landet")

    landet_df = df[df["Område"] == "Hele landet"].sort_values("Periode (dt)")

    brutto_series = landet_df["Antal personer omfattet af arbejdspligt (brutto)"]
    netto_series = landet_df["Antal personer omfattet af arbejdspligt (netto)"]
    antal_indsatsrettet_series = landet_df["Antal personer med beskæftigelsesrettet indsats"]
    andel_indsatsrettet_series = landet_df["Andel personer med beskæftigelsesrettet indsats"]
    periode_series = landet_df["Periode"]

    seneste_antal_brutto = int(brutto_series.iloc[-1])
    seneste_antal_netto = int(netto_series.iloc[-1])
    seneste_antal_indsatsrettet = int(antal_indsatsrettet_series.iloc[-1])
    seneste_andel_indsatsrettet = float(andel_indsatsrettet_series.iloc[-1]) 

    Seneste_periode = periode_series.iloc[-1]

    seneste_antal_brutto_delta = (
        int(brutto_series.iloc[-1] - brutto_series.iloc[-2])
        if len(brutto_series) > 1
        else None
    )
    seneste_antal_netto_delta = (
        int(netto_series.iloc[-1] - netto_series.iloc[-2])
        if len(netto_series) > 1
        else None
    )
    seneste_antal_indsatsrettet_delta = (
        int(antal_indsatsrettet_series.iloc[-1] - antal_indsatsrettet_series.iloc[-2])
        if len(antal_indsatsrettet_series) > 1
        else None
    )
    seneste_andel_indsatsrettet_delta = (
        float(andel_indsatsrettet_series.iloc[-1] - andel_indsatsrettet_series.iloc[-2])
        if len(andel_indsatsrettet_series) > 1
        else None
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            f"Antal personer omfattet af arbejdspligt (brutto) pr. {Seneste_periode}",
            seneste_antal_brutto,
            delta=seneste_antal_brutto_delta,
            border=True
        )
    with col2:
        st.metric(
            f"Antal personer omfattet af arbejdspligt (netto) pr. {Seneste_periode}",
            seneste_antal_netto,
            delta=seneste_antal_netto_delta,
            border=True
        )
    with col3:
        st.metric(
            f"Antal personer med beskæftigelsesrettet indsats pr. {Seneste_periode}",
            seneste_antal_indsatsrettet,
            delta=seneste_antal_indsatsrettet_delta,
            border=True
        )   
    with col4:
        st.metric(
            f"Andel personer med beskæftigelsesrettet indsats pr. {Seneste_periode}",
            f"{seneste_andel_indsatsrettet:.2f}%",
            delta=f"{seneste_andel_indsatsrettet_delta:.2f}%" if seneste_andel_indsatsrettet_delta is not None else None,
            border=True
        )