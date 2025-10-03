
import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any
from ..utils.logger import logger

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_data')

class ChromaManager:
    def __init__(self, path: str = CHROMA_PATH, collection_name: str = "chimera_semantic_memory"):
        self.path = path
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    def check_connection(self):
        try:
            self.client = chromadb.PersistentClient(path=self.path)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cliente de ChromaDB inicializado. Colección '{self.collection_name}' lista en '{self.path}'.")
        except Exception:
            logger.exception("Error fatal al inicializar ChromaDB. La memoria semántica no estará disponible.")

    def add_entry(self, session_id: str, text_content: str, turn_id: str, metadata: Dict[str, Any], trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id, 'turn_id': turn_id}}
        if not self.collection:
            logger.warning("No se pudo añadir entrada a ChromaDB: colección no disponible.", extra=log_extra)
            return

        metadata['session_id'] = session_id
        try:
            self.collection.add(documents=[text_content], metadatas=[metadata], ids=[turn_id])
            logger.debug("Entrada añadida a la memoria semántica (ChromaDB).", extra=log_extra)
        except Exception:
            logger.exception(f"Error al añadir entrada a ChromaDB (ID: {turn_id}).", extra=log_extra)

    def search_similar(self, query_text: str, n_results: int = 5, filter_by_session: str = None, trace_id: str = 'N/A') -> List[Dict[str, Any]]:
        log_extra = {'trace_id': trace_id, 'data': {'n_results': n_results, 'filter_session': filter_by_session}}
        if not self.collection:
            logger.warning("No se pudo buscar en ChromaDB: colección no disponible.", extra=log_extra)
            return []

        try:
            # CORRECCIÓN: Construir los argumentos de la consulta dinámicamente para evitar
            # pasar un filtro `where` vacío, lo que causa un ValueError.
            query_args = {
                'query_texts': [query_text],
                'n_results': n_results
            }
            if filter_by_session:
                query_args['where'] = {"session_id": filter_by_session}

            results = self.collection.query(**query_args)
            
            logger.debug(f"Búsqueda en ChromaDB devolvió {len(results.get('documents', [[]])[0])} resultados.", extra=log_extra)
            return results
        except Exception:
            logger.exception(f"Error al buscar en ChromaDB.", extra=log_extra)
            return []

    def delete_session_entries(self, session_id: str, trace_id: str = 'N/A'):
        log_extra = {'trace_id': trace_id, 'data': {'session_id': session_id}}
        if not self.collection:
            logger.warning("No se pudieron eliminar entradas de ChromaDB: colección no disponible.", extra=log_extra)
            return
        try:
            self.collection.delete(where={"session_id": session_id})
            logger.info(f"Entradas de la sesión {session_id} eliminadas de ChromaDB.", extra=log_extra)
        except Exception:
            logger.exception(f"Error al eliminar entradas de ChromaDB para la sesión {session_id}.", extra=log_extra)

    def reset_database(self, trace_id: str = 'N/A') -> bool:
        """Elimina y recrea la colección de ChromaDB, borrando todos los datos."""
        log_extra = {'trace_id': trace_id}
        if not self.client:
            logger.error("No se puede resetear la base de datos de ChromaDB: cliente no disponible.", extra=log_extra)
            return False
        try:
            logger.warning(f"Iniciando reseteo de la base de datos ChromaDB (colección: {self.collection_name})...", extra=log_extra)
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("La base de datos de ChromaDB ha sido reseteada exitosamente.", extra=log_extra)
            return True
        except Exception:
            logger.exception("Error fatal durante el reseteo de la base de datos de ChromaDB.", extra=log_extra)
            return False

# Ejemplo de uso (para pruebas directas del módulo)
if __name__ == '__main__':
    print(f"Usando ChromaDB en: {CHROMA_PATH}")
    manager = ChromaManager()

    if manager.collection:
        test_session_id = "session_chroma_12345"
        print(f"\n--- Probando la sesión: {test_session_id} ---")

        # Añadir entradas
        print("\nAñadiendo entradas a la memoria semántica...")
        manager.add_entry(test_session_id, "El usuario está preocupado por la seguridad de los datos.", "turn_1", {"role": "user", "timestamp": "2025-07-30T10:00:00Z"})
        manager.add_entry(test_session_id, "Hemos implementado encriptación de extremo a extremo.", "turn_2", {"role": "assistant", "timestamp": "2025-07-30T10:01:00Z"})
        manager.add_entry(test_session_id, "¿Qué tipo de algoritmos de cifrado se utilizan?", "turn_3", {"role": "user", "timestamp": "2025-07-30T10:02:00Z"})
        manager.add_entry(test_session_id, "Mi comida favorita es la pizza de pepperoni.", "turn_4", {"role": "user", "timestamp": "2025-07-30T10:03:00Z"})

        # Realizar una búsqueda semántica
        query = "¿Cómo se protege la información del usuario?"
        print(f"\nBuscando recuerdos similares a: '{query}'")
        search_results = manager.search_similar(query, test_session_id, n_results=2)

        if search_results and search_results['documents']:
            # search_results es un diccionario con claves: ids, documents, metadatas, distances
            # Accedemos a la primera (y única) lista de resultados
            docs = search_results['documents'][0]
            dists = search_results['distances'][0]

            print("Resultados encontrados:")
            for i, doc in enumerate(docs):
                print(f"  - Documento: '{doc}' (Distancia: {dists[i]:.4f})")
        else:
            print("No se encontraron resultados.")
