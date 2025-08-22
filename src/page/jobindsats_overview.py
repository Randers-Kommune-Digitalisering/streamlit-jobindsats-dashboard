import streamlit as st
import pandas as pd
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def show_jobindsats_metadata_overview():
    st.title("Jobindsats Metadata Overblik")
    st.markdown("Her vises seneste og kommende opdateringer for Jobindsats tabeller.")

    try:
        query = """
        SELECT "TableID", "TableName", "SubjectName", "LatestUpdate", "NextUpdate", "UpdateFrequency"
        FROM jobindsats_table_updates
        """
        with st.spinner("Indlæser metadata..."):
            result = db_client.execute_sql(query)
            columns = ["TableID", "TableName", "SubjectName", "LatestUpdate", "NextUpdate", "UpdateFrequency"]
            if result is not None:
                df = pd.DataFrame(result, columns=columns)
            else:
                st.error("Kunne ikke hente metadata fra databasen.")
                return

        with st.sidebar:
            st.markdown("### 🔎 Filtrer tabeller")
            subject_options = sorted(df["SubjectName"].dropna().unique().tolist())
            subject_filter = st.selectbox("Emne", options=["Alle"] + subject_options)
            search_query = st.text_input("Søg emne", value="", placeholder="Søg fx emne eller tabelnavn")

        filtered_df = df.copy()
        if subject_filter != "Alle":
            filtered_df = filtered_df[filtered_df["SubjectName"] == subject_filter]
        if search_query.strip():
            filtered_df = filtered_df[
                filtered_df["SubjectName"].str.contains(search_query, case=False, na=False) |
                filtered_df["TableName"].str.contains(search_query, case=False, na=False)
            ]

        st.markdown(
            f"<span style='background:#e0e0e0; border-radius:8px; padding:4px 12px; font-size:1rem; margin-left:8px;'>📋 :blue[{len(filtered_df)}] tabeller fundet</span>",
            unsafe_allow_html=True
        )

        if filtered_df.empty:
            st.warning("Ingen metadata fundet.")
            return

        for i, row in filtered_df.iterrows():
            table_id = row['TableID'] or 'Ikke angivet'
            table_name = row['TableName'] or 'Ikke angivet'
            subject_name = row['SubjectName'] or 'Ikke angivet'
            latest_update = row['LatestUpdate'] or 'Ikke angivet'
            next_update = row['NextUpdate'] or 'Ikke angivet'
            update_frequency = row['UpdateFrequency'] or 'Ikke angivet'

            title = f"**{subject_name}**: {table_name}"

            with st.expander(title):
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(90deg, #f8f4ed 80%, #e0e0e0 100%);
                        padding: 1.2rem;
                        border-radius: 12px;
                        margin-bottom: 1rem;
                        border: 1px solid #9E9E9E;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        gap: 2rem;
                    ">
                        <div style="flex:1;">
                            <p style="margin:0.2rem 0;"><strong>Datasæt:</strong> {table_id}</p>
                            <p style="margin:0.2rem 0;"><strong>Tabelnavn:</strong> {table_name}</p>
                            <p style="margin:0.2rem 0;"><strong>Emne:</strong> {subject_name}</p>
                        </div>
                        <div style="flex:0.5; text-align:center;">
                            <p style="margin:0.2rem 0;"><strong>Seneste opdatering:</strong> {latest_update}</p>
                            <p style="margin:0.2rem 0;"><strong>Næste opdatering:</strong> {next_update}</p>
                            <p style="margin:0.2rem 0;"><strong>Opdateringsfrekvens:</strong> {update_frequency}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"Fejl ved hentning af metadata: {e}")
    finally:
        db_client.close_connection()
