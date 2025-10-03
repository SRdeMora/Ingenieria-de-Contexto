# FILE: chimera_core/utils/logger.py (VERSIÓN CORREGIDA DEL SYNTAXERROR)

import logging
import logging.handlers
import os
import json

# --- ESTADO GLOBAL PARA SEPARADORES ---
_last_trace_id = None

# --- FILTRO PARA DETECTAR NUEVAS INTERACCIONES ---
class TraceChangeFilter(logging.Filter):
    def filter(self, record):
        global _last_trace_id
        trace_id = getattr(record, 'trace_id', 'N/A')
        if not hasattr(record, 'trace_id'):
            record.trace_id = 'N/A'
        is_new_trace = (trace_id != 'N/A' and trace_id != _last_trace_id)
        record.new_trace = is_new_trace
        if is_new_trace:
            _last_trace_id = trace_id
        return True

# --- FORMATEADOR DE TEXTO PLANO MEJORADO (CORREGIDO) ---
class PlainTextTraceFormatter(logging.Formatter):
    """
    Formateador mejorado que añade separadores y es capaz de registrar
    datos extra y excepciones en un formato de texto legible.
    """
    def format(self, record):
        # 1. Formatea el mensaje base
        log_message = super().format(record)

        # 2. Añade datos extra si existen
        if hasattr(record, 'data'):
            extra_data_str = json.dumps(record.data, indent=4, ensure_ascii=False)
            # CORRECCIÓN: Se realiza el replace fuera del f-string para evitar el SyntaxError
            indented_data = extra_data_str.replace('\n', '\n    ')
            log_message += f"\n    [EXTRA DATA]\n    {indented_data}"

        # 3. Añade información de la excepción si existe
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            log_message += f"\n[EXCEPTION]\n{exc_text}"

        # 4. Añade el separador de interacción si es un nuevo trace
        if getattr(record, 'new_trace', False):
            separator = "\n" + "="*120 + "\n"
            separator += f"=== INICIO DE INTERACCIÓN | Trace ID: {getattr(record, 'trace_id', 'N/A')} ===="
            separator += "\n" + "="*120 + "\n"
            return separator + log_message
        
        return log_message

# --- CONFIGURACIÓN CENTRAL ---
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'chimera_logs')
LOG_FILE = "chimera_trace.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# --- FUNCIÓN DE CONFIGURACIÓN DEL LOGGER ---
def setup_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger("ChimeraLogger")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addFilter(TraceChangeFilter())

    fmt = '%(asctime)s - %(levelname)s - [%(module)s:%(funcName)s:%(lineno)d] - (Trace: %(trace_id)s) - %(message)s'
    formatter = PlainTextTraceFormatter(fmt=fmt)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_PATH, when="midnight", interval=1, backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)

    return logger

# --- Instancia Global ---
logger = setup_logger()

# --- EJEMPLO DE USO ---
if __name__ == '__main__':
    print("--- Ejecutando prueba del logger de texto mejorado ---")
    
    # Primera interacción
    trace_1 = "trace-abc-123"
    logger.info("Inicio de la primera operación.", extra={'trace_id': trace_1})
    logger.debug("Procesando datos internos.", extra={'trace_id': trace_1, 'data': {'user_id': 1, 'scope': 'read'}})
    
    # Segunda interacción (debería crear un separador)
    trace_2 = "trace-def-456"
    logger.info("Inicio de la segunda operación.", extra={'trace_id': trace_2})
    logger.warning("El token de usuario está a punto de expirar.", extra={'trace_id': trace_2, 'data': {'token_id': 'xyz'}})
    
    # Tercera interacción con un error
    trace_3 = "trace-ghi-789"
    try:
        result = 1 / 0
    except ZeroDivisionError:
        logger.exception("Ha ocurrido una excepción grave.", extra={'trace_id': trace_3, 'data': {'input': 0}})

    print("\n--- Prueba finalizada ---")
    print(f"Verifica el archivo '{LOG_PATH}' para ver los logs de texto con datos extra.")
