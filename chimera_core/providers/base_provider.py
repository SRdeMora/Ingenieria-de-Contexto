
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    """
    Clase Base Abstracta (ABC) que define el "contrato" para todos los proveedores de LLM.

    Cualquier proveedor de LLM que se integre en Quimera (OpenAI, Gemini, Llama, etc.)
    debe heredar de esta clase e implementar todos sus métodos abstractos.
    Esto asegura que el Orquestador pueda tratar con cualquier proveedor de manera uniforme,
    haciendo el sistema modular y fácilmente extensible.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Devuelve el nombre del proveedor (ej. "openai", "gemini").
        """
        pass

    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        history: List[Dict[str, Any]] = [], 
        tools: List[Dict[str, Any]] = [],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Genera una respuesta a partir de un prompt, considerando el historial y las herramientas.

        Args:
            prompt (str): El prompt del usuario actual.
            history (List[Dict[str, Any]]): El historial de la conversación.
            tools (List[Dict[str, Any]]): La lista de herramientas (plugins) disponibles
                                         en formato compatible con el proveedor (ej. OpenAI Function Calling).
            **kwargs: Argumentos adicionales específicos del proveedor (ej. temperature, max_tokens).

        Returns:
            Dict[str, Any]: Un diccionario que contiene la respuesta. La estructura puede variar
                            ligeramente, pero típicamente incluirá el contenido del texto y, si aplica,
                            información sobre la herramienta a llamar.
        """
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding vectorial para un texto dado.

        Aunque ChromaDB usa `sentence-transformers` localmente, este método es útil si
        queremos usar los modelos de embedding nativos de un proveedor (ej. `text-embedding-ada-002` de OpenAI).

        Args:
            text (str): El texto a convertir en embedding.

        Returns:
            List[float]: El embedding vectorial.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Devuelve una lista de los nombres de los modelos disponibles para este proveedor.
        """
        pass
