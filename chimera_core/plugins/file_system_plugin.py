import os
from typing import Dict, Any, List

from .mcp_base import MCPPlugin, ToolSignature

# Por seguridad, restringimos todas las operaciones a la raíz del proyecto.
# Esto previene que el LLM pueda acceder a archivos fuera de su directorio de trabajo.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def _is_safe_path(path: str) -> bool:
    """Comprueba que la ruta solicitada está dentro del directorio del proyecto."""
    requested_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    return os.path.commonpath([requested_path, PROJECT_ROOT]) == PROJECT_ROOT

class FileSystemPlugin(MCPPlugin):
    """
    Un plugin que proporciona herramientas para interactuar con el sistema de archivos local
    de forma segura, restringido al directorio del proyecto.
    """

    @property
    def name(self) -> str:
        return "file_system"

    def get_tools(self) -> List[ToolSignature]:
        return [
            ToolSignature(
                name="list_directory",
                description="Lista el contenido (archivos y directorios) de una ruta específica relativa a la raíz del proyecto.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "La ruta del directorio a listar."}
                    },
                    "required": ["path"]
                }
            ),
            ToolSignature(
                name="read_file",
                description="Lee y devuelve el contenido de un archivo de texto específico.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "La ruta del archivo a leer."}
                    },
                    "required": ["path"]
                }
            )
        ]

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path", ".")

        if not _is_safe_path(path):
            return {"status": "error", "error_message": f"Acceso denegado. La ruta '{path}' está fuera del directorio del proyecto."}

        full_path = os.path.join(PROJECT_ROOT, path)

        try:
            if tool_name == "list_directory":
                if not os.path.isdir(full_path):
                    return {"status": "error", "error_message": f"La ruta '{path}' no es un directorio válido."}
                
                content = os.listdir(full_path)
                return {"status": "success", "result": content}

            elif tool_name == "read_file":
                if not os.path.isfile(full_path):
                    return {"status": "error", "error_message": f"El archivo '{path}' no se encontró."}
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"status": "success", "result": content}

            else:
                return {"status": "error", "error_message": f"La herramienta '{tool_name}' no es reconocida por el plugin {self.name}."}
        
        except Exception as e:
            return {"status": "error", "error_message": str(e)}
