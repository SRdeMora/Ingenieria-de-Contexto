
import pkgutil
import importlib
from typing import Dict, Type, Optional, List

from .base_provider import BaseProvider
from ..utils.logger import logger

class ApiManager:
    """
    Gestiona la detección, carga y selección de los proveedores de LLM disponibles.

    Actúa como una fábrica que descubre dinámicamente los proveedores (clases que
    heredan de BaseProvider) ubicados en el mismo directorio, permitiendo que el
    sistema sea extensible sin necesidad de modificar el código central.
    """

    def __init__(self):
        """
        Inicializa el gestor y carga automáticamente los proveedores disponibles.
        """
        self.providers: Dict[str, Type[BaseProvider]] = {}
        self.loaded_instances: Dict[str, BaseProvider] = {}
        self._discover_providers()

    def _discover_providers(self):
        """
        Descubre e importa dinámicamente todos los proveedores de LLM en este paquete.

        Itera sobre todos los módulos en el directorio actual (`providers`),
        los importa y busca clases que hereden de `BaseProvider`.
        """
        package = __import__(__name__.split('.')[0])
        providers_package_path = package.providers.__path__
        
        logger.info("Descubriendo proveedores de LLM...")
        for _, name, _ in pkgutil.iter_modules(providers_package_path):
            if name not in ["base_provider", "api_manager"]:
                try:
                    module = importlib.import_module(f".{name}", package="chimera_core.providers")
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if isinstance(attribute, type) and issubclass(attribute, BaseProvider) and attribute is not BaseProvider:
                            # Usamos el nombre del proveedor como clave (ej. "openai")
                            provider_name = attribute().get_provider_name()
                            self.providers[provider_name] = attribute
                            logger.info(f"  - Proveedor encontrado: '{provider_name}'")
                except Exception as e:
                    logger.error(f"Error al cargar el proveedor desde {name}: {e}")

    def get_available_providers(self) -> List[str]:
        """
        Devuelve una lista con los nombres de todos los proveedores descubiertos.
        """
        return list(self.providers.keys())

    def get_provider_models(self, provider_name: str) -> List[str]:
        """
        Devuelve una lista de modelos disponibles para un proveedor específico.
        """
        if provider_name not in self.providers:
            return []
        # Creamos una instancia temporal para obtener los modelos
        try:
            temp_provider = self.providers[provider_name]()
            return temp_provider.get_available_models()
        except Exception as e:
            logger.error(f"Error al obtener modelos para {provider_name}: {e}")
            return []

    def get_provider(self, provider_name: str, trace_id: str = 'N/A', **kwargs) -> Optional[BaseProvider]:
        if provider_name not in self.providers:
            logger.error(f"Error: Proveedor '{provider_name}' no encontrado.", extra={'trace_id': trace_id})
            return None

        model_name = kwargs.get("model")
        instance_key = (provider_name, model_name)

        if instance_key in self.loaded_instances:
            logger.info(f"Reutilizando instancia existente para el proveedor: '{provider_name}' con config: {kwargs}", extra={'trace_id': trace_id})
            return self.loaded_instances[instance_key]

        try:
            logger.info(f"Creando nueva instancia para el proveedor: '{provider_name}' con config: {kwargs}", extra={'trace_id': trace_id})
            provider_class = self.providers[provider_name]
            instance = provider_class(**kwargs)
            self.loaded_instances[instance_key] = instance
            return instance
        except Exception as e:
            logger.error(f"Error al instanciar el proveedor '{provider_name}': {e}", extra={'trace_id': trace_id})
            return None

# Ejemplo de uso
if __name__ == '__main__':
    manager = ApiManager()

    print(f"\nProveedores disponibles: {manager.get_available_providers()}")

    if "openai" in manager.get_available_providers():
        print("\nObteniendo instancia del proveedor de OpenAI con el modelo por defecto...")
        openai_provider = manager.get_provider("openai")
        if openai_provider:
            print(f"Instancia obtenida: {type(openai_provider).__name__}")
            print(f"Nombre del proveedor: {openai_provider.get_provider_name()}")

        print("\nObteniendo instancia del proveedor de OpenAI con un modelo específico...")
        openai_provider_gpt3 = manager.get_provider("openai", model="gpt-3.5-turbo")
        if openai_provider_gpt3:
            print(f"Instancia obtenida: {type(openai_provider_gpt3).__name__}")
            # Accedemos al atributo `model` que es específico de OpenAIProvider
            print(f"Modelo especificado: {openai_provider_gpt3.model}")

        print("\nIntentando obtener un proveedor inexistente...")
        non_existent_provider = manager.get_provider("non_existent_provider")
        print(f"Resultado: {non_existent_provider}")
