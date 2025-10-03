
import redis
import json
from typing import List, Dict, Any
from ..utils.logger import logger

class RedisManager:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        except redis.exceptions.ConnectionError as e:
            logger.exception("Error fatal al conectar con Redis. La memoria a corto plazo no estará disponible.")
            self.client = None

    def check_connection(self):
        """Verifica que la conexión con Redis está activa."""
        if not self.client:
            raise ConnectionError("El cliente de Redis no está inicializado.")
        self.client.ping()
        logger.info("Verificación de Redis: OK.")
        
    def _get_session_key(self, session_id: str) -> str:
        return f"session:{session_id}:short_term_memory"

    def add_turn(self, session_id: str, turn_data: Dict[str, Any], trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'turn_role': turn_data.get('role')}}
        if not self.client:
            logger.warning("No se pudo añadir turno a Redis: cliente no disponible.", extra=log_extra)
            return
        
        session_key = self._get_session_key(session_id)
        try:
            self.client.rpush(session_key, json.dumps(turn_data))
            logger.debug("Turno añadido a la memoria a corto plazo (Redis).", extra=log_extra)
        except redis.exceptions.RedisError:
            logger.exception(f"Error de Redis al añadir turno para la sesión {session_id}.", extra=log_extra)

    def get_recent_turns(self, session_id: str, num_turns: int = 20, trace_id: str = 'N/A') -> List[Dict[str, Any]]:
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'num_turns': num_turns}}
        if not self.client:
            logger.warning("No se pudieron recuperar turnos de Redis: cliente no disponible.", extra=log_extra)
            return []
        
        session_key = self._get_session_key(session_id)
        try:
            raw_turns = self.client.lrange(session_key, -num_turns, -1)
            deserialized_turns = [json.loads(turn) for turn in raw_turns]
            logger.debug(f"Recuperados {len(deserialized_turns)} turnos de Redis.", extra=log_extra)
            return deserialized_turns
        except redis.exceptions.RedisError:
            logger.exception(f"Error de Redis al recuperar turnos para la sesión {session_id}.", extra=log_extra)
            return []

    def delete_session_history(self, session_id: str, trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id}}
        if not self.client:
            logger.warning("No se pudo eliminar historial de Redis: cliente no disponible.", extra=log_extra)
            return
        
        session_key = self._get_session_key(session_id)
        try:
            self.client.delete(session_key)
            logger.info(f"Historial de la sesión {session_id} eliminado de Redis.", extra=log_extra)
        except redis.exceptions.RedisError:
            logger.exception(f"Error de Redis al eliminar el historial de la sesión {session_id}.", extra=log_extra)

    def trim_history(self, session_id: str, max_len: int, trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'max_len': max_len}}
        if not self.client:
            logger.warning("No se pudo podar el historial de Redis: cliente no disponible.", extra=log_extra)
            return
        
        session_key = self._get_session_key(session_id)
        try:
            self.client.ltrim(session_key, -max_len, -1)
            logger.debug(f"Historial de la sesión {session_id} podado para conservar los últimos {max_len} turnos.", extra=log_extra)
        except redis.exceptions.RedisError:
            logger.exception(f"Error de Redis al podar el historial de la sesión {session_id}.", extra=log_extra)

# Ejemplo de uso (para pruebas directas del módulo)
if __name__ == '__main__':
    manager = RedisManager()

    if manager.client:
        test_session_id = "session_redis_12345"
        print(f"\n--- Probando la sesión: {test_session_id} ---")

        # Limpiar datos de pruebas anteriores
        manager.client.delete(manager._get_session_key(test_session_id))

        # Añadir turnos
        print("\nAñadiendo 5 turnos a la conversación...")
        manager.add_turn(test_session_id, {"role": "user", "content": "Hola Quimera"})
        manager.add_turn(test_session_id, {"role": "assistant", "content": "Hola Arkitekto. ¿En qué puedo ayudarte hoy?"})
        manager.add_turn(test_session_id, {"role": "user", "content": "Háblame de tu arquitectura de memoria."})
        manager.add_turn(test_session_id, {"role": "assistant", "content": "Mi memoria es jerárquica y se divide en cuatro capas..."})
        manager.add_turn(test_session_id, {"role": "user", "content": "Interesante, ¿puedes detallar la memoria a corto plazo?"})

        # Recuperar turnos
        print("\nRecuperando los últimos 3 turnos:")
        recent_turns = manager.get_recent_turns(test_session_id, num_turns=3)
        for i, turn in enumerate(recent_turns):
            print(f"  Turno {i+1}: {turn}")

        # Podar historial
        print("\nPodando el historial para conservar solo los 2 últimos turnos...")
        manager.trim_history(test_session_id, max_len=2)

        # Verificar el podado
        print("\nRecuperando todos los turnos después del podado (deberían ser 2):")
        all_turns_after_trim = manager.get_recent_turns(test_session_id, num_turns=100)
        print(f"Número de turnos encontrados: {len(all_turns_after_trim)}")
        for i, turn in enumerate(all_turns_after_trim):
            print(f"  Turno {i+1}: {turn}")
