<div align="center">
  <!-- ICONO SVG INCRUSTADO Y COLOREADO -->
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="150" fill="#3399FF">
    <path d="M142.9 22.3c-4.4-10.3-18.3-13.3-28.6-8.9s-13.3 18.3-8.9 28.6l15.3 35.8-39.6 28.4c-10.1 7.2-13.6 20.3-8.5 31.3l15.3 33.3-39.7 13.2c-11 3.7-17.8 15.1-16.4 26.9l5.4 45.3-34.4 3.8c-11.4 .6-20.9 9.5-21.5 20.9l-2.4 46.1c-1.3 25.1 18.2 46.4 43.2 46.4l2.4 0 50.3-4.4c10.5-.9 18.7-9.9 17.8-20.4l-3.3-38.3 22.1-13.3c10.3-6.2 13.9-19.1 8.6-29.9l-12.6-25.9 30.3-15.1c10.7-5.4 23.3-1.3 28.6 9.4l15.3 30.6 33.1 3.7c11.3 1.3 21.6-6.1 24.9-16.9l13.2-43.2 43.2-13.2c10.8-3.3 18.1-12.9 18.1-24.3l0-43.2 13.2-43.2c3.3-10.8-4.1-21.6-14.9-24.9l-43.2-13.2-3.7-33.1c-1.3-11.3-10.6-20.2-21.9-20.2l-30.6-15.3c-10.7-5.4-23.3-1.3-28.6 9.4l-15.1 30.3 25.9 12.6c10.8 5.3 19.9-1.5 19.9-13.9l13.3-22.1-38.3-3.3c-10.5-.9-18.7-9.9-17.8-20.4l4.4-50.3 0-2.4c0-25-21.4-44.5-46.4-43.2l-46.1 2.4c-11.4 .6-20.3 10.1-20.9 21.5l-3.8 34.4 45.3 5.4c11.8 1.4 21.2 10.7 23.1 22.5l13.2 39.7 33.3 15.3c11 5.1 24.1 1.6 29.3-9.5l28.4-39.6-35.8-15.3zM256 320a64 64 0 1 1 0-128 64 64 0 1 1 0 128z"/>
  </svg>
  <h1 align="center">
    Proyecto Quimera: Exo-Córtex Conversacional
  </h1>
  <p align="center">
    <strong>Una implementación avanzada de un sistema RAG (Retrieval-Augmented Generation) con memoria híbrida, orquestación inteligente y capacidades agenticas.</strong>
  </p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PySide6-24912A?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/ChromaDB-6E44FF?style=for-the-badge" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B9?style=for-the-badge&logo=google-gemini&logoColor=white" alt="Google Gemini">
</p>

---

## 🎯 Visión del Proyecto

El **Proyecto Quimera** es un asistente de IA diseñado para funcionar como un "exo-córtex": un cerebro externo que aumenta las capacidades del usuario ("Arkitekto"). A diferencia de los chatbots simples, Quimera está diseñado para comprender el contexto profundo (tono, emoción, intención) y utilizar un sistema de memoria complejo para mantener conversaciones coherentes, personalizadas y extensibles a largo plazo.

---

## ✨ Características de Vanguardia

-   🧠 **Motor de Personalidad:** Analiza el prompt del usuario para detectar tono, emoción y estilo, generando directivas que adaptan la personalidad del LLM en tiempo real.
-   💾 **Arquitectura de Memoria Híbrida:** Un sistema de memoria multi-capa para un contexto enriquecido y persistente.
    -   **Redis:** Memoria a corto plazo de alta velocidad para el flujo conversacional inmediato.
    -   **ChromaDB:** Memoria semántica a largo plazo para la recuperación de "recuerdos" relevantes.
    -   **SQLite:** Memoria a medio plazo que almacena resúmenes de sesiones para una contextualización eficiente.
    -   **Neo4j:** Memoria estructural (grafo de conocimiento) para entender relaciones complejas entre entidades.
-   ⚡ **Orquestación Inteligente y Síntesis de Contexto:** Utiliza un LLM secundario (ej. GPT-3.5) para sintetizar la información recuperada de todas las memorias en un contexto cohesivo, antes de enviarlo al LLM principal (ej. GPT-4o-mini). Esto optimiza la calidad de la respuesta y los costes.
-   🧩 **Sistema de Plugins Agentico (MCP):** Permite al LLM invocar herramientas externas (ej. gestión de archivos, búsquedas web) para realizar acciones, transformando a Quimera en un agente capaz de interactuar con su entorno.
-   ☁️ **Integración Multi-Proveedor de LLM:** Soporte para múltiples proveedores (OpenAI, Gemini) a través de una interfaz unificada, permitiendo cambiar de modelo dinámicamente.

<div align="center">
  <br/>
  <img src="https://github.com/SRdeMora/Ingenieria-de-Contexto/blob/main/asset/git.gif" alt="Demo de Quimera UI en acción"/><!-- AÑADE AQUÍ UN GIF DE DEMOSTRACIÓN DE LA UI -->
  <img src= alt="Demo de Quimera UI en acción"/>
  <p><em>Demostración de la interfaz de usuario de Quimera.</em></p>
</div>

---

## 💡 Relevancia y Demostración de Habilidades

Este repositorio demuestra la capacidad de diseñar y construir un sistema de IA complejo que va más allá de simples llamadas a una API.

