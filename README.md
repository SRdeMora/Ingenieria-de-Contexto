<div align="center">
  <img src="./_docs/logo_quimera.png" alt="Logo de Quimera" width="150"/>
  <h1 align="center">
    Proyecto Quimera: Exo-Córtex Conversacional
  </h1>
  <p align="center">
    <strong>Un sistema de IA conversacional avanzado, diseñado para actuar como un "exo-córtex" adaptable, contextual y extensible para el usuario.</strong>
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

## 📜 Descripción del Proyecto

El **Proyecto Quimera** es un asistente de inteligencia artificial conversacional diseñado para funcionar como un "exo-córtex" para el usuario (denominado "Arkitekto"). Su objetivo es comprender el tono, la emoción, la intención y el estilo del usuario para adaptar dinámicamente sus respuestas, ofreciendo una experiencia profundamente personalizada a través de una arquitectura modular de LLMs, sistemas de memoria y plugins extensibles.

---

## ✨ Características Principales

-   ✅ **Adaptabilidad de Personalidad:** Analiza el prompt del usuario para ajustar la respuesta del LLM en tono, emoción y formalidad.
-   ✅ **Gestión de Sesiones Persistentes:** Mantiene el contexto a través de las conversaciones para una interacción coherente.
-   ✅ **Memoria Híbrida Avanzada:** Combina Redis (corto plazo), ChromaDB (largo plazo semántico), SQLite (resúmenes) y Neo4j (estructural) para un contexto enriquecido.
-   ✅ **Integración Flexible de LLM:** Soporte para múltiples proveedores (OpenAI, Gemini) a través de una interfaz unificada.
-   ✅ **Sistema de Plugins (MCP):** Extiende las capacidades de Quimera con herramientas que el LLM puede invocar para realizar acciones (ej. búsquedas web, gestión de archivos).
-   ✅ **Interfaz de Usuario de Escritorio:** Una aplicación intuitiva en PySide6 para interactuar con el sistema.
-   ✅ **Backend API Robusto:** Un servicio en FastAPI que expone toda la lógica central de Quimera.

---

## 🏗️ Arquitectura del Sistema

Quimera sigue una arquitectura de microservicios lógicos, dividida en un **Backend (Core)** y una **UI (Frontend)** que se comunican vía API REST, integrándose con múltiples sistemas de memoria y servicios externos.



<!-- SECCIÓN DE STACK TECNOLÓGICO EN HTML -->
<div align="left">
  <h3>🛠️ Stack Tecnológico</h3>
  <ul>
    <li><strong>Lenguaje:</strong> Python 3.10+</li>
    <li><strong>Backend:</strong> FastAPI, Uvicorn</li>
    <li><strong>Frontend:</strong> PySide6</li>
    <li><strong>Bases de Datos de Memoria:</strong> Redis, SQLite, ChromaDB, Neo4j (Opcional)</li>
    <li><strong>Proveedores LLM:</strong> OpenAI, Google Gemini</li>
    <li><strong>NLP (Análisis de Personalidad):</strong> Hugging Face Transformers</li>
    <li><strong>Renderizado UI:</strong> Markdown-it-py, Pygments</li>
  </ul>
</div>

---

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
