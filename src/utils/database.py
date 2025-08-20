import pymysql
import logging
import pymssql
import psycopg2


class DatabaseClient:
    def __init__(self, database, username, password, host, port, db_type='postgresql'):
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_type = db_type.lower()
        self.logger = logging.getLogger(__name__)

        self.connection = None
        self.cursor = None

    def get_connection(self):
        try:
            if self.connection is None or self.connection.closed:
                self.logger.info(f"Attempting to connect to {self.db_type} database: {self.database} at {self.host}:{self.port}")
                if self.db_type == 'mssql':
                    self.connection = pymssql.connect(host=self.host, user=self.username, password=self.password, database=self.database, port=self.port)
                elif self.db_type == 'mysql':
                    self.connection = pymysql.connect(host=self.host, user=self.username, password=self.password, database=self.database, port=self.port)
                elif self.db_type == 'postgresql':
                    self.connection = psycopg2.connect(host=self.host, user=self.username, password=self.password, dbname=self.database, port=self.port)
                else:
                    raise ValueError(f"Unsupported database type: {self.db_type}")
                self.logger.info(f"Connected to {self.db_type} database: {self.database} at {self.host}:{self.port}")
            return self.connection
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")
            return None

    def get_cursor(self):
        try:
            if self.cursor is None or self.cursor.closed:
                self.cursor = self.get_connection().cursor()
            return self.cursor
        except Exception as e:
            self.logger.error(f"Error getting cursor: {e}")
            return None

    def execute_sql(self, sql, params=None):
        try:
            cur = self.get_cursor()
            if cur is None:
                raise Exception("Cursor is None, cannot execute SQL")
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            if cur.description:
                return cur.fetchall()
            else:
                self.connection.commit()
                return None
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
