# FILE: chimera_core/orchestrator.py (VERSIÓN CORREGIDA)

import uuid
import json
from typing import Dict, Any, List
import time
from fastapi import BackgroundTasks
from pydantic import BaseModel

# Importación añadida para el type hinting del proveedor
from .providers.base_provider import BaseProvider

class LLMSettings(BaseModel):
    provider_name: str
    model_name: str
    temperature: float
    max_tokens: int
    # Podríamos añadir más campos como el contexto utilizado, herramientas ejecutadas, etc.

from .context_engine import ContextEngine
from .meta.personality_engine import PersonalityEngine
from .providers.api_manager import ApiManager
from .utils.logger import logger

class Orchestrator:
    def __init__(self):
        logger.info("Inicializando el Orquestador...")
        self.api_manager = ApiManager()
        self.context_engine = ContextEngine(api_manager=self.api_manager)
        self.personality_engine = PersonalityEngine()
        self.llm_config = {
            "provider_name": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 1500
        }
        logger.info("Orquestador listo.")

    def handle_user_request(self, session_id: str, user_prompt: str, llm_settings: LLMSettings, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        log_extra = {'trace_id': trace_id}
        
        logger.info(f"Iniciando manejo de petición para la sesión {session_id}.", extra=log_extra)
        
        self.update_llm_settings(
            llm_settings.provider_name,
            llm_settings.model_name,
            llm_settings.temperature,
            llm_settings.max_tokens,
            trace_id
        )
        
        start_time = time.time()
        
        # --- FASE 1: ANÁLISIS Y TRIAGE ---
        # CORRECCIÓN: Pasar el trace_id a analyze_user_input
        personality_directives = self.personality_engine.analyze_user_input(user_prompt, trace_id=trace_id)
        #memory_flags = self.context_engine._determine_memory_relevance(user_prompt)
        
        # --- FASE 2: CONSTRUCCIÓN DE CONTEXTO ---
        augmented_context = self.context_engine.build_augmented_prompt(
            session_id=session_id, user_prompt=user_prompt,
            personality_directives=personality_directives, trace_id=trace_id
        )
        
        system_prompt = augmented_context["system_prompt"]
        history = augmented_context["history"]
        tools = augmented_context["tools"]
        entities = augmented_context["entities"]
        api_history = [{"role": "system", "content": system_prompt}] + history

        # CORRECCIÓN: Crear la instancia del proveedor una vez y pasar el trace_id
        llm_provider = self.api_manager.get_provider(
            self.llm_config['provider_name'],
            model=self.llm_config['model_name'],
            trace_id=trace_id
        )
        if not llm_provider:
            logger.error(f"Proveedor LLM '{self.llm_config['provider_name']}' no encontrado.", extra=log_extra)
            return {"error": f"Proveedor '{self.llm_config['provider_name']}' no encontrado."}
            
        # --- FASE 3: LLAMADA A LA API Y BUCLE DE HERRAMIENTAS ---
        api_call_params = {
            "temperature": self.llm_config["temperature"],
            "max_tokens": self.llm_config["max_tokens"]
        }

        logger.info("Enviando petición inicial al LLM.", extra=log_extra)
        log_message = f"Prompt inicial enviado al LLM: user_prompt='{user_prompt}'"
        log_message += "\n--- API HISTORY ---"
        for turn in api_history:
            role = ""
            content = ""
            if isinstance(turn, dict):
                role = turn.get('role')
                content = turn.get('content')
            elif hasattr(turn, 'role') and hasattr(turn, 'content'):
                role = turn.role
                content = turn.content
            elif hasattr(turn, 'tool_calls') and turn.tool_calls: # Handle tool calls
                role = "tool_calls"
                content = str(turn.tool_calls) # Convert tool_calls to string for logging
            
            log_message += f"\n- ROLE: {role}"
            # Truncate content for readability in logs
            truncated_content = (content[:200] + '...') if content and len(content) > 200 else content
            log_message += f"\n  CONTENT: {truncated_content}"
        logger.debug(log_message, extra=log_extra)
        response_message = llm_provider.generate_response(
            prompt=user_prompt, history=api_history, tools=tools, **api_call_params
        )

        while response_message and response_message.tool_calls:
            logger.info("Llamada a herramienta detectada por el LLM.", extra=log_extra)
            api_history.append(response_message.model_dump())

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    logger.error(f"Error al decodificar argumentos JSON para '{function_name}'.", extra=log_extra)
                    arguments = {}

                plugin_name = self.context_engine.plugin_manager.find_plugin_for_tool(function_name)
                
                if not plugin_name:
                    logger.error(f"No se encontró plugin para la herramienta '{function_name}'.", extra=log_extra)
                    continue

                logger.info(f"Ejecutando herramienta: '{plugin_name}.{function_name}'.", extra={'trace_id': trace_id, 'data': arguments})
                tool_result = self.context_engine.plugin_manager.execute_tool(
                    plugin_name=plugin_name, tool_name=function_name, **arguments
                )
                logger.info(f"Resultado de la herramienta: {tool_result}", extra=log_extra)

                api_history.append(
                    {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": json.dumps(tool_result)}
                )
            
            logger.info("Enviando resultado de la herramienta al LLM para obtener respuesta final.", extra=log_extra)
            log_message = f"Prompt de seguimiento enviado al LLM (después de herramienta):"
            log_message += "\n--- API HISTORY ---\n"
            for turn in api_history:
                role = ""
                content = ""
                if isinstance(turn, dict):
                    role = turn.get('role')
                    content = turn.get('content')
                elif hasattr(turn, 'role') and hasattr(turn, 'content'):
                    role = turn.role
                    content = turn.content
                elif hasattr(turn, 'tool_calls') and turn.tool_calls: # Handle tool calls
                    role = "tool_calls"
                    content = str(turn.tool_calls) # Convert tool_calls to string for logging
                
                log_message += f"\n- ROLE: {role}"
                # Truncate content for readability in logs
                truncated_content = (content[:200] + '...') if content and len(content) > 200 else content
                log_message += f"\n  CONTENT: {truncated_content}"
            logger.debug(log_message, extra=log_extra)
            response_message = llm_provider.generate_response(
                prompt=None, history=api_history, tools=tools, **api_call_params
            )

        final_response_text = response_message.content if response_message else "No se recibió respuesta del LLM."

        # --- FASE 4: PERSISTENCIA ---
        user_turn_id = f"{session_id}_{uuid.uuid4()}"
        assistant_turn_id = f"{session_id}_{uuid.uuid4()}"
        self.context_engine.save_turn(session_id, user_prompt, final_response_text, user_turn_id, assistant_turn_id, trace_id, entities)

        # --- FASE 5: RESUMEN ASÍNCRONO ---
        turn_count = self.context_engine.redis_manager.client.llen(self.context_engine.redis_manager._get_session_key(session_id))
        if turn_count > 10:
            logger.info(f"Umbral de resumen alcanzado (Turno {turn_count}). Disparando tarea de fondo.", extra=log_extra)
            background_tasks.add_task(self._summarize_and_update_mid_term_memory, session_id, trace_id)

        execution_time = (time.time() - start_time) * 1000
        logger.info(f"Petición manejada exitosamente en {execution_time:.2f} ms.", extra=log_extra)
        return {"response": final_response_text}

    # CORRECCIÓN: Modificar la firma de la función para aceptar la instancia del proveedor
    def _summarize_and_update_mid_term_memory(self, session_id: str, trace_id: str):
        """[TAREA EN SEGUNDO PLANO] Genera un resumen de los turnos más antiguos y los poda de Redis."""
        log_extra = {'trace_id': trace_id}
        logger.info("Iniciando proceso de resumen rodante para la memoria a medio plazo.", extra=log_extra)

        # 1. Obtener todo el historial
        all_turns = self.context_engine.redis_manager.get_recent_turns(session_id, num_turns=0, trace_id=trace_id) # num_turns=0 para obtener todo
        
        num_turns_to_summarize = len(all_turns) - 10
        if num_turns_to_summarize <= 0:
            logger.info("No hay suficientes turnos para resumir.", extra=log_extra)
            return

        # 2. Seleccionar los turnos a resumir
        turns_to_summarize = all_turns[:num_turns_to_summarize]
        
        # 3. Crear el resumen
        conversation_text = "\n".join([f"{turn['role']}: {turn['content']}" for turn in turns_to_summarize])
        previous_summary = self.context_engine.sqlite_manager.get_summary(session_id, trace_id)
        previous_summary_text = f"Resumen anterior: {previous_summary[0]}" if previous_summary else "Este es el primer resumen de la conversación."

        summarization_prompt = f"{previous_summary_text}\n\nBasándote en el resumen anterior y el siguiente extracto de la conversación reciente, actualiza el resumen de forma concisa, capturando solo la información o conclusiones clave en una o dos frases.\n\nConversación Reciente:\n{conversation_text}\n\nResumen actualizado y conciso:"

        provider = self.api_manager.get_provider("openai", model="gpt-3.5-turbo", trace_id=trace_id)
        if not provider:
            logger.error("No se pudo obtener el proveedor de OpenAI para el resumen de medio plazo.", extra=log_extra)
            return

        try:
            summary_response = provider.generate_response(
                prompt=summarization_prompt, history=[], tools=[], temperature=0.2, max_tokens=250
            )
            summary_text = summary_response.content.strip()
            
            # 4. Actualizar el resumen en SQLite
            self.context_engine.sqlite_manager.update_summary(session_id, summary_text, len(all_turns), trace_id)
            logger.info(f"Memoria a medio plazo (SQLite) actualizada con nuevo resumen.", extra={'trace_id': trace_id, 'data': {'summary': summary_text}})

            # 5. Podar el historial de Redis
            self.context_engine.redis_manager.trim_history(session_id, 10, trace_id)

        except Exception:
            logger.exception("Ocurrió un error durante el proceso de resumen en segundo plano.", extra=log_extra)

    def delete_session_data(self, session_id: str) -> bool:
        trace_id = str(uuid.uuid4())
        log_extra = {'trace_id': trace_id}
        logger.info(f"Iniciando eliminación de datos para la sesión {session_id}.", extra=log_extra)
        try:
            self.context_engine.sqlite_manager.delete_session(session_id, trace_id)
            self.context_engine.redis_manager.delete_session_history(session_id, trace_id)
            self.context_engine.chroma_manager.delete_session_entries(session_id, trace_id)
            if self.context_engine.neo4j_manager:
                self.context_engine.neo4j_manager.delete_session_graph(session_id, trace_id)
            logger.info(f"Borrado de sesión {session_id} completado.", extra=log_extra)
            return True
        except Exception as e:
            logger.exception(f"Error durante el borrado en cascada para la sesión {session_id}.", extra=log_extra)
            return False

    def update_llm_settings(self, provider_name: str, model_name: str, temperature: float, max_tokens: int, trace_id: str = None):
        log_extra = {'trace_id': trace_id or 'N/A'}
        if provider_name is not None: self.llm_config["provider_name"] = provider_name
        if model_name is not None: self.llm_config["model_name"] = model_name
        if temperature is not None: self.llm_config["temperature"] = temperature
        if max_tokens is not None: self.llm_config["max_tokens"] = max_tokens
        logger.info(f"Configuración de LLM actualizada.", extra={'trace_id': trace_id, 'data': self.llm_config})

    def get_current_llm_settings(self) -> Dict[str, Any]:
        return self.llm_config