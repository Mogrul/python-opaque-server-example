import logging
import sqlite3
import threading
from pathlib import Path

from opaque_server.metaclass import Singleton

DATABASE_FILE_PATH = Path("data/database.db")

class Database(metaclass=Singleton):
    def __init__(self):
        self._logger = logging.getLogger("database")
        self._connection = sqlite3.connect(DATABASE_FILE_PATH, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.Lock()

        self._add_tables()

    def _add_tables(self) -> None:
        script = """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password BLOB NOT NULL
            )
        """

        self._connection.executescript(script)

    def register_user(self, username: str, password_file: bytes) -> None:
        query = """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            ON CONFLICT (username) DO NOTHING
        """

        with self._lock:
            self._connection.execute(query, (username, password_file))
            self._connection.commit()

        self._logger.info(f"Registered user: {username}")

    def get_user_password(self, username: str) -> bytes | None:
        query = """
            SELECT password FROM users WHERE username = ? LIMIT 1
        """

        with self._lock:
            row = self._connection.execute(query, (username,)).fetchone()

            if not row:
                return None

            return row["password"]