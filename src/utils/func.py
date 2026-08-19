from utils.database_connection import get_jobindsats_db
import pandas as pd

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