import sqlite3
from io import BytesIO
from threading import Lock
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import loguru

if TYPE_CHECKING:
	from loguru import Logger

from ..problem import fetch_paid_problems
class SQLiteConnectionPool:
    def __init__(self, database: str, max_connections: int = 5):
        self.database = database
        self.max_connections = max_connections
        self.connections = []
        self.lock = Lock()

    def get_connection(self):
        with self.lock:
            if self.connections:
                return self.connections.pop()
            else:
                return sqlite3.connect(self.database)

    def return_connection(self, connection: sqlite3.Connection):
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(connection)
            else:
                connection.close()

class DatabaseManager:
    _instance = None
    _lock = Lock()
    _initialized = False
    def __new__(cls, database: str, logger: "Logger"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls.logger = logger
                cls._instance.pool = SQLiteConnectionPool(database)
                cls._instance._initialize_database()
                cls._instance._initialize_meta_table()
                cls._instance._preload_paid_questions(fetch_paid_problems())
            return cls._instance

    def __init__(self, database: str, logger: "Logger"):
        with self._lock:
            if not self._initialized:
                self.pool = SQLiteConnectionPool(database)
                self._initialize_database()
                self._initialize_meta_table()
                self._preload_paid_questions(fetch_paid_problems())
                self.logger = logger
                self._initialized = True

    def _initialize_database(self):
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    question_frontend_id INTEGER,
                    language TEXT,
                    image BLOB,
                    title_slug TEXT,
                    paid_only BOOLEAN,
                    PRIMARY KEY (question_frontend_id, language)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_messages (
                    user_id TEXT,
                    message_index INTEGER,
                    role TEXT,
                    content TEXT,
                    PRIMARY KEY (user_id, message_index)
                )
            ''')
            conn.commit()

    def _initialize_meta_table(self):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meta_info (
                    table_name TEXT PRIMARY KEY,
                    last_updated TIMESTAMP
                )
            ''')
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to initialize meta table: {e}")
        finally:
            self.pool.return_connection(conn)

    def update_last_updated(self, table_name: str):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO meta_info (table_name, last_updated)
                VALUES (?, ?)
            ''', (table_name, datetime.now()))
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update last_updated for {table_name}: {e}")
        finally:
            self.pool.return_connection(conn)

    def should_update_table(self, table_name: str, hours: int = 48) -> bool:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT last_updated FROM meta_info WHERE table_name = ?
            ''', (table_name,))
            result = cursor.fetchone()
            if result is None:
                return True
            last_updated = datetime.fromisoformat(result[0])
            return datetime.now() - last_updated > timedelta(hours=hours)
        except Exception as e:
            self.logger.error(f"Failed to check last_updated for {table_name}: {e}")
            return True
        finally:
            self.pool.return_connection(conn)

    def _preload_paid_questions(self, paid_question_ids: List[int]):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # Prepare the SQL statement
            sql = '''
                INSERT OR REPLACE INTO images 
                (question_frontend_id, language, image, title_slug, paid_only)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(question_frontend_id, language) 
                DO UPDATE SET paid_only = excluded.paid_only
            '''
            
            # Prepare the data to be inserted/updated
            data = [(qid, 'en', None, '', True) for qid in paid_question_ids]
            # add cn as well
            data.extend([(qid, 'cn', None, '', True) for qid in paid_question_ids])
            # Execute the batch operation
            cursor.executemany(sql, data)
            
            conn.commit()
            self.logger.info(f"Preloaded {len(paid_question_ids)} paid questions into the database.")
        except Exception as e:
            self.logger.error(f"Failed to preload paid questions: {e}")
            conn.rollback()
        finally:
            self.pool.return_connection(conn)

    def store_image(self, question_frontend_id: int, language: str, image: BytesIO, title_slug: str, paid_only: bool):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO images (question_frontend_id, language, image, title_slug, paid_only)
                VALUES (?, ?, ?, ?, ?)
            ''', (question_frontend_id, language, image.getvalue(), title_slug, paid_only))
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store image: {e}")
        finally:
            self.pool.return_connection(conn)

    def read_image_and_slug(self, question_frontend_id: int, language: str) -> Tuple[BytesIO, str]:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image, title_slug FROM images
                WHERE question_frontend_id = ? AND language = ?
            ''', (question_frontend_id, language))
            result = cursor.fetchone()
            if result:
                return BytesIO(result[0]), result[1]
            raise ValueError(f"Image not found for question {question_frontend_id} in {language}")
        except Exception as e:
            self.logger.error(f"Failed to read image: {e}")
            raise e
        finally:
            self.pool.return_connection(conn)


    def image_exists_and_is_paid_only(self, question_frontend_id: int, language: str) -> Tuple[bool, bool]:
        """Return a tuple of two values, the first one indicates whether the image exists, the second one indicates whether the problem is paid only"""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT paid_only FROM images
                WHERE question_frontend_id = ? AND language = ?
                LIMIT 1
            ''', (question_frontend_id, language))
            result = cursor.fetchone()
            if result is not None:
                return True, bool(result[0])
            # if the image does not exist, then it's not paid only
            # bcs we have preloaded all paid only questions
            return False, False
        except Exception as e:
            self.logger.error(f"Failed to check image existence: {e}")
            return False, False
        finally:
            self.pool.return_connection(conn)

    def store_user_message(self, user_id: str, messages: List[Tuple[str, str]]):
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_messages WHERE user_id = ?', (user_id,))
            for index, (role, content) in enumerate(messages):
                cursor.execute('''
                    INSERT INTO user_messages (user_id, message_index, role, content)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, index, role, content))
            conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store user messages: {e}")
        finally:
            self.pool.return_connection(conn)

    def read_user_messages(self, user_id: str) -> Optional[List[Tuple[str, str]]]:
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM user_messages
                WHERE user_id = ?
                ORDER BY message_index
            ''', (user_id,))
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Failed to read user messages: {e}")
        finally:
            self.pool.return_connection(conn)