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

```mermaid
graph TD
    subgraph Frontend
        A[Chimera UI (PySide6)] -- "Peticiones HTTP" --> B(API Client)
    end

    subgraph Backend
        B -- "Peticiones HTTP" --> C[Chimera Core API (FastAPI)]
        C -- "Orquestación" --> D[Orchestrator]
        D --> E[PersonalityEngine]
        D --> F[ContextEngine]
        D --> G[ApiManager]
        D --> H[PluginManager]
    end

    subgraph "Memoria y Servicios"
        F -- Historial --> I[Redis]
        F -- Resúmenes --> J[SQLite]
        F -- "Memoria Semántica" --> K[ChromaDB]
        F -- "Grafo Conocimiento" --> L[Neo4j]
        G -- Interacción --> M[Proveedores LLM]
        H -- Acciones --> N[Plugins]
    end
