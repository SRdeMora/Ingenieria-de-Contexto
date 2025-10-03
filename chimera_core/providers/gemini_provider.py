
import os
import google.generativeai as genai
from typing import List, Dict, Any
from .base_provider import BaseProvider

# --- Inicialización del Cliente de Gemini ---
# La clave de API se carga automáticamente desde la variable de entorno GOOGLE_API_KEY.
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    if not os.getenv("GOOGLE_API_KEY"):
        print("Advertencia: La variable de entorno GOOGLE_API_KEY no está configurada.")
except Exception as e:
    print(f"Error al configurar el cliente de Gemini: {e}")

class GeminiProvider(BaseProvider):
    """
    Implementación concreta del proveedor para los modelos de Google Gemini.
    """

    def __init__(self, model: str = "gemini-pro"):
        """
        Inicializa el proveedor con un modelo específico de Gemini.

        Args:
            model (str): El nombre del modelo a utilizar (ej. "gemini-pro").
        """
        if not os.getenv("GOOGLE_API_KEY"):
            raise ConnectionError("La API key de Google Gemini no está configurada.")
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    def get_provider_name(self) -> str:
        return "gemini"

    def generate_response(
        self, 
        prompt: str, 
        history: List[Dict[str, Any]] = [], 
        tools: List[Dict[str, Any]] = [],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Genera una respuesta utilizando la API de Gemini.

        Args:
            prompt (str): El prompt del usuario actual.
            history (List[Dict[str, Any]]): El historial de la conversación.
            tools (List[Dict[str, Any]]): La lista de herramientas (no implementado para Gemini aún).
            **kwargs: Argumentos adicionales específicos del proveedor (ej. temperature, max_output_tokens).

        Returns:
            Dict[str, Any]: Un diccionario que contiene la respuesta.
        """
        # Gemini API espera un formato ligeramente diferente para el historial
        # y no soporta un 'system' role directamente en el historial de chat.
        # El 'system_prompt' debe ser parte del primer mensaje o de la instrucción inicial.
        # Por simplicidad, lo concatenaremos al primer mensaje del historial.
        
        # Convertir el historial al formato de Gemini
        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "system" or msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Añadir el prompt actual del usuario
        gemini_history.append({"role": "user", "parts": [prompt]})

        try:
            # Gemini no tiene un parámetro 'tools' directo en generate_content como OpenAI.
            # Esto requeriría un manejo más complejo para Function Calling.
            # Por ahora, ignoramos el parámetro 'tools'.
            response = self.model.generate_content(
                gemini_history,
                generation_config=genai.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 800) # Usamos max_tokens
                )
            )
            
            # La respuesta de Gemini puede tener múltiples candidatos.
            # Tomamos el primero y su texto.
            return {"role": "assistant", "content": response.text}

        except Exception as e:
            print(f"Error de la API de Gemini: {e}")
            return {"role": "assistant", "content": f"Error de Gemini: {e}"}

    def get_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding vectorial para un texto dado usando el modelo de embedding de Gemini.
        """
        try:
            response = genai.embed_content(model="models/embedding-001", content=text)
            return response['embedding']
        except Exception as e:
            print(f"Error de la API de Gemini al crear embedding: {e}")
            return []

    def get_available_models(self) -> List[str]:
        """
        Devuelve una lista de los nombres de los modelos de chat disponibles de Gemini.
        """
        if not os.getenv("GOOGLE_API_KEY"):
            return []
        try:
            # Listar solo modelos de tipo "generative" (chat)
            models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            return sorted(models)
        except Exception as e:
            print(f"Error al obtener modelos de Gemini: {e}")
            return []

# Ejemplo de uso
if __name__ == '__main__':
    # Para probar, asegúrate de tener tu GOOGLE_API_KEY en las variables de entorno
    if not os.getenv("GOOGLE_API_KEY"):
        print("Por favor, establece la variable de entorno GOOGLE_API_KEY para probar.")
    else:
        print("Probando el GeminiProvider...")
        provider = GeminiProvider()
        
        print(f"Proveedor: {provider.get_provider_name()}")
        print(f"Modelo: {provider.model_name}")

        # Prueba de generación de respuesta simple
        print("\n--- Prueba de Chat Básico ---")
        response_message = provider.generate_response("Hola, ¿quién eres?")
        print(f"Respuesta de Quimera (Gemini): {response_message['content']}")

        # Prueba de embedding
        print("\n--- Prueba de Embedding ---")
        text_to_embed = "El proyecto Quimera es un exo-córtex conversacional."
        embedding = provider.get_embedding(text_to_embed)
        if embedding:
            print(f"Embedding para: '{text_to_embed}'")
            print(f"Dimensiones del vector: {len(embedding)}")
            print(f"Primeros 5 valores: {embedding[:5]}")
        else:
            print("No se pudo generar el embedding.")
