import os
import importlib
import inspect
from typing import Dict, Any, List

from .mcp_base import MCPPlugin, ToolSignature

class PluginManager:
    """
    Descubre, carga y gestiona todos los plugins MCP disponibles.

    Actúa como un registro central para todas las herramientas que Quimera puede usar,
    y como el punto de entrada para ejecutar cualquier acción.
    """

    def __init__(self, plugin_dir: str = "chimera_core/plugins"):
        self.plugins: Dict[str, MCPPlugin] = {}
        self._load_plugins(plugin_dir)

    def _load_plugins(self, plugin_dir: str):
        """
        Escanea un directorio, importa dinámicamente los módulos de plugins,
        y los registra.
        """
        print("--- PluginManager: Cargando plugins... ---")
        for filename in os.listdir(plugin_dir):
            if filename.endswith("_plugin.py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = f"{plugin_dir.replace('/', '.')}.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    for name, cls in inspect.getmembers(module, inspect.isclass):
                        if issubclass(cls, MCPPlugin) and cls is not MCPPlugin:
                            plugin_instance = cls()
                            self.plugins[plugin_instance.name] = plugin_instance
                            print(f"  - Plugin '{plugin_instance.name}' cargado exitosamente.")
                except Exception as e:
                    print(f"Error al cargar el plugin {module_name}: {e}")
        print("--- Carga de plugins finalizada. ---")

    def get_all_tools(self) -> List[ToolSignature]:
        """
        Recopila y devuelve las firmas de todas las herramientas de todos los plugins cargados.
        """
        all_tools = []
        for plugin in self.plugins.values():
            all_tools.extend(plugin.get_tools())
        return all_tools

    def execute_tool(self, plugin_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica de un plugin.
        """
        if plugin_name not in self.plugins:
            return {"status": "error", "error_message": f"Plugin '{plugin_name}' no encontrado."}
        
        plugin = self.plugins[plugin_name]
        try:
            return plugin.execute(tool_name=tool_name, **kwargs)
        except Exception as e:
            return {"status": "error", "error_message": f"Error al ejecutar la herramienta '{tool_name}' en el plugin '{plugin_name}': {e}"}

    def find_plugin_for_tool(self, tool_name: str) -> str | None:
        """
        Encuentra el nombre del plugin que posee una herramienta específica.
        """
        for plugin_name, plugin in self.plugins.items():
            for tool in plugin.get_tools():
                if tool.name == tool_name:
                    return plugin_name
        return None
