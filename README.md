<div align="center">
  <h1 align="center">
    🧠 Proyecto Quimera
  </h1>
  <p align="center">
    <strong>Un sistema de IA conversacional diseñado para actuar como un "exo-córtex" personal, contextual y extensible.</strong>
  </p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PySide6-24912A?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/Uvicorn-009688?style=for-the-badge&logo=python&logoColor=white" alt="Uvicorn">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B9?style=for-the-badge&logo=google-gemini&logoColor=white" alt="Google Gemini">
</p>

---

## 📜 Descripción del Proyecto

El **Proyecto Quimera** es un asistente de inteligencia artificial conversacional avanzado. Su objetivo es funcionar como un "exo-córtex" para el usuario: un cerebro externo que entiende el contexto, la intención y el estilo para ofrecer una experiencia de asistencia verdaderamente personalizada y extensible.

### Arquitectura
El sistema se divide en dos componentes principales que deben ejecutarse de forma independiente:

-   **`chimera_core` (Backend):** El cerebro del sistema. Construido con **FastAPI**, gestiona toda la lógica de la conversación, la memoria a largo y corto plazo, la conexión con los LLMs y la gestión de plugins.
-   **`chimera_ui` (Frontend):** La interfaz de usuario. Una aplicación de escritorio nativa construida con **PySide6** que proporciona una ventana de chat para interactuar con el core.

---

## 🚀 Guía de Instalación

Sigue estos pasos en una terminal para configurar el entorno del proyecto.

### 1. Activar Entorno Virtual
Es crucial usar un entorno virtual. Este proyecto ya incluye uno.
```bash
# Navega a la raíz del proyecto
cd C:\Users\Samuel\Documents\EXPERIMENTO\chimera_project

# Activa el entorno virtual
.\venv\Scripts\activate
