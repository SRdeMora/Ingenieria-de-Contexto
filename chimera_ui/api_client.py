
import requests
from PySide6.QtCore import QObject, Signal, QThread
from typing import Dict, Any

# --- Configuración del Cliente ---
# La URL base del servidor FastAPI. En una aplicación real, esto podría
# ser configurable.
API_BASE_URL = "http://127.0.0.1:8000"

class ApiWorker(QObject):
    """
    El "trabajador" que se ejecuta en un hilo separado (QThread).
    
    Hereda de QObject para poder definir y emitir señales. Su única función
    es realizar la llamada de red bloqueante sin congelar la GUI.
    """
    # --- Señales ---
    # La señal `response_received` llevará un diccionario con la respuesta.
    # La señal `error_occurred` llevará un string con el mensaje de error.
    # La señal `finished` se emite cuando el trabajador ha completado su tarea.
    response_received = Signal(dict)
    sessions_received = Signal(list) # Nueva señal para la lista de sesiones
    session_created = Signal(dict)   # Nueva señal para la sesión creada
    session_deleted = Signal(str)    # Nueva señal para confirmar el borrado de una sesión
    providers_received = Signal(dict) # Nueva señal para la lista de proveedores y sus modelos
    settings_received = Signal(dict) # Nueva señal para la configuración de LLM recibida
    settings_updated = Signal(dict)  # Nueva señal para la configuración de LLM actualizada
    chroma_reset_completed = Signal(dict) # Nueva señal para el reseteo de ChromaDB
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, request_type: str, payload: Dict = None):
        super().__init__()
        self.request_type = request_type
        self.payload = payload if payload is not None else {}

    def run(self):
        """
        El método principal que se ejecuta en el hilo de trabajo.
        Realiza la petición HTTP al backend según el tipo de petición.
        """
        try:
            if self.request_type == "get_sessions":
                response = requests.get(f"{API_BASE_URL}/v1/sessions", timeout=10)
                response.raise_for_status()
                self.sessions_received.emit(response.json())

            elif self.request_type == "create_session":
                response = requests.post(f"{API_BASE_URL}/v1/sessions", json=self.payload, timeout=10)
                response.raise_for_status()
                self.session_created.emit(response.json())

            elif self.request_type == "send_prompt":
                response = requests.post(f"{API_BASE_URL}/v1/chat", json=self.payload, timeout=120)
                response.raise_for_status()
                self.response_received.emit(response.json())

            elif self.request_type == "delete_session":
                session_id = self.payload.get('session_id')
                response = requests.delete(f"{API_BASE_URL}/v1/sessions/{session_id}", timeout=30)
                response.raise_for_status()
                self.session_deleted.emit(session_id) # Emitimos el ID de la sesión borrada

            elif self.request_type == "get_providers":
                response = requests.get(f"{API_BASE_URL}/v1/providers", timeout=10)
                response.raise_for_status()
                self.providers_received.emit(response.json())

            elif self.request_type == "get_settings":
                response = requests.get(f"{API_BASE_URL}/v1/settings", timeout=10)
                response.raise_for_status()
                self.settings_received.emit(response.json())

            elif self.request_type == "update_settings":
                response = requests.post(f"{API_BASE_URL}/v1/settings", json=self.payload, timeout=10)
                response.raise_for_status()
                self.settings_updated.emit(response.json().get("current_settings", {}))

            elif self.request_type == "reset_chroma_db":
                response = requests.post(f"{API_BASE_URL}/v1/memory/reset", json=self.payload, timeout=30)
                response.raise_for_status()
                self.chroma_reset_completed.emit(response.json())

        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Error de conexión: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Error inesperado: {e}")
        finally:
            self.finished.emit()

class ApiClient(QObject):
    """
    Fachada para la comunicación con el backend de Chimera Core.

    Encapsula la complejidad de la ejecución en hilos. La interfaz de usuario
    solo necesita interactuar con esta clase, simplificando el código de la GUI.
    Hereda de QObject para poder ser el padre de los hilos y trabajadores.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self.worker = None

    def send_prompt(self, session_id: str, prompt: str, llm_settings: Dict[str, Any], on_success, on_error):
        """Envía un prompt al backend de forma asíncrona."""
        payload = {"session_id": session_id, "prompt": prompt, "llm_settings": llm_settings}
        self._start_worker("send_prompt", payload, on_success, on_error)

    def get_sessions(self, on_success, on_error):
        """Obtiene todas las sesiones del backend."""
        self._start_worker("get_sessions", {}, on_success, on_error)

    def create_session(self, session_name: str, on_success, on_error):
        """Crea una nueva sesión en el backend."""
        payload = {"session_name": session_name}
        self._start_worker("create_session", payload, on_success, on_error)

    def delete_session(self, session_id: str, on_success, on_error):
        """Elimina una sesión en el backend."""
        payload = {"session_id": session_id}
        self._start_worker("delete_session", payload, on_success, on_error)

    def get_providers(self, on_success, on_error):
        """Obtiene la lista de proveedores y sus modelos del backend."""
        self._start_worker("get_providers", {}, on_success, on_error)

    def get_settings(self, on_success, on_error):
        """
        Obtiene la configuración actual del LLM desde el backend.
        """
        self._start_worker("get_settings", {}, on_success, on_error, settings_signal=self.worker.settings_received)

    def update_settings(self, settings_data: Dict[str, Any], on_success, on_error):
        """
        Envía la nueva configuración del LLM al backend para que sea persistente.
        """
        self._start_worker("update_settings", settings_data, on_success, on_error, settings_updated_signal=self.worker.settings_updated)

    def reset_chroma_db(self, on_success, on_error):
        """Resetea la base de datos de ChromaDB."""
        payload = {"memory_type": "chroma"}
        self._start_worker("reset_chroma_db", payload, on_success, on_error)

    def _start_worker(self, request_type: str, payload: Dict, on_success, on_error):
        """Método genérico para crear, configurar y ejecutar un trabajador en un hilo."""
        # Creamos el hilo y el trabajador con el ApiClient como su padre.
        # Esto asegura que no sean eliminados por el recolector de basura prematuramente.
        self.thread = QThread(self)
        self.worker = ApiWorker(request_type, payload)
        self.worker.moveToThread(self.thread)

        # Conectar la señal de éxito apropiada según el tipo de petición
        if request_type == "send_prompt":
            self.worker.response_received.connect(on_success)
        elif request_type == "get_sessions":
            self.worker.sessions_received.connect(on_success)
        elif request_type == "create_session":
            self.worker.session_created.connect(on_success)
        elif request_type == "delete_session":
            self.worker.session_deleted.connect(on_success)
        elif request_type == "get_providers":
            self.worker.providers_received.connect(on_success)
        elif request_type == "get_settings":
            self.worker.settings_received.connect(on_success)
        elif request_type == "update_settings":
            self.worker.settings_updated.connect(on_success)
        elif request_type == "reset_chroma_db":
            self.worker.chroma_reset_completed.connect(on_success)
        
        # Conectar las señales comunes
        self.worker.error_occurred.connect(on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        
        self.thread.start()
