from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ToolSignature(BaseModel):
    """
    Define la estructura de la firma de una herramienta que se presentará al LLM.
    Esto permite al LLM entender qué herramientas tiene a su disposición y cómo usarlas.
    """
    name: str = Field(..., description="El nombre único de la herramienta, usado para invocarla.")
    description: str = Field(..., description="Una descripción clara de lo que hace la herramienta y cuándo usarla.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Un diccionario que describe los parámetros que la herramienta acepta, siguiendo el formato de esquema JSON.")

class MCPPlugin(ABC):
    """
    La clase base abstracta para todos los plugins del Master Control Program (MCP).

    Cada plugin representa una capacidad o "herramienta" que Quimera puede utilizar.
    Esta clase define el contrato que todos los plugins deben seguir para ser
    descubiertos y utilizados por el PluginManager y el Orchestrator.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """El nombre único y programático del plugin (ej. 'file_system')."""
        pass

    @abstractmethod
    def get_tools(self) -> List[ToolSignature]:
        """
        Devuelve una lista de las firmas de las herramientas que este plugin proporciona.
        Esta información se usará para que el LLM sepa qué puede hacer.
        """
        pass

    @abstractmethod
    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica proporcionada por este plugin.

        Args:
            tool_name (str): El nombre de la herramienta a ejecutar.
            **kwargs: Los argumentos necesarios para la herramienta.

        Returns:
            Un diccionario con el resultado de la operación. Debe ser serializable a JSON.
            Por convención, debería contener una clave 'status' ('success' o 'error')
            y una clave 'result' o 'error_message'.
        """
        pass
