
from transformers import pipeline
import re
from ..utils.logger import logger

class PersonalityEngine:
    def __init__(self):
        logger.info("PersonalityEngine: Cargando comité de modelos de PLN...")
        # Usamos un bloque try-except para cada modelo para un arranque más robusto
        try:
            self.intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            logger.info("Clasificador de intención (bart-large-mnli) cargado.")
        except Exception:
            logger.exception("Error al cargar el clasificador de intención. La detección de intención no estará disponible.")
            self.intent_classifier = None

        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis")
            logger.info("Analizador de sentimiento (robertuito-sentiment-analysis) cargado.")
        except Exception:
            logger.exception("Error al cargar el analizador de sentimiento. La detección de sentimiento no estará disponible.")
            self.sentiment_analyzer = None
        logger.info("PersonalityEngine: Comité de expertos listo.")

    def _analyze_structure_and_style(self, prompt: str, trace_id: str) -> dict:
        log_extra = {'trace_id': trace_id}
        logger.debug("Analizando estructura y estilo del prompt.", extra=log_extra)
        # ... (la lógica de regex para formato y estilo permanece igual)
        return {}

    def analyze_user_input(self, prompt: str, trace_id: str = 'N/A') -> dict:
        log_extra = {'trace_id': trace_id, 'data': {'prompt': prompt}}
        logger.debug("Iniciando análisis de personalidad.", extra=log_extra)
        
        if not prompt or not (self.intent_classifier or self.sentiment_analyzer):
            logger.warning("Análisis de personalidad omitido: prompt vacío o clasificadores no disponibles.", extra=log_extra)
            return {}

        final_directives = {}
        
        # --- FASE 1: ANÁLISIS DE SENTIMIENTO (Prioridad Alta) ---
        if self.sentiment_analyzer:
            try:
                sentiment_results = self.sentiment_analyzer(prompt)[0]
                sentiment_label = sentiment_results['label']
                sentiment_score = sentiment_results['score']
                
                logger.debug(f"Resultados del analizador de sentimiento: Label='{sentiment_label}', Score={sentiment_score:.2f}", extra=log_extra)

                if sentiment_label == 'NEG' and sentiment_score > 0.8: # Umbral alto para negatividad
                    final_directives['intent'] = 'queja o frustración'
                    logger.info(f"Sentimiento negativo fuerte detectado. Directiva: '{final_directives['intent']}'.", extra=log_extra)
                    return final_directives # Si hay negatividad fuerte, priorizamos esto
            except Exception:
                logger.exception("Error durante el análisis de sentimiento.", extra=log_extra)

        # --- FASE 2: ANÁLISIS DE INTENCIÓN (Si no hay sentimiento negativo fuerte) ---
        if self.intent_classifier:
            candidate_labels = [
                'saludo o conversación casual',
                'pregunta conceptual o técnica',
                'petición de brainstorming o sugerencias',
                'queja o frustración',
                'broma o comentario humorístico'
            ]
            confidence_threshold = 0.50 # Umbral de confianza para intención

            try:
                intent_results = self.intent_classifier(prompt, candidate_labels, multi_label=False)
                
                log_data = {
                    'prompt': prompt,
                    'labels': intent_results['labels'],
                    'scores': intent_results['scores'],
                    'threshold': confidence_threshold
                }
                logger.debug("Resultados del clasificador de intención Zero-Shot.", extra={'trace_id': trace_id, 'data': log_data})

                top_label = intent_results['labels'][0]
                top_score = intent_results['scores'][0]

                if top_score >= confidence_threshold:
                    final_directives['intent'] = top_label
                    logger.info(f"Intención detectada: '{top_label}' (Confianza: {top_score:.2f})", extra=log_extra)
                else:
                    logger.info(f"La intención principal ('{top_label}') no superó el umbral de confianza (Score: {top_score:.2f}). No se aplicará directiva de intención.", extra=log_extra)

            except Exception:
                logger.exception("Ocurrió un error durante la clasificación de intención.", extra=log_extra)

        # --- FASE 3: ANÁLISIS ESTRUCTURAL (simplificado por ahora) ---
        # La lógica de _analyze_structure_and_style se puede añadir aquí si es necesario

        logger.debug(f"Diagnóstico final de personalidad: {final_directives}", extra=log_extra)
        return final_directives
