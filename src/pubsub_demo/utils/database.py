import sqlite3

DB_URI = "/src/db/.db"


class SqlClient:
    def __init__(self, db_uri=DB_URI):
        self.db_uri = db_uri
        self.conn = sqlite3.connect(self.db_uri)

    def execute(self, query):
        cursor = self.cursor()
        cursor.execute(query)
        self.commit()

    def fetch(self, query):
        cursor = self.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()


def init_db_tables() -> None:
    sql = SqlClient()
    sql.execute(
        """
        CREATE TABLE IF NOT EXISTS stamps
        (
            [entry_id] INTEGER PRIMARY KEY,
            [request_id] STRING NOT NULL, 
            [letter_num] INTEGER NOT NULL,
            [request_type] STRING NOT NULL,
            [stamps] STRING NOT NULL,
            [runtime_ms] FLOAT NOT NULL
        )
        """
    )


init_db_tables()  # This should go into some init script
