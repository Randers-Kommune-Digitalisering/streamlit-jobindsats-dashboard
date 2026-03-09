import os
import psycopg2


class InputsDBConnection:
    def __init__(self):
        self.host = os.getenv("INPUTS_DB_HOST", "localhost")
        self.port = int(os.getenv("INPUTS_DB_PORT", "5434"))
        self.database = os.getenv("INPUTS_DB_NAME", "inputs_db")
        self.username = os.getenv("INPUTS_DB_USER", "inputs_user")
        self.password = os.getenv("INPUTS_DB_PASS", "inputs_pass")

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
