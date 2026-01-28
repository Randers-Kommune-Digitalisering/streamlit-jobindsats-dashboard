import streamlit as st
from utils.database_connection import get_jobindsats_db

db_client = get_jobindsats_db()


def show_job_og_lontimer_graph():
    st.write("This is job og løntimer!")
    try:
        if 'y30r21' not in st.session_state:
            with st.spinner("Indlæser jobindstats_y30r21 data..."):
                query = (
                    'SELECT "Område", "Periode", "Ydelsesgrupper", '

                    'FROM jobindsats_y30r21'
                )

                columns = [
                    "Område",
                    "Periode",
                    "Ydelsesgrupper",
                    "Antal løntimer",
                    "Antal løntimer i pct. af arbejdsstyrken 16-66 år",
                    "Antal løntimer i pct. af befolkningen 16-66 år"
                ]
                result = db_client.execute_sql(query)
                if result is not None:
                    df = pd.DataFrame(result, columns=columns)
                    st.session:state.y30r21 = df
                else:
                    st.error("Kunne ikke hente data fra databasen.")
                    return

    except Exception as e:
        st.error(f"Der opstod en fejl: {e}")
