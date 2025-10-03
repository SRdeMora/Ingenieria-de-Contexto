# FILE: chimera_core/context_engine.py (MODIFICADO PARA USAR GPT-3.5

import os
import json
from typing import Dict, Any, List

from .memory.redis_manager import RedisManager
from .memory.sqlite_manager import SQLiteManager
from .memory.chroma_manager import ChromaManager
from .memory.neo4j_manager import Neo4jManager
from .plugins.plugin_manager import PluginManager
from .providers.api_manager import ApiManager
from .utils.logger import logger

class ContextEngine:
    def __init__(self, api_manager: ApiManager):
        logger.info("Inicializando el Motor de Contexto y sus gestores...")
        self.api_manager = api_manager
        self.redis_manager = RedisManager()
        self.sqlite_manager = SQLiteManager()
        self.chroma_manager = ChromaManager()
        self.plugin_manager = PluginManager()
        try:
            self.neo4j_manager = Neo4jManager(
                uri=os.getenv("NEO4J_URI"), user=os.getenv("NEO4J_USER"), password=os.getenv("NEO4J_PASSWORD")
            )
        except Exception as e:
            logger.exception("Error al inicializar Neo4jManager.")
            self.neo4j_manager = None
        
        logger.info("Motor de Contexto listo.")

    def check_all_connections(self):
        logger.info("Verificando todas las conexiones de las bases de datos...")
        self.redis_manager.check_connection()
        self.sqlite_manager.check_connection()
        self.chroma_manager.check_connection()
        if self.neo4j_manager:
            self.neo4j_manager.check_connection()
        logger.info("Verificación de conexiones completada.")

    def _extract_entities_with_gpt(self, user_prompt: str, trace_id: str) -> List[str]:
        log_extra = {'trace_id': trace_id}
        logger.debug("Extrayendo entidades con GPT-3.5.", extra=log_extra)
        
        provider = self.api_manager.get_provider("openai", model="gpt-3.5-turbo", trace_id=trace_id)
        if not provider:
            logger.error("No se pudo obtener el proveedor de OpenAI para la extracción de entidades.", extra=log_extra)
            return []

        extraction_prompt = f"""
        Analiza el siguiente texto y extrae los conceptos y entidades más importantes.
        Enfócate en la intención principal de la pregunta.
        Devuelve el resultado como una lista JSON de strings.
        Por ejemplo, para "Que campos de la Inteligencia artifical quedan por explorar?", una buena extracción sería ["campos", "explorar", "inteligencia artificial"].
        Si no encuentras ninguna entidad relevante, devuelve una lista JSON vacía: [].
        Texto: "{user_prompt}"
        Entidades (SOLO el JSON):
        """

        try:
            response = provider.generate_response(prompt=extraction_prompt, history=[], tools=[])
            entities_json = response.content.strip()

            # Log the raw response for debugging
            logger.debug(f"Respuesta cruda de GPT-3.5 para extracción de entidades: '{entities_json}'", extra=log_extra)

            if not entities_json or not entities_json.startswith('['):
                logger.warning("La respuesta de GPT-3.5 no es un JSON válido o está vacía.", extra=log_extra)
                return []

            entities = json.loads(entities_json)
            if isinstance(entities, list) and all(isinstance(e, str) for e in entities):
                logger.info(f"Entidades extraídas con GPT-3.5: {entities}", extra=log_extra)
                return entities
            else:
                logger.warning(f"La respuesta de GPT-3.5 para extracción de entidades no es una lista de strings: {entities_json}", extra=log_extra)
                return []
        except json.JSONDecodeError:
            logger.exception(f"Error de decodificación JSON al extraer entidades con GPT-3.5. Respuesta recibida: '{entities_json}'", extra=log_extra)
            return []
        except Exception as e:
            logger.exception("Ocurrió un error inesperado al extraer entidades con GPT-3.5.", extra=log_extra)
            return []

    def _synthesize_context_with_gpt(self, combined_snippets: List[str], trace_id: str) -> str:
        log_extra = {'trace_id': trace_id}
        if not combined_snippets:
            return ""

        text_to_summarize = "\n".join(combined_snippets)
        
        provider = self.api_manager.get_provider("openai", model="gpt-3.5-turbo", trace_id=trace_id)
        if not provider:
            logger.error("No se pudo obtener el proveedor de OpenAI para la síntesis de contexto.", extra=log_extra)
            return ""

        summarization_prompt = f"""
        Resume los siguientes fragmentos de información en un párrafo conciso y coherente. 
        Este resumen se usará como contexto para un asistente de IA.
        Fragmentos:
        {text_to_summarize}
        Resumen:
        """

        try:
            response = provider.generate_response(prompt=summarization_prompt, history=[], tools=[], temperature=0.3, max_tokens=300)
            synthesized_context = response.content.strip()
            logger.info("Contexto sintetizado con GPT-3.5.", extra=log_extra)
            return synthesized_context
        except Exception as e:
            logger.exception("Error durante la síntesis de contexto con GPT-3.5.", extra=log_extra)
            return ""

    def build_augmented_prompt(self, session_id: str, user_prompt: str, personality_directives: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        log_extra = {'trace_id': trace_id}
        relevant_context_snippets = []

        # --- PASO 0: Recuperar Resumen de Memoria a Medio Plazo (SQLite) ---
        summary = self.sqlite_manager.get_summary(session_id, trace_id)
        if summary and summary[0]:
            summary_text = summary[0]
            logger.info(f"\n--- PASO 0: RESUMEN DE MEMORIA A MEDIO PLAZO RECUPERADO ---\n{summary_text}", extra=log_extra)
            relevant_context_snippets.append(summary_text)

        # --- PASO 1: Extracción de Entidades con GPT-3.5 ---
        entity_names = self._extract_entities_with_gpt(user_prompt, trace_id)
        logger.info(f"\n--- PASO 1: ENTIDADES EXTRAÍDAS ---\n{json.dumps(entity_names, indent=2, ensure_ascii=False)}", extra=log_extra)

        # --- PASO 2 & 3: Búsqueda Condicional en Memoria a Largo Plazo ---
        if entity_names:
            logger.info("Entidades relevantes encontradas. Consultando memoria a largo plazo...", extra=log_extra)
            # --- Búsqueda en ChromaDB ---
            logger.debug(f"Iniciando búsqueda en ChromaDB por entidades: {entity_names}", extra=log_extra)
            for entity_name in entity_names:
                search_query = f"¿Qué información relevante hay sobre {entity_name}?"
                similar_memories = self.chroma_manager.search_similar(query_text=search_query, n_results=5, filter_by_session=session_id, trace_id=trace_id)
                if similar_memories and similar_memories.get('documents') and similar_memories['documents'][0]:
                    chroma_results = similar_memories['documents'][0]
                    log_message = f"\n--- PASO 2.1: CONTENIDO RECUPERADO DE CHROMADB (para '{entity_name}') ---"
                    for i, doc in enumerate(chroma_results):
                        log_message += f"\n[DOC {i+1}]: {doc}"
                    logger.info(log_message, extra=log_extra)
                    truncated_results = [doc[:300] + "..." if len(doc) > 300 else doc for doc in chroma_results]
                    relevant_context_snippets.extend(truncated_results)
            
            # --- Búsqueda en Neo4j ---
            if self.neo4j_manager:
                structural_info_parts = []
                for entity_name in entity_names:
                    related_concepts = self.neo4j_manager.get_related_entities(entity_name, session_id, limit=5, trace_id=trace_id)
                    if related_concepts:
                        info = f"Sobre el concepto '{entity_name}', el sistema también conoce estos temas relacionados: {', '.join(related_concepts)}."
                        structural_info_parts.append(info)
                
                if structural_info_parts:
                    full_structural_info = " ".join(structural_info_parts)
                    logger.info(f"\n--- PASO 3: CONTENIDO RECUPERADO DE NEO4J ---\n{full_structural_info}", extra=log_extra)
                    relevant_context_snippets.append(full_structural_info)
        else:
            logger.info("No se encontraron entidades relevantes. Omitiendo consulta a memoria a largo plazo.", extra=log_extra)
        
        final_context = ""
        unique_snippets = list(dict.fromkeys(relevant_context_snippets))
        
        if unique_snippets:
            log_message = "\n--- PASO 4: DOSSIER DE FRAGMENTOS PARA RESUMIR ---"
            for i, snippet in enumerate(unique_snippets):
                log_message += f"\n[SNIPPET {i+1}]: {snippet}"
            logger.info(log_message, extra=log_extra)

            synthesized_context = self._synthesize_context_with_gpt(unique_snippets, trace_id)
            if synthesized_context:
                final_context = f"--- CONTEXTO DE MEMORIA A LARGO-MEDIO PLAZO ---\n{synthesized_context}"
                logger.info(f"\n--- PASO 5: CONTEXTO FINAL SINTETIZADO ---\n{final_context}", extra=log_extra)

        personality_instruction = self._translate_directives_to_prompt(personality_directives)
        tools = self.plugin_manager.get_all_tools()
        conversational_history = self.redis_manager.get_recent_turns(session_id, num_turns=10, trace_id=trace_id)

        system_prompt_parts = [
            "Eres Quimera, un asistente de IA avanzado.",
            personality_instruction,
            final_context,
            "Responde de manera útil y coherente..."
        ]
        
        final_system_prompt = "\n".join(filter(None, system_prompt_parts))
        log_message = "\n--- PASO 6: PROMPT DE SISTEMA FINAL ENSAMBLADO ---"
        for part in final_system_prompt.split('\n'):
            log_message += f"\n{part}"
        logger.info(log_message, extra=log_extra)

        return {"system_prompt": final_system_prompt, "history": conversational_history, "tools": tools, "entities": entity_names}

    def _translate_directives_to_prompt(self, directives: dict) -> str:
        intent = directives.get('intent')
        if intent == 'pregunta conceptual o técnica': return "El usuario ha hecho una pregunta técnica. Sé preciso y detallado en tu respuesta."
        if intent == 'broma o comentario humorístico': return "El usuario está de humor para bromas. Responde de una manera ligera y divertida."
        return ""
    
    def save_turn(self, session_id: str, user_prompt: str, assistant_response: str, user_turn_id: str, assistant_turn_id: str, trace_id: str, user_entities: List[str]):
        log_extra = {'trace_id': trace_id}
        logger.debug("Guardando turno en las capas de memoria.", extra=log_extra)
        self.redis_manager.add_turn(session_id, {"role": "user", "content": user_prompt}, trace_id)
        self.redis_manager.add_turn(session_id, {"role": "assistant", "content": assistant_response}, trace_id)
        
        self.chroma_manager.add_entry(session_id, assistant_response, assistant_turn_id, {"role": "assistant"}, trace_id)
        
        if self.neo4j_manager:
            assistant_entities = self._extract_entities_with_gpt(assistant_response, trace_id)
            user_entities_dict = [{"text": entity, "label": "MISC"} for entity in user_entities]
            assistant_entities_dict = [{"text": entity, "label": "MISC"} for entity in assistant_entities]

            self.neo4j_manager.add_message_and_entities(session_id, user_turn_id, "user", user_prompt, user_entities_dict, trace_id)
            self.neo4j_manager.add_message_and_entities(session_id, assistant_turn_id, "assistant", assistant_response, assistant_entities_dict, trace_id)
