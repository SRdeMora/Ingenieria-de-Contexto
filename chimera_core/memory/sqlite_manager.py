import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from ..utils.logger import logger

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'chimera_memory.db')

class SQLiteManager:
    """
    Gestiona la base de datos SQLite para la memoria a medio plazo ("El Cronista").
    """

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.conn = None

    def check_connection(self):
        try:
            self._create_table()
            logger.info(f"Conexión con SQLite establecida y tablas verificadas en: {self.db_path}")
        except sqlite3.Error:
            logger.exception("Error fatal al inicializar o crear tablas en SQLite.")

    def _get_connection(self) -> sqlite3.Connection:
        """Establece y devuelve una conexión a la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error al conectar con la base de datos SQLite: {e}")
            raise

    def _create_table(self):
        """
        Crea las tablas `sessions` y `session_info` si no existen.
        """
        conn = self._get_connection()
        try:
            with conn:
                # Tabla para resúmenes (memoria a medio plazo)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        summary TEXT NOT NULL,
                        turn_count INTEGER NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Tabla para información de la sesión
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_info (
                        session_id TEXT PRIMARY KEY,
                        session_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        finally:
            conn.close()

    def update_summary(self, session_id: str, summary: str, turn_count: int, trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'turn_count': turn_count}}
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    REPLACE INTO sessions (session_id, summary, turn_count)
                    VALUES (?, ?, ?)
                """, (session_id, summary, turn_count))
            logger.debug("Resumen de sesión actualizado en SQLite.", extra=log_extra)
        except sqlite3.Error:
            logger.exception("Error al actualizar resumen en SQLite.", extra=log_extra)
        finally:
            conn.close()

    def get_summary(self, session_id: str, trace_id: str = 'N/A') -> Optional[Tuple[str, int]]:
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id}}
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT summary, turn_count FROM sessions WHERE session_id = ?", (session_id,))
            result = cursor.fetchone()
            logger.debug(f"Búsqueda de resumen en SQLite devolvió {'un resultado' if result else 'ningún resultado'}.", extra=log_extra)
            return result
        except sqlite3.Error:
            logger.exception("Error al recuperar resumen de SQLite.", extra=log_extra)
            return None
        finally:
            conn.close()

    def create_session(self, session_id: str, session_name: str, trace_id: str = 'N/A') -> bool:
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'session_name': session_name}}
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("INSERT INTO session_info (session_id, session_name) VALUES (?, ?)", (session_id, session_name))
            logger.info(f"Nueva sesión '{session_name}' creada en SQLite.", extra=log_extra)
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Intento de crear sesión con ID duplicado: {session_id}.", extra=log_extra)
            return False
        except sqlite3.Error:
            logger.exception("Error al crear sesión en SQLite.", extra=log_extra)
            return False
        finally:
            conn.close()

    def get_all_sessions(self, trace_id: str = 'N/A') -> List[Dict[str, str]]:
        log_extra = {'trace_id': trace_id}
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, session_name, created_at FROM session_info ORDER BY created_at DESC")
            rows = cursor.fetchall()
            sessions = [dict(row) for row in rows]
            logger.debug(f"Recuperadas {len(sessions)} sesiones de SQLite.", extra=log_extra)
            return sessions
        except sqlite3.Error:
            logger.exception("Error al recuperar todas las sesiones de SQLite.", extra=log_extra)
            return []
        finally:
            conn.close()

    def delete_session(self, session_id: str, trace_id: str = 'N/A') -> bool:
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id}}
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM session_info WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            logger.info(f"Datos de la sesión {session_id} eliminados de SQLite.", extra=log_extra)
            return True
        except sqlite3.Error:
            logger.exception(f"Error al eliminar la sesión {session_id} de SQLite.", extra=log_extra)
            return False
        finally:
            conn.close()