<details>
  <summary><strong>Conceptos de IA Avanzados Demostrados</strong></summary>
  <br/>
  <ul>
    <li><strong>Retrieval-Augmented Generation (RAG):</strong> Implementación de un sistema RAG sofisticado con múltiples fuentes de conocimiento.</li>
    <li><strong>Sistemas Agenticos:</strong> El núcleo del proyecto es un agente de IA que puede razonar y utilizar herramientas (plugins).</li>
    <li><strong>Optimización de LLMs:</strong> El uso de un modelo para sintetizar contexto demuestra una comprensión avanzada de cómo optimizar el rendimiento y los costes en aplicaciones de LLM.</li>
    <li><strong>Gestión de Estado y Memoria a Largo Plazo:</strong> Aborda uno de los mayores desafíos en la IA conversacional.</li>
  </ul>
</details>

<details>
  <summary><strong>Prácticas de Ingeniería de Software Profesional</strong></summary>
  <br/>
  <ul>
    <li><strong>Arquitectura Modular y Desacoplada:</strong> Clara separación entre el core, la UI, los plugins y los proveedores.</li>
    <li><strong>Logging Robusto y Trazabilidad:</strong> El sistema de logging con Trace IDs y datos estructurados es crucial para la depuración y el mantenimiento en entornos de producción.</li>
    <li><strong>Gestión de Dependencias y Entornos:</strong> Uso correcto de <code>venv</code> y <code>requirements.txt</code> para la reproducibilidad.</li>
    <li><strong>Documentación Clara:</strong> Un README bien estructurado que explica tanto el "qué" como el "porqué" del proyecto.</li>
  </ul>
</details>

---

## 🏗️ Estructura del Proyecto

```plaintext
📂 chimera_project/
├── ⚙️ .env                  # Claves API y configuraciones
├── 📜 requirements.txt      # Dependencias de Python
│
├── 🧠 chimera_core/         # Cerebro del sistema (API con FastAPI)
│   ├── 🐍 main.py           # Punto de entrada de la API
│   ├── 🐍 orchestrator.py   # Coordina todos los módulos
│   ├── 🐍 context_engine.py # Construye el contexto para el LLM
│   ├── 💾 memory/           # Módulos de gestión de memoria
│   ├── 🔬 meta/             # Análisis de metadatos (personalidad, tono)
│   ├── 🧩 plugins/          # Herramientas extensibles para el LLM
│   └── ☁️ providers/        # Integraciones con proveedores de LLM
│
├── 🖥️ chimera_ui/           # Frontend de la aplicación (UI con PySide6)
│   ├── 🐍 main.py           # Punto de entrada de la UI
│   ├── 🐍 api_client.py     # Cliente para conectar con el backend
│   └── 🎨 ui/               # Componentes de la interfaz
│
├── 📚 _docs/                # Documentación y assets
├── 🗄️ chroma_data/          # Datos persistentes de ChromaDB
├── 🛠️ setup/                # Scripts de utilidad
└── 🌐 venv/                 # Entorno virtual de Python
```
<div align="center">
  <strong>¡Bienvenido al Proyecto Quimera, Arkitekto!</strong>
</div>
<!-- SECCIÓN DE GUÍA DE USO EN HTML CON DESPLEGABLES -->
<div>
  <h3>🚀 Guía de Instalación y Uso</h3>
  <details>
    <summary><strong>Paso 1: Requisitos Previos</strong></summary>
    <br/>
    <ul>
      <li>Python 3.10 o superior.</li>
      <li>Servidores de Redis y/o Neo4j en ejecución (si se van a utilizar).</li>
    </ul>
  </details>
  <details>
    <summary><strong>Paso 2: Clonar e Instalar</strong></summary>
    <br/>
    <p>Clona el repositorio:</p>
    <pre><code>git clone https://github.com/tu_usuario/chimera_project.git
cd chimera_project</code></pre>
    <p>Crea y activa el entorno virtual:</p>
    <pre><code>python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # macOS/Linux</code></pre>
    <p>Instala las dependencias:</p>
    <pre><code>pip install -r requirements.txt</code></pre>
  </details>
  <details>
    <summary><strong>Paso 3: Configurar Variables de Entorno (`.env`)</strong></summary>
    <br/>
    <p>Crea un archivo <code>.env</code> en la raíz del proyecto y añade tus claves API y configuraciones.</p>
    <pre><code># Claves API para Proveedores de LLM
OPENAI_API_KEY="tu_clave_api_openai_aqui"
GOOGLE_API_KEY="tu_clave_api_gemini_aqui"

# Configuración de Redis
REDIS_HOST="localhost"
REDIS_PORT=6379

# Configuración de Neo4j (Opcional)
# NEO4J_URI="bolt://localhost:7687"
# NEO4J_USER="neo4j"
# NEO4J_PASSWORD="tu_contraseña_neo4j"</code></pre>
  </details>
  <details>
    <summary><strong>Paso 4: Ejecución</strong></summary>
    <br/>
    <p><strong>IMPORTANTE:</strong> Debes tener <strong>dos terminales abiertas</strong> con el entorno virtual activado.</p>
    <p><strong>Terminal 1: Iniciar el Backend (Core)</strong></p>
    <pre><code>python chimera_core/main.py</code></pre>
    <p><strong>Terminal 2: Iniciar el Frontend (UI)</strong></p>
    <pre><code>python chimera_ui/main.py</code></pre>
  </details>
</div>

---

## 🧩 Extensibilidad y Contribución

El diseño modular de Quimera facilita la adición de nuevas capacidades.

-   **Añadir Nuevos Proveedores de LLM:** Crea una nueva clase en `chimera_core/providers/` que herede de `BaseProvider`. El `ApiManager` lo descubrirá automáticamente.
-   **Crear Nuevos Plugins (Herramientas):** Crea una nueva clase en `chimera_core/plugins/` que herede de `MCPPlugin` y define sus `ToolSignature`. El `PluginManager` lo cargará al iniciar.

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

<div align="center">
  <strong>¡Bienvenido al Proyecto Quimera, Arkitekto!</strong>
</div>
