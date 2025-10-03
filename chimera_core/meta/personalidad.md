De acuerdo. Un gran proyecto merece un gran `README.md`. Este documento no es solo una guía, es el manifiesto de tu proyecto, diseñado para impresionar y para que cualquiera (incluido tu futuro yo) entienda la brillantez y complejidad de Quimera.

Aquí tienes el `README.md` perfecto. Copia y pega esto en el archivo `README.md` en la raíz de tu proyecto.

---

# Quimera - Un Exo-Córtex Simbiótico

**Quimera** no es un chatbot. Es un prototipo de **exo-córtex simbiótico**: una extensión de la mente del usuario, diseñada para recordar, razonar y adaptarse. Su arquitectura multi-capa de memoria y su motor de personalidad dinámico le permiten mantener conversaciones coherentes, contextuales y, lo más importante, genuinamente adaptativas.

Este proyecto explora la vanguardia de la ingeniería de sistemas de IA conversacional, implementando una arquitectura modular que separa la memoria, la lógica y la personalidad para crear un asistente verdaderamente inteligente.

## 📜 Manifiesto: La Conversación como un Organismo Vivo

La premisa fundamental de Quimera es que las conversaciones no son secuencias lineales de texto, sino redes vivientes de conceptos, intenciones y relaciones. Una memoria simple (como un archivo de log) captura el *qué*, pero fracasa en capturar el *cómo* y el *porqué*.

Quimera está diseñado para superar esta limitación a través de una arquitectura de memoria híbrida y un sistema de personalidad que analiza el subtexto de la conversación, permitiendo al asistente no solo responder, sino reaccionar.

## 🏛️ Arquitectura: El Sistema de Memoria Multi-Capa

Quimera se fundamenta en un sistema de memoria compuesto por cuatro capas distintas, cada una con una función específica, que trabajan en conjunto bajo la dirección de un orquestador central.

---

### **Capa 1: Memoria a Corto Plazo (El Sistema Nervioso)**
*   **Tecnología:** **Redis**
*   **Función:** Almacena el historial inmediato de la conversación (últimos N turnos) y el **tono emocional de la sesión**. Es una memoria de trabajo ultrarrápida que vive en RAM, garantizando una recuperación de contexto instantánea. Responde a la pregunta: *“¿De qué estamos hablando ahora mismo?”*.

---

### **Capa 2: Memoria Asociativa (El Inconsciente Semántico)**
*   **Tecnología:** **ChromaDB** (u otra base de datos vectorial)
*   **Función:** Es el corazón de la memoria a largo plazo. Cada mensaje se convierte en un vector numérico (embedding) y se almacena. Permite realizar búsquedas de similitud semántica para encontrar conceptos y conversaciones pasadas que son temáticamente relevantes al prompt actual. Responde a la pregunta: *“¿Hemos hablado de algo parecido a esto antes, aunque fuera hace mucho tiempo?”*.

---

### **Capa 3: Memoria Estructural (El Palacio de la Memoria)**
*   **Tecnología:** **Neo4j** (Base de Datos de Grafos)
*   **Función:** Es la capa más sofisticada y la que da a Quimera su poder contextual único. Modela la conversación como un grafo, conectando mensajes con relaciones `[:NEXT]`. Esto permite reconstruir el flujo narrativo exacto alrededor de un recuerdo recuperado. Responde a la pregunta: *“Recuerdo que hablamos de 'Pangolin'. ¿Qué se dijo exactamente antes y después de eso?”*.

---

### **Capa 4: Memoria Narrativa (El Cronista)**
*   **Tecnología:** **SQLite**
*   **Función:** *(Actualmente desactivada por optimización de costes)*. Diseñada para generar y almacenar resúmenes periódicos de las conversaciones. Actuaría como un cronista que escribe el "diario" de la relación entre el usuario y Quimera, permitiendo una memoria a muy largo plazo sin necesidad de procesar conversaciones enteras. Responde a la pregunta: *“¿Cuál fue el tema principal de nuestra conversación la semana pasada?”*.

## 🧠 El Módulo Adaptativo: `PersonalityEngine`

Esta es la pieza que da vida a Quimera. El `PersonalityEngine` es un módulo de análisis de entrada que dota al asistente de inteligencia emocional.

### Funcionamiento:
1.  **Análisis Híbrido:** Utiliza una cascada de técnicas. Primero, **heurísticas rápidas** (expresiones regulares) para detectar instantáneamente patrones obvios como risas o preguntas.
2.  **Clasificación de Intención:** Si las heurísticas no son suficientes, utiliza un **modelo de clasificación Zero-Shot** (ej. `valhalla/distilbart-mnli-12-3`) para analizar el prompt y etiquetarlo con una intención más profunda (ej. `broma`, `frustración`, `pregunta técnica`).
3.  **Generación de Directivas:** El motor no solo detecta el tono, sino que lo traduce en un **diccionario de directivas de comportamiento** (`{'humor_detected': True, 'length': 'corto'}`).

##  orchestrator.py: El Director de la Orquesta

El `Orchestrator` es el cerebro lógico que une todo. Para cada prompt del usuario, sigue un sofisticado flujo de trabajo:

1.  **Diagnóstico:** Llama al `PersonalityEngine` para obtener un "diagnóstico" de la intención del usuario.
2.  **Recuperación:** Consulta las capas de memoria activas (Redis, ChromaDB, Neo4j) para obtener el historial reciente y los hechos relevantes del pasado.
3.  **Traducción:** Utiliza una función interna para traducir el diccionario de directivas del `PersonalityEngine` en un párrafo de **instrucciones de comportamiento explícitas**.
4.  **Construcción del Contexto:** Ensambla un **Mensaje de Sistema (System Prompt) dinámico y a medida para cada respuesta**. Este prompt se construye en capas:
    *   **Rol Base:** *"Eres Quimera..."*
    *   **Guía de Comportamiento:** Las instrucciones traducidas del `PersonalityEngine` (ej. *"El usuario está frustrado. Prioriza la empatía..."*).
    *   **Contexto de Memoria:** Los hechos recuperados de las bases de datos.
5.  **Llamada al LLM:** Envía este contexto enriquecido al LLM (ej. GPT-4) para generar una respuesta que no solo es correcta, sino también **contextual y emocionalmente alineada**.
6.  **Persistencia:** Guarda el nuevo turno de la conversación en las capas de memoria correspondientes.



## 💡 Conclusión

Quimera es un testimonio de que la verdadera inteligencia artificial conversacional no reside en el modelo de lenguaje por sí solo, sino en la **arquitectura de orquestación** que lo rodea. Es un sistema diseñado para escuchar, recordar y adaptarse, acercándose un paso más al ideal de una IA verdaderamente simbiótica.