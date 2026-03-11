import psycopg2
from config import JOBINDSATS_POSTGRES_DB_HOST, JOBINDSATS_POSTGRES_DB_USER, JOBINDSATS_POSTGRES_DB_PASS, JOBINDSATS_POSTGRES_DB_DATABASE, JOBINDSATS_POSTGRES_DB_PORT


class InputsDBConnection:
    def __init__(self):
        self.host = JOBINDSATS_POSTGRES_DB_HOST
        self.port = JOBINDSATS_POSTGRES_DB_PORT
        self.database = JOBINDSATS_POSTGRES_DB_DATABASE
        self.username = JOBINDSATS_POSTGRES_DB_USER
        self.password = JOBINDSATS_POSTGRES_DB_PASS

    def execute_sql(self, sql: str, params=None):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.username,
            password=self.password,
        )
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    return cur.fetchall()
                conn.commit()
                return []
        finally:
            conn.close()


def get_inputs_db() -> InputsDBConnection:
    return InputsDBConnection()
