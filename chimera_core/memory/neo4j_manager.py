# FILE: chimera_core/memory/neo4j_manager.py (SIMPLIFICADO)

import os
from neo4j import GraphDatabase, basic_auth
from typing import List, Dict, Any
from ..utils.logger import logger

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jManager:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
            self.driver.verify_connectivity()
            logger.info("Conexión con Neo4j establecida exitosamente.")
            self._ensure_constraints()
        except Exception:
            logger.exception("Error fatal al conectar con Neo4j.")
            self.driver = None
            raise
    
    def check_connection(self):
        if not self.driver:
            raise ConnectionError("El driver de Neo4j no está inicializado.")
        self.driver.verify_connectivity()
        logger.info("Verificación de Neo4j: OK.")

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Conexión con Neo4j cerrada.")

    def _ensure_constraints(self):
        if not self.driver: 
            return
        try:
            with self.driver.session() as session:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Message) REQUIRE (m.session_id, m.turn_id) IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            logger.info("Restricciones de unicidad en Neo4j verificadas/creadas.")
        except Exception:
            logger.exception("Error al asegurar las restricciones en Neo4j.")

    def add_message_and_entities(self, session_id: str, turn_id: str, role: str, text: str, entities: List[Dict[str, str]], trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'turn_id': turn_id}}
        if not self.driver:
            logger.warning("No se pudo añadir mensaje a Neo4j: driver no disponible.", extra=log_extra)
            return
        try:
            with self.driver.session() as session:
                session.execute_write(self._create_message_and_link_entities, session_id, turn_id, role, text, entities)
        except Exception:
            logger.exception("Error al añadir mensaje y entidades a Neo4j.", extra=log_extra)

    @staticmethod
    def _create_message_and_link_entities(tx, session_id, turn_id, role, text, entities):
        tx.run(
            """
            MATCH (s:Session {session_id: $session_id})
            MERGE (m:Message {session_id: $session_id, turn_id: $turn_id})
            ON CREATE SET m.role = $role, m.text = $text, m.timestamp = datetime()
            ON MATCH SET m.role = $role, m.text = $text
            MERGE (s)-[:HAS_MESSAGE]->(m)
            """,
            session_id=session_id, turn_id=turn_id, role=role, text=text
        )
        if entities:
            tx.run(
                """
                MATCH (m:Message {session_id: $session_id, turn_id: $turn_id})
                UNWIND $entities AS ent
                MERGE (e:Entity {name: toLower(ent.text)})
                ON CREATE SET e.type = ent.label
                MERGE (m)-[:MENTIONS]->(e)
                """,
                session_id=session_id, turn_id=turn_id, entities=entities
            )

    def get_related_entities(self, entity_name: str, session_id: str, limit: int = 10, trace_id: str = 'N/A') -> List[str]:
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'entity_name': entity_name}}
        if not self.driver:
            logger.warning("No se pudieron obtener entidades relacionadas de Neo4j.", extra=log_extra)
            return []
        try:
            with self.driver.session() as session:
                query = """
                MATCH (s:Session {session_id: $session_id})-[:HAS_MESSAGE]->(m:Message)-[:MENTIONS]->(target_entity:Entity)
                WHERE toLower(target_entity.name) CONTAINS toLower($name)
                WITH m, target_entity
                MATCH (m)-[:MENTIONS]->(related_entity:Entity)
                WHERE related_entity <> target_entity
                RETURN related_entity.name AS related_entity, COUNT(related_entity) AS frequency
                ORDER BY frequency DESC
                LIMIT $limit
                """
                result = session.run(query, session_id=session_id, name=entity_name, limit=limit)
                related = [record["related_entity"] for record in result]
                logger.debug(f"Búsqueda de entidades co-mencionadas en Neo4j devolvió {len(related)} resultados.", extra=log_extra)
                return related
        except Exception:
            logger.exception("Error al obtener entidades relacionadas de Neo4j.", extra=log_extra)
            return []

    def delete_session_graph(self, session_id: str, trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id}}
        if not self.driver:
            logger.warning("No se pudo eliminar el grafo de sesión de Neo4j.", extra=log_extra)
            return
        try:
            with self.driver.session() as session:
                session.execute_write(self._delete_session_graph_tx, session_id)
            logger.info(f"Subgrafo de la sesión {session_id} eliminado de Neo4j.", extra=log_extra)
        except Exception:
            logger.exception(f"Error al eliminar el grafo de la sesión {session_id} de Neo4j.", extra=log_extra)

    @staticmethod
    def _delete_session_graph_tx(tx, session_id):
        tx.run(
            "MATCH (s:Session {session_id: $session_id}) "
            "OPTIONAL MATCH (s)-[:HAS_MESSAGE]->(m:Message) "
            "DETACH DELETE s, m",
            session_id=session_id
        )

    def create_session_in_graph(self, session_id: str, session_name: str):
        if not self.driver:
            return
        with self.driver.session() as session:
            session.run(
                "MERGE (s:Session {session_id: $session_id}) "
                "ON CREATE SET s.name = $session_name",
                session_id=session_id, session_name=session_name
            )