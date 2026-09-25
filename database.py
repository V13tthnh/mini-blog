import psycopg2
from psycopg2.extras import RealDictCursor
import re
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD

class PostgresCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, query: str, params=None):
        # Convert SQLite placeholders (?) to PostgreSQL (%s)
        if "?" in query:
            query = query.replace("?", "%s")
        
        # Convert SQLite 'INSERT OR IGNORE INTO' to PostgreSQL 'INSERT INTO ... ON CONFLICT DO NOTHING'
        if "INSERT OR IGNORE INTO" in query.upper():
            query = re.sub(r"INSERT OR IGNORE INTO", "INSERT INTO", query, flags=re.IGNORECASE)
            if "ON CONFLICT" not in query.upper():
                query += " ON CONFLICT DO NOTHING"

        is_insert = query.strip().upper().startswith("INSERT")

        # Special handling for post creation lastrowid in Postgres if RETURNING id is needed
        if is_insert and "RETURNING" not in query.upper():
            query += " RETURNING id"

        if params is not None:
            if isinstance(params, (list, tuple)):
                self._cursor.execute(query, params)
            else:
                self._cursor.execute(query, (params,))
        else:
            self._cursor.execute(query)

        # Capture lastrowid ONLY for INSERT queries
        if is_insert and self._cursor.description:
            col_names = [desc[0] for desc in self._cursor.description]
            if "id" in col_names:
                try:
                    row = self._cursor.fetchone()
                    if row and "id" in row:
                        self.lastrowid = row["id"]
                except Exception:
                    pass

        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass

class PostgresConnWrapper:
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor(cursor_factory=RealDictCursor))

    def execute(self, query: str, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

def get_db():
    raw_conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    return PostgresConnWrapper(raw_conn)

def init_db():
    from setup_postgres import init_postgres
    init_postgres()
