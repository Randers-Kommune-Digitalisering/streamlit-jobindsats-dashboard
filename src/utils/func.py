from utils.database_connection import get_jobindsats_db
import pandas as pd
import streamlit as st
from io import BytesIO

db_client = get_jobindsats_db()

def format_date_ddmmyyyy(value):
    parsed = pd.to_datetime(value, errors='coerce')
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime('%d-%m-%Y')

def LastUpdate(table_id):
    try:
        query = 'SELECT "LatestUpdate" FROM jobindsats_table_updates WHERE "TableID" = %s;'
        result = db_client.execute_sql(query, (table_id,))
        if not result:
            return "Ukendt"
        return format_date_ddmmyyyy(result[0][0])
    except Exception:
        return "Ukendt"

def NextUpdate(table_id):
    query = 'SELECT "NextUpdate" FROM jobindsats_table_updates WHERE "TableID" = %s;'
    result = db_client.execute_sql(query, (table_id,))
    if not result:
        return "Ukendt"
    return format_date_ddmmyyyy(result[0][0])



def ComparisonGroupDropdown(label,options, key, default=0, visible=True):
    selected = st.selectbox(
        label,
        options.keys(),
        key=key,
        index=default,
        label_visibility="visible" if visible else "collapsed"

    )
    return options[selected], selected  # Return the selected value and its label



def render_vector_downloads(fig, filename_prefix):
    svg_buffer = BytesIO()
    fig.savefig(svg_buffer, format='svg', bbox_inches='tight')

    spacer, col1 = st.columns([4, 1])
    with col1:
        st.download_button(
            label='',
            data=svg_buffer.getvalue(),
            file_name=f'{filename_prefix}.svg',
            mime='image/svg+xml',
            icon=':material/download:',
            use_container_width=True
        )
    

def render_vector_downloads_nocol(fig, filename_prefix):
    svg_buffer = BytesIO()
    fig.savefig(svg_buffer, format='svg', bbox_inches='tight')

    st.download_button(
        label='',
        data=svg_buffer.getvalue(),
        file_name=f'{filename_prefix}.svg',
        mime='image/svg+xml',
        icon=':material/download:',
        use_container_width=False
    )
    