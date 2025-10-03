De acuerdo. Acepto el desafío.

Has superado las explicaciones y las analogías. Quieres el plano de ingeniería final, basado en todo lo que hemos deducido y en las arquitecturas de producción reales. Quieres que Quimera sea verdaderamente adaptativo.

Aquí están los pasos exactos. Este es un plan ambicioso que combina varias técnicas. No es simple, pero es la forma correcta de construir un sistema de este calibre.

---

### **Plan de Acción Integral para un Quimera Adaptativo**

Este plan se divide en tres fases: **Análisis de Entrada**, **Construcción de Contexto Dinámico** y **Respuesta Adaptativa**. Lo implementaremos modificando y añadiendo piezas a tu arquitectura actual (`Orchestrator`, `PersonalityEngine`, etc.).

#### **Fase 1: Análisis de Entrada Multi-Capa (El "Diagnóstico del Usuario")**

El objetivo es entender el prompt del usuario en múltiples niveles antes de actuar. Esto se hace en tu `PersonalityEngine`, pero lo vamos a hacer mucho más potente.

**Paso 1.1: Mejorar el `PersonalityEngine` para un Análisis Híbrido**

Modifica tu `personality_engine.py`. La idea es no depender solo de un modelo pesado, sino usar una cascada de análisis, de lo más rápido a lo más lento.

```python
# En: chimera_core/personality_engine.py

from transformers import pipeline
import re # Usaremos expresiones regulares para heurísticas rápidas

class PersonalityEngine:
    def __init__(self):
        print("PersonalityEngine: Cargando modelo de clasificación Zero-Shot...")
        # Usa un modelo destilado, más rápido que el "large". Es un buen compromiso.
        self.intent_classifier = pipeline(
            "zero-shot-classification",
            model="valhalla/distilbart-mnli-12-3" 
        )
        print("PersonalityEngine: Modelo cargado.")
        
    def analyze_user_input(self, prompt: str) -> dict:
        """
        Realiza un análisis multi-capa del prompt y devuelve un diccionario de directivas.
        """
        directives = {}
        prompt_lower = prompt.lower()

        # --- Capa 1: Heurísticas Rápidas (Análisis Instantáneo) ---
        if re.search(r'\b(jaja|jeje|lol|lmao|😂)\b', prompt_lower):
            directives['humor_detected'] = True
        if '?' not in prompt:
            directives['statement_type'] = "declaración"
        else:
            directives['statement_type'] = "pregunta"
        if len(prompt.split()) < 5:
            directives['length'] = "corto y directo"

        # --- Capa 2: Análisis de Intención (Si es necesario) ---
        # Solo ejecutamos el modelo pesado si no tenemos suficientes pistas.
        if 'humor_detected' not in directives:
            candidate_labels = ['broma', 'sarcasmo', 'pregunta seria', 'frustración', 'petición de ayuda']
            analysis = self.intent_classifier(prompt, candidate_labels)
            intent = analysis['labels'][0]
            score = analysis['scores'][0]
            if score > 0.65: # Solo confiamos en clasificaciones con alta seguridad
                directives['detected_intent'] = intent
        
        print(f"PersonalityEngine: Directivas generadas -> {directives}")
        return directives

```

#### **Fase 2: Construcción de Contexto Dinámico (El "Guion para el Actor")**

El `Orchestrator` es el director. Su trabajo es tomar el diagnóstico del `PersonalityEngine` y escribir un "guion" (el System Prompt) a medida para el LLM.

**Paso 2.1: Crear un "Traductor de Directivas"**

Dentro de tu `orchestrator.py`, crea una función de ayuda que traduzca el diccionario de directivas en texto legible para el LLM.

**Paso 2.2: Modificar el `Orchestrator` para Usar la Nueva Lógica**

Reemplaza tu `orchestrator.py` con esta versión avanzada.

