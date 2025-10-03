from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSlider, QSpinBox, QPushButton, QFormLayout, QMessageBox
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any, List

from ..api_client import ApiClient

class SettingsDialog(QDialog):
    """
    Diálogo de configuración para los parámetros del LLM y la selección del proveedor.
    Permite al usuario ajustar la temperatura, el modelo, los tokens de salida y
    elegir entre los proveedores de LLM disponibles.
    """
    # Señal que se emite cuando la configuración es aceptada
    settings_accepted = Signal(str, str, float, int) # provider_name, model_name, temperature, max_tokens

    def __init__(self, api_client: ApiClient, current_settings: Dict[str, Any], parent=None):
        """
        Inicializa el diálogo de configuración.

        Args:
            api_client (ApiClient): Instancia del cliente de API para comunicarse con el backend.
            current_settings (Dict[str, Any]): Diccionario con la configuración actual (provider, model, temp, tokens).
            parent (QWidget): Widget padre.
        """
        super().__init__(parent)
        self.setWindowTitle("Configuración de Quimera")
        self.api_client = api_client
        self.current_settings = current_settings

        self.providers: List[str] = []
        self.models: Dict[str, List[str]] = {}

        self._setup_ui()
        self._load_initial_settings()
        self._load_providers_and_models()

    def _setup_ui(self):
        """
        Configura los elementos de la interfaz de usuario del diálogo.
        """
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Selector de Proveedor ---
        self.provider_combo = QComboBox()
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        form_layout.addRow("Proveedor de LLM:", self.provider_combo)

        # --- Selector de Modelo ---
        self.model_combo = QComboBox()
        form_layout.addRow("Modelo de LLM:", self.model_combo)

        # --- Slider de Temperatura ---
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 20) # 0.0 a 2.0 con un paso de 0.1
        self.temperature_slider.setSingleStep(1)
        self.temperature_slider.setTickInterval(1)
        self.temperature_slider.setTickPosition(QSlider.TicksBelow)
        self.temperature_label = QLabel("0.7")
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        self.temperature_slider.valueChanged.connect(lambda value: self.temperature_label.setText(str(value / 10.0)))
        form_layout.addRow("Temperatura:", temp_layout)

        # --- Selector de Max Output Tokens ---
        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(50, 4096) # Rango típico para tokens de salida
        self.max_tokens_spinbox.setSingleStep(50)
        form_layout.addRow("Max Tokens:", self.max_tokens_spinbox)

        main_layout.addLayout(form_layout)

        # --- Botones de Aceptar/Cancelar ---
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Aceptar")
        self.cancel_button = QPushButton("Cancelar")
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.ok_button.clicked.connect(self._on_accept)
        self.cancel_button.clicked.connect(self.reject)

        # --- Botón de Resetear ChromaDB ---
        self.reset_chroma_button = QPushButton("Borrar Memoria Semántica (ChromaDB)")
        self.reset_chroma_button.setStyleSheet("background-color: #ffcccc; color: black;") # Estilo para destacar acción destructiva
        main_layout.addWidget(self.reset_chroma_button)
        self.reset_chroma_button.clicked.connect(self._on_reset_chroma_db)

    def _load_initial_settings(self):
        """
        Carga la configuración actual en los controles de la UI.
        """
        self.temperature_slider.setValue(int(self.current_settings.get("temperature", 0.7) * 10))
        self.max_tokens_spinbox.setValue(self.current_settings.get("max_tokens", 800))

    def _load_providers_and_models(self):
        """
        Obtiene la lista de proveedores y modelos del backend de forma asíncrona.
        """
        self.api_client.get_providers(self._on_providers_received, self._on_error)

    def _on_providers_received(self, providers_data: Dict[str, List[str]]):
        """
        Slot para manejar la lista de proveedores y sus modelos recibida del backend.
        """
        self.providers = list(providers_data.keys())
        self.models = providers_data

        self.provider_combo.clear()
        self.provider_combo.addItems(self.providers)

        # Seleccionar el proveedor actual
        current_provider = self.current_settings.get("provider_name", "openai")
        if current_provider in self.providers:
            self.provider_combo.setCurrentText(current_provider)
        else:
            self.provider_combo.setCurrentIndex(0) # Seleccionar el primero por defecto

    def _on_provider_changed(self, index: int):
        """
        Actualiza la lista de modelos cuando cambia el proveedor seleccionado.
        """
        selected_provider = self.provider_combo.currentText()
        self.model_combo.clear()
        if selected_provider in self.models:
            self.model_combo.addItems(self.models[selected_provider])
            # Seleccionar el modelo actual si coincide con el proveedor
            if self.current_settings.get("provider_name") == selected_provider:
                current_model = self.current_settings.get("model_name")
                if current_model in self.models[selected_provider]:
                    self.model_combo.setCurrentText(current_model)
                else:
                    self.model_combo.setCurrentIndex(0) # Seleccionar el primero por defecto
            else:
                self.model_combo.setCurrentIndex(0) # Seleccionar el primero por defecto

    def _on_error(self, error_message: str):
        """
        Maneja los errores de comunicación con el backend.
        """
        QMessageBox.critical(self, "Error de Comunicación", f"No se pudo conectar con el servidor: {error_message}")

    def _on_accept(self):
        """
        Emite la señal settings_accepted con la configuración seleccionada y cierra el diálogo.
        """
        provider_name = self.provider_combo.currentText()
        model_name = self.model_combo.currentText()
        temperature = self.temperature_slider.value() / 10.0
        max_tokens = self.max_tokens_spinbox.value()
        
        self.settings_accepted.emit(provider_name, model_name, temperature, max_tokens)
        self.accept()

    def _on_reset_chroma_db(self):
        """
        Maneja el clic en el botón de resetear ChromaDB.
        Pide confirmación antes de proceder.
        """
        reply = QMessageBox.question(self, "Confirmar Reseteo",
                                       "¿Estás seguro de que quieres borrar PERMANENTEMENTE toda la memoria semántica (ChromaDB)? Esta acción no se puede deshacer.",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.api_client.reset_chroma_db(self._on_chroma_reset_success, self._on_chroma_reset_error)

    def _on_chroma_reset_success(self, response_data: Dict[str, Any]):
        """
        Maneja la respuesta exitosa del reseteo de ChromaDB.
        """
        QMessageBox.information(self, "Reseteo Completado", response_data.get("message", "Memoria semántica borrada exitosamente."))

    def _on_chroma_reset_error(self, error_message: str):
        """
        Maneja el error durante el reseteo de ChromaDB.
        """
        QMessageBox.critical(self, "Error al Resetear", f"Ocurrió un error al borrar la memoria semántica: {error_message}")

    def get_settings(self) -> Dict[str, Any]:
        """
        Devuelve la configuración seleccionada por el usuario.
        """
        return {
            "provider_name": self.provider_combo.currentText(),
            "model_name": self.model_combo.currentText(),
            "temperature": self.temperature_slider.value() / 10.0,
            "max_tokens": self.max_tokens_spinbox.value()
        }