import chromadb
from typing import Dict, Any, List
from chromadb.utils import embedding_functions
import os

from .mcp_base import MCPPlugin, ToolSignature

KNOWLEDGE_BASE_COLLECTION_NAME = "empresa_kb"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Ruta para la base de datos persistente de ChromaDB para la base de conocimiento.
# Debe ser la misma que en el script de ingesta.
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_data', 'knowledge_base_db'))

class KnowledgeBasePlugin(MCPPlugin):
    """
    Un plugin que proporciona herramientas para interactuar con una base de conocimiento
    vectorial dedicada, separada de la memoria conversacional.
    """

    def __init__(self):
        super().__init__()
        # Ahora usamos un cliente persistente de ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Crear la función de embedding, asegurando que es la misma que en la ingesta
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        # Pasar la función de embedding al obtener o crear la colección
        self.knowledge_base = self.chroma_client.get_or_create_collection(
            name=KNOWLEDGE_BASE_COLLECTION_NAME,
            embedding_function=embedding_function
        )
        print(f"Plugin de Base de Conocimiento conectado a la colección '{KNOWLEDGE_BASE_COLLECTION_NAME}' con el modelo de embedding correcto y persistencia en {CHROMA_DB_PATH}.")

    @property
    def name(self) -> str:
        return "knowledge_base"

    def get_tools(self) -> List[ToolSignature]:
        return [
            ToolSignature(
                name="query_knowledge_base",
                description="Busca en la base de conocimiento interna de la empresa información relevante para responder a la pregunta del usuario. Úsalo cuando el usuario pregunte sobre políticas, procedimientos, datos técnicos o cualquier información específica de la empresa.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "La pregunta o tema a buscar en la base de conocimiento."},
                        "n_results": {"type": "integer", "description": "El número de resultados relevantes a devolver.", "default": 3}
                    },
                    "required": ["query"]
                }
            )
        ]

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name == "query_knowledge_base":
            query = kwargs.get("query")
            n_results = kwargs.get("n_results", 3)

            if not query:
                return {"status": "error", "error_message": "Se requiere un 'query' para buscar en la base de conocimiento."}

            try:
                results = self.knowledge_base.query(
                    query_texts=[query],
                    n_results=n_results
                )
                # Devolvemos los documentos encontrados, que es lo que el LLM necesita.
                return {"status": "success", "result": results['documents'][0]}
            except Exception as e:
                return {"status": "error", "error_message": f"Ocurrió un error al consultar la base de conocimiento: {e}"}
        else:
            return {"status": "error", "error_message": f"La herramienta '{tool_name}' no es reconocida por el plugin {self.name}."}
