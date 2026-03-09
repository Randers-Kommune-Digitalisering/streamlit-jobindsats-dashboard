from utils.database import DatabaseClient
from utils.config import JOBINDSATS_POSTGRES_DB_DATABASE, JOBINDSATS_POSTGRES_DB_HOST, JOBINDSATS_POSTGRES_DB_PASS, JOBINDSATS_POSTGRES_DB_PORT, JOBINDSATS_POSTGRES_DB_USER


def get_jobindsats_db():
    return DatabaseClient(
        db_type='postgresql',
        database=JOBINDSATS_POSTGRES_DB_DATABASE,
        username=JOBINDSATS_POSTGRES_DB_USER,
        password=JOBINDSATS_POSTGRES_DB_PASS,
        host=JOBINDSATS_POSTGRES_DB_HOST,
        port=JOBINDSATS_POSTGRES_DB_PORT
    )