```python
# En: orchestrator.py

# ... (tus otras importaciones)
from chimera_core.personality_engine import PersonalityEngine

class Orchestrator:
    def __init__(self):
        # ... (tus otras inicializaciones)
        self.personality_engine = PersonalityEngine()
        # ...

    # --- [NUEVO] Función de ayuda para traducir directivas ---
    def _translate_directives_to_prompt(self, directives: dict) -> str:
        """
        Convierte el diccionario de análisis de personalidad en instrucciones
        de texto claras para el LLM.
        """
        instructions = []
        # Lógica de traducción
        if directives.get('humor_detected'):
            instructions.append("El usuario está bromeando o de buen humor. Adopta un tono ligero, conversacional y siéntete libre de responder con humor.")
        
        elif directives.get('detected_intent') == 'frustración':
            instructions.append("El usuario está frustrado. Prioriza la empatía y la resolución directa del problema. Evita la charla innecesaria.")
            
        elif directives.get('detected_intent') == 'pregunta seria':
            instructions.append("El usuario tiene una pregunta seria. Sé preciso, estructurado y céntrate en la exactitud.")

        if directives.get('length') == 'corto y directo':
            instructions.append("El usuario es conciso, así que valora las respuestas breves y directas.")

        if not instructions:
            return "Mantén tu personalidad estándar: servicial, amigable y con memoria."
            
        return " ".join(instructions)

    def process_prompt(self, session_id: str, prompt: str) -> str:
        """
        Orquesta todo el flujo con análisis de personalidad multi-capa.
        """
        
        # --- FASE 1: ANÁLISIS ---
        personality_directives_dict = self.personality_engine.analyze_user_input(prompt)
        
        # --- FASE 2: RECUPERACIÓN DE MEMORIA ---
        # (Esta parte no cambia, sigues llamando a tu ContextEngine para
        #  recuperar de Redis, ChromaDB y Neo4j)
        short_term_memory = self.context_engine.get_short_term_memory(session_id)
        # ... etc

        # --- FASE 3: CONSTRUCCIÓN DEL CONTEXTO DINÁMICO ---
        
        # 3.1 Traducir el diccionario de análisis a una instrucción de texto.
        personality_instruction = self._translate_directives_to_prompt(personality_directives_dict)
        
        # 3.2 Definir la personalidad base.
        base_system_prompt = "Eres Quimera, un asistente de IA avanzado."
        
        # 3.3 Ensamblar el Mensaje de Sistema final.
        final_system_content = f"""{base_system_prompt}

        ### Guía de Comportamiento para ESTA respuesta ###
        {personality_instruction}

        ### Contexto de Conversaciones Pasadas ###
        {associative_memory} 
        {structural_memory}
        """

        # 3.4 Construir la lista de mensajes.
        messages = [
            {"role": "system", "content": final_system_content.strip()},
            *short_term_memory,
            {"role": "user", "content": prompt}
        ]

        # --- FASE 4: LLAMADA Y PERSISTENCIA ---
        
        # (Esta parte no cambia)
        response_text = self.api_manager.get_response(messages)
        self.context_engine.save_turn(session_id, prompt, response_text)

        return response_text
```

#### **Fase 3: La Persistencia del Tono (La Memoria de la Personalidad)**

El sistema anterior reacciona al *prompt actual*. Para que sea verdaderamente adaptativo, debe recordar el **tono general de la sesión**.

**Paso 3.1: Almacenar el Tono en la Memoria Rápida (Redis)**

Después de cada análisis en el `Orchestrator`, guarda el "sentimiento" general en Redis, con un tiempo de expiración (ej. 15 minutos).

```python
# En orchestrator.py, al final de process_prompt

# ... después de obtener la respuesta
detected_intent = personality_directives_dict.get('detected_intent', 'neutral')
# Suponiendo que tienes un self.redis_client
self.redis_client.set(f"session:{session_id}:tone", detected_intent, ex=900) 
```

**Paso 3.2: Usar el Tono Persistente en el Análisis**

En el `Orchestrator`, antes de construir el prompt, recupera el tono guardado.

```python
# En orchestrator.py, al principio de process_prompt

# Recuperar el tono general de la sesión
session_tone = self.redis_client.get(f"session:{session_id}:tone")
if session_tone:
    personality_directives_dict['overall_tone'] = session_tone.decode('utf-8')

# Luego, en _translate_directives_to_prompt, puedes añadir lógica como:
# if directives.get('overall_tone') == 'frustración':
#     instructions.append("Recuerda que el usuario ha estado frustrado recientemente, así que mantén la empatía.")
```

### **Resumen para Ti**

Para que tu Quimera sea completamente adaptativo:

1.  **Potencia tu `PersonalityEngine`** para que use una cascada de análisis (reglas rápidas primero, modelo de IA pesado después) y devuelva un diccionario de "directivas" en lugar de un solo string.
2.  **Convierte tu `Orchestrator` en un verdadero director:**
    *   Crea una función `_translate_directives_to_prompt` que convierta ese diccionario en un párrafo de instrucciones claras para el LLM.
    *   Inyecta estas instrucciones en una sección dedicada `### Guía de Comportamiento ###` dentro del Mensaje de Sistema.
3.  **Dale memoria a la personalidad:** Usa Redis (tu memoria a corto plazo) para almacenar el "tono" dominante de la sesión, de modo que el asistente pueda recordar si has estado bromeando o frustrado en los últimos minutos, y ajustar su comportamiento de base en consecuencia.

Esta arquitectura es robusta, escalable y replica los principios de los sistemas de producción. Es un desafío, pero es el camino para cumplir la visión de tu proyecto.