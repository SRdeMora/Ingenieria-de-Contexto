
import os
import openai
from typing import List, Dict, Any
from .base_provider import BaseProvider
from ..utils.logger import logger

# --- Inicialización del Cliente de OpenAI ---
# Es una buena práctica inicializar el cliente una vez por módulo.
# La clave de API se carga automáticamente desde la variable de entorno OPENAI_API_KEY.
try:
    client = openai.OpenAI()
    # Cargar la clave explícitamente si está en otra variable o para mayor claridad
    client.api_key = os.getenv("OPENAI_API_KEY")
    if not client.api_key:
        logger.warning("Advertencia: La variable de entorno OPENAI_API_KEY no está configurada.")
except Exception as e:
    logger.error(f"Error al inicializar el cliente de OpenAI: {e}")
    client = None

class OpenAIProvider(BaseProvider):
    """
    Implementación concreta del proveedor para los modelos de OpenAI (GPT-3.5, GPT-4, etc.).
    """

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """
        Inicializa el proveedor con un modelo específico de OpenAI.

        Args:
            model (str): El nombre del modelo a utilizar (ej. "gpt-4-turbo-preview").
        """
        if not client:
            raise ConnectionError("El cliente de OpenAI no pudo ser inicializado. Revisa tu API key.")
        self.model = model

    def get_provider_name(self) -> str:
        return "openai"

    def generate_response(
        self, 
        prompt: str, 
        history: List[Dict[str, Any]] = [], 
        tools: List[Dict[str, Any]] = [],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Llama a la API de Chat Completions de OpenAI, soportando el protocolo de Tool Calling.
        """
        messages = history
        if prompt:
            messages.append({"role": "user", "content": prompt})
        
        try:
            api_args = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1500)
            }
            if tools:
                # Formatear las herramientas para la API de OpenAI
                api_args["tools"] = [{"type": "function", "function": tool.dict()} for tool in tools]
                api_args["tool_choice"] = "auto"

            response = client.chat.completions.create(**api_args)
            return response.choices[0].message

        except openai.APIError as e:
            logger.error(f"Error de la API de OpenAI: {e}")
            # Devolvemos un objeto de mensaje simulado para consistencia
            return openai.types.chat.ChatCompletionMessage(role='assistant', content=f"Error de OpenAI: {e}")
        except Exception as e:
            logger.error(f"Un error inesperado ocurrió: {e}")
            return openai.types.chat.ChatCompletionMessage(role='assistant', content=f"Error inesperado: {e}")

    def get_embedding(self, text: str, model="text-embedding-3-small") -> List[float]:
        """
        Obtiene un embedding para un texto usando los modelos de embedding de OpenAI.
        """
        try:
            response = client.embeddings.create(
                input=[text.replace("\n", " ")], # La API recomienda reemplazar saltos de línea
                model=model
            )
            return response.data[0].embedding
        except openai.APIError as e:
            logger.error(f"Error de la API de OpenAI al crear embedding: {e}")
            return []

    def get_available_models(self) -> List[str]:
        """
        Devuelve una lista de los nombres de los modelos de chat disponibles de OpenAI.
        """
        if not client:
            return []
        try:
            models = client.models.list()
            # Filtramos para incluir solo modelos de chat relevantes
            chat_models = [
                m.id for m in models.data 
                if "gpt" in m.id and ("-turbo" in m.id or "-4" in m.id or "-3.5" in m.id) and "instruct" not in m.id
            ]
            # Añadimos algunos modelos comunes que quizás no aparezcan en la lista completa
            common_models = ["gpt-4-turbo-preview", "gpt-3.5-turbo"]
            return sorted(list(set(chat_models + common_models)))
        except Exception as e:
            logger.error(f"Error al obtener modelos de OpenAI: {e}")
            return []

# Ejemplo de uso
if __name__ == '__main__':
    # Para probar, asegúrate de tener tu OPENAI_API_KEY en las variables de entorno
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("Por favor, establece la variable de entorno OPENAI_API_KEY para probar.")
    else:
        logger.info("Probando el OpenAIProvider...")
        provider = OpenAIProvider()
        
        logger.info(f"Proveedor: {provider.get_provider_name()}")
        logger.info(f"Modelo: {provider.model}")

        # Prueba de generación de respuesta simple
        logger.info("\n--- Prueba de Chat Básico ---")
        response_message = provider.generate_response("Hola, ¿quién eres?")
        logger.info(f"Respuesta de Quimera (OpenAI): {response_message.content}")

        # Prueba de embedding
        logger.info("\n--- Prueba de Embedding ---")
        text_to_embed = "El proyecto Quimera es un exo-córtex conversacional."
        embedding = provider.get_embedding(text_to_embed)
        if embedding:
            logger.info(f"Embedding para: '{text_to_embed}'")
            logger.info(f"Dimensiones del vector: {len(embedding)}")
            logger.info(f"Primeros 5 valores: {embedding[:5]}")
        else:
            logger.info("No se pudo generar el embedding.")
