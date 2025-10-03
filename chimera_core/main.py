
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks 
from pydantic import BaseModel, RootModel
import uvicorn
import uuid
from typing import List, Dict

# Importamos el cerebro del sistema
from .orchestrator import Orchestrator, LLMSettings

# --- Modelos de Datos (Pydantic) ---
# Definen la estructura de los datos para las peticiones y respuestas de la API.
# Esto asegura la validación, serialización y documentación automática.

class ProviderModels(RootModel):
    root: Dict[str, List[str]]



class UserRequest(BaseModel):
    """Modelo para la petición del usuario."""
    session_id: str
    prompt: str
    llm_settings: LLMSettings # Añadido para incluir la configuración del LLM

class ChimeraResponse(BaseModel):
    """Modelo para la respuesta de Quimera."""
    session_id: str
    response_text: str

class NewSessionRequest(BaseModel):
    """Modelo para la petición de creación de una nueva sesión."""
    session_name: str

class SessionInfo(BaseModel):
    session_id: str
    session_name: str
    created_at: str

class ResetMemoryRequest(BaseModel):
    """Modelo para la petición de reseteo de una memoria."""
    memory_type: str


# --- Inicialización de la Aplicación FastAPI ---
app = FastAPI(
    title="Chimera Core API",
    description="El Córtex del Proyecto Quimera. Gestiona la lógica, memoria y proveedores de LLM.",
    version="1.0.0"
)

# --- Instancia Global del Orquestador ---
# Creamos una única instancia del orquestador que será utilizada por todas las peticiones.
# Esto es eficiente ya que el orquestador y sus componentes (motores, gestores)
# se inicializan solo una vez cuando arranca el servidor.
orchestrator = Orchestrator()

@app.on_event("startup")
async def startup_event():
    orchestrator.context_engine.check_all_connections()


# --- Endpoints de la API ---

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint raíz que devuelve un saludo. Útil para una comprobación básica.
    """
    return {"message": "Chimera Core está activo."}

@app.get("/health", tags=["Status"])
async def health_check():
    """
    Endpoint de estado de salud. Devuelve el estado del servidor.
    Ideal para sistemas de monitorización o para verificar que el servicio está online.
    """
    return {"status": "ok"}

@app.post("/v1/memory/reset", tags=["Memory"])
async def reset_memory(request: ResetMemoryRequest):
    """
    Endpoint para resetear una de las memorias del sistema.
    Actualmente solo soporta 'chroma'.
    """
    if request.memory_type == "chroma":
        success = orchestrator.context_engine.chroma_manager.reset_database()
        if success:
            return {"message": "La base de datos de ChromaDB ha sido reseteada exitosamente."}
        else:
            raise HTTPException(status_code=500, detail="Ocurrió un error al resetear ChromaDB.")
    else:
        raise HTTPException(status_code=400, detail=f"Tipo de memoria '{request.memory_type}' no soportado para reseteo.")


@app.get("/v1/sessions", response_model=List[SessionInfo], tags=["Sessions"])
async def get_sessions():
    """
    Endpoint para obtener la lista de todas las sesiones de conversación.
    """
    sessions = orchestrator.context_engine.sqlite_manager.get_all_sessions()
    return sessions

@app.post("/v1/sessions", response_model=SessionInfo, tags=["Sessions"])
async def create_session(request: NewSessionRequest):
    """
    Endpoint para crear una nueva sesión de conversación.
    Esto crea una entrada en SQLite y un nodo :Session en Neo4j.
    """
    session_id = str(uuid.uuid4())
    session_name = request.session_name
    
    # Crear en SQLite
    sqlite_success = orchestrator.context_engine.sqlite_manager.create_session(session_id, session_name)
    if not sqlite_success:
        raise HTTPException(status_code=500, detail="No se pudo crear la sesión en SQLite.")

    # Crear en Neo4j
    if orchestrator.context_engine.neo4j_manager:
        try:
            orchestrator.context_engine.neo4j_manager.create_session_in_graph(session_id, session_name)
        except Exception as e:
            # Si Neo4j falla, podríamos querer revertir la creación en SQLite (rollback)
            # Por ahora, simplemente lanzamos un error.
            raise HTTPException(status_code=500, detail=f"No se pudo crear la sesión en Neo4j: {e}")
    
    # Devolvemos la información de la sesión recién creada
    new_session_info = {
        "session_id": session_id,
        "session_name": session_name,
        "created_at": "now" # Simplificación, la BD tiene el timestamp real
    }
    return new_session_info

@app.delete("/v1/sessions/{session_id}", status_code=204, tags=["Sessions"])
async def delete_session(session_id: str):
    """
    Endpoint para eliminar una sesión y todos sus datos asociados.
    """
    success = orchestrator.delete_session_data(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Ocurrió un error al eliminar los datos de la sesión.")

@app.get("/v1/providers", response_model=ProviderModels, tags=["Providers"])
async def get_providers():
    """
    Endpoint para obtener la lista de proveedores de LLM disponibles y sus modelos.
    """
    providers_data = {}
    for provider_name in orchestrator.api_manager.get_available_providers():
        providers_data[provider_name] = orchestrator.api_manager.get_provider_models(provider_name)
    return providers_data

@app.post("/v1/settings", tags=["Settings"])
async def update_settings(settings: LLMSettings):
    """
    Endpoint para actualizar la configuración del LLM en el backend.
    """
    orchestrator.update_llm_settings(
        settings.provider_name,
        settings.model_name,
        settings.temperature,
        settings.max_output_tokens
    )
    return {"message": "Configuración de LLM actualizada.", "current_settings": orchestrator.get_current_llm_settings()}

@app.get("/v1/settings", response_model=LLMSettings, tags=["Settings"])
async def get_settings():
    """
    Endpoint para obtener la configuración actual del LLM desde el backend.
    """
    return orchestrator.get_current_llm_settings()
    # No se devuelve contenido en una respuesta 204 No Content

@app.post("/v1/chat", response_model=ChimeraResponse, tags=["Conversation"])
async def handle_chat(request: UserRequest, background_tasks: BackgroundTasks):
    """
    Endpoint principal para gestionar las conversaciones.
    
    Actualmente es un placeholder. En futuras implementaciones, este endpoint
    llamará al Orquestador para procesar la petición completa.
    """
    # Llama al orquestador para procesar la solicitud
    result = orchestrator.handle_user_request(request.session_id, request.prompt, request.llm_settings, background_tasks)

    # Construye la respuesta final
    if "error" in result:
        # En un caso real, podríamos querer diferentes códigos de estado HTTP
        response_text = result["error"]
    else:
        response_text = result["response"]
        
    response = ChimeraResponse(
        session_id=request.session_id,
        response_text=response_text
    )
    
    return response

# --- Punto de Entrada para Ejecución Directa ---
# Esto permite ejecutar el servidor directamente con `python main.py`
# `uvicorn.run` es la forma programática de iniciar el servidor ASGI.
if __name__ == "__main__":
    print("Iniciando servidor FastAPI con Uvicorn...")
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,  # El servidor se reinicia automáticamente con los cambios en el código
        log_level="info"
    )
