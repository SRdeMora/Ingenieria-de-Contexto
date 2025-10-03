
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QTextEdit, QVBoxLayout, QPushButton, QInputDialog, QListWidgetItem, QMessageBox, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

from .settings_dialog import SettingsDialog
from ..api_client import ApiClient

class PromptInputWidget(QTextEdit):
    prompt_submitted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.prompt_submitted.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quimera Exo-Córtex v1.3")
        self.setGeometry(100, 100, 1600, 900)

        # Inicialización de componentes clave
        self.api_client = ApiClient(self)
        self.active_session_id = None
        self.thinking_message_cursor = None # Para gestionar el mensaje "Pensando..."
        self.llm_settings = {
            "provider_name": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 1024
        }
        self.md = MarkdownIt("gfm-like", options_update={'highlight': self.highlight_code}).enable("table")

        # Configuración del widget central y el layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Creación y adición de los paneles principales
        session_panel = self._create_session_panel()
        chat_panel = self._create_chat_panel()

        main_layout.addWidget(session_panel, 1)
        main_layout.addWidget(chat_panel, 3)

        # Carga inicial de datos
        self.load_sessions()

    def _create_session_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMaximumWidth(280) # Ancho máximo reducido
        layout = QVBoxLayout(panel)

        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("font-size: 11pt;") # Letra más grande
        self.new_session_button = QPushButton("Nueva Sesión")
        self.settings_button = QPushButton("Configuración")

        layout.addWidget(self.new_session_button)
        layout.addWidget(self.sessions_list)
        layout.addWidget(self.settings_button)

        self.sessions_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self.show_session_context_menu)
        self.new_session_button.clicked.connect(self.handle_new_session)
        self.sessions_list.currentItemChanged.connect(self.handle_session_changed)
        self.settings_button.clicked.connect(self.open_settings_dialog)

        return panel

    def _create_chat_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setPlaceholderText("Selecciona o crea una sesión para comenzar.")
        self.chat_view.setStyleSheet("""
            QTextEdit { font-family: sans-serif; font-size: 12pt; }
            pre, code { font-family: monospace; font-size: 11pt; }
            pre { background-color: #f0f0f0; padding: 10px; border-radius: 5px; display: block; white-space: pre-wrap; }
        """)

        self.prompt_input = PromptInputWidget()
        self.prompt_input.setFixedHeight(120)
        self.prompt_input.setPlaceholderText("Escribe tu prompt... (Enter para enviar, Shift+Enter para nueva línea)")
        # Aumentamos el tamaño de la fuente del área de entrada
        self.prompt_input.setStyleSheet("font-family: sans-serif; font-size: 12pt;")

        self.send_button = QPushButton("Enviar Prompt")

        layout.addWidget(self.chat_view)
        layout.addWidget(self.prompt_input)
        layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.handle_send_prompt)
        self.prompt_input.prompt_submitted.connect(self.handle_send_prompt)

        return panel

        # Configuración inicial del LLM
        self.llm_settings = {
            "provider_name": "openai",
            "model_name": "gpt-4o-mini", # Modelo por defecto
            "temperature": 0.7,
            "max_output_tokens": 800
        }

        # Cargar las sesiones existentes al iniciar
        self.load_sessions()

    def highlight_code(self, code, lang, attrs):
        """
        Función de resaltado que se pasa a MarkdownIt.
        Usa Pygments para colorear el bloque de código.
        """
        try:
            # Intenta obtener el lexer por el nombre del lenguaje (ej. 'python')
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            try:
                # Si no se encuentra, intenta adivinar el lenguaje
                lexer = guess_lexer(code)
            except:
                # Si todo falla, devuelve el código sin resaltar
                return f'<pre><code>{code}</code></pre>'
        
        # Usamos el formateador de HTML de Pygments. `noclasses=True` incrusta los estilos
        # directamente en los tags, lo que es más robusto para QTextEdit.
        formatter = HtmlFormatter(style='monokai', noclasses=True)
        return highlight(code, lexer, formatter)

    def load_sessions(self):
        """Llama al API client para obtener y mostrar la lista de sesiones."""
        self.sessions_list.clear()
        self.api_client.get_sessions(self.on_sessions_received, self.on_api_error)

    def on_sessions_received(self, sessions):
        """Slot para manejar la lista de sesiones recibida del backend."""
        for session in sessions:
            item = QListWidgetItem(session['session_name'])
            item.setData(Qt.UserRole, session['session_id']) # Guardar el ID en el item
            self.sessions_list.addItem(item)

        # Si la lista no está vacía, seleccionar el primer elemento por defecto.
        # Esto asegura que siempre haya una sesión activa si existe alguna.
        if self.sessions_list.count() > 0 and self.sessions_list.currentRow() == -1:
            self.sessions_list.setCurrentRow(0)

    def handle_new_session(self):
        """Maneja la creación de una nueva sesión."""
        text, ok = QInputDialog.getText(self, 'Nueva Sesión', 'Nombre de la nueva sesión:')
        if ok and text:
            self.api_client.create_session(text, self.on_session_created, self.on_api_error)

    def on_session_created(self, new_session):
        """
        Slot para manejar la respuesta de una sesión recién creada.
        Añade el nuevo item a la lista y lo selecciona.
        """
        item = QListWidgetItem(new_session['session_name'])
        item.setData(Qt.UserRole, new_session['session_id'])
        self.sessions_list.addItem(item)
        self.sessions_list.setCurrentItem(item) # Seleccionar la nueva sesión

    def handle_session_changed(self, current, previous):
        """Maneja el cambio de selección en la lista de sesiones."""
        if current is not None:
            self.active_session_id = current.data(Qt.UserRole)
            print(f"Cambiando a la sesión: {self.active_session_id}")
            self.chat_view.clear()
            # TODO: Aquí llamaríamos al backend para obtener el historial de esta sesión
            self.chat_view.setPlaceholderText(f"Historial de la sesión: {current.text()}")
        else:
            self.active_session_id = None

    def show_session_context_menu(self, position):
        """Muestra el menú contextual para un item de la lista de sesiones."""
        item = self.sessions_list.itemAt(position)
        if not item:
            return

        menu = QMenu()
        delete_action = menu.addAction("Eliminar Sesión")
        
        action = menu.exec(self.sessions_list.mapToGlobal(position))
        
        if action == delete_action:
            self.handle_delete_session(item)

    def handle_delete_session(self, item):
        """Maneja la lógica de confirmación y borrado de una sesión."""
        session_id = item.data(Qt.UserRole)
        session_name = item.text()

        reply = QMessageBox.question(self, 'Confirmar Borrado',
                                       f"¿Estás seguro de que quieres eliminar permanentemente la sesión '{session_name}' y todo su historial?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.api_client.delete_session(session_id, self.on_session_deleted, self.on_api_error)

    def on_session_deleted(self, session_id):
        """Slot que se ejecuta cuando una sesión ha sido borrada exitosamente."""
        # Simplemente recargamos la lista para que desaparezca la sesión eliminada
        print(f"Sesión {session_id} eliminada exitosamente.")
        self.load_sessions()

    def open_settings_dialog(self):
        """
        Abre el diálogo de configuración de LLM.
        """
        dialog = SettingsDialog(self.api_client, self.llm_settings, self)
        dialog.settings_accepted.connect(self.on_settings_accepted)
        dialog.exec()

    def on_settings_accepted(self, provider_name: str, model_name: str, temperature: float, max_tokens: int):
        """
        Slot para manejar la configuración aceptada desde el diálogo.
        """
        self.llm_settings["provider_name"] = provider_name
        self.llm_settings["model_name"] = model_name
        self.llm_settings["temperature"] = temperature
        self.llm_settings["max_tokens"] = max_tokens
        print(f"Configuración de LLM actualizada: {self.llm_settings}")

    def handle_send_prompt(self):
        """
        Se activa cuando el usuario presiona el botón de Enviar.
        """
        if not self.active_session_id:
            QMessageBox.warning(self, "No hay sesión activa", "Por favor, selecciona una sesión o crea una nueva antes de enviar un mensaje.")
            return

        user_prompt = self.prompt_input.toPlainText().strip()
        if user_prompt:
            # Añadir el prompt del usuario a la vista de chat
            self.chat_view.append(f"<b>Arkitekto:</b> {user_prompt}")
            self.prompt_input.clear()

            # Usar el ApiClient para enviar el prompt al backend de forma asíncrona
            # con el ID de la sesión activa.
            self.api_client.send_prompt(
                session_id=self.active_session_id,
                prompt=user_prompt,
                llm_settings=self.llm_settings,
                on_success=self.on_response_received,
                on_error=self.on_api_error
            )

            # Mostrar un estado de "pensando" inmediatamente en la UI
            self.add_bot_response("<i>Pensando...</i>")
            self.thinking_message_cursor = self.chat_view.textCursor()

    def on_response_received(self, response_data: dict):
        """
        Slot que se ejecuta cuando el ApiClient emite la señal `response_received`.
        Este método se ejecuta en el hilo principal de la GUI.
        """
        # Reemplazamos el mensaje "Pensando..." con la respuesta real.
        # La forma más robusta es deshacer la adición del texto "Pensando..."
        # y luego añadir la nueva respuesta.
        if self.thinking_message_cursor:
            self.thinking_message_cursor.select(QTextCursor.BlockUnderCursor)
            self.thinking_message_cursor.removeSelectedText()
            self.thinking_message_cursor = None # Resetear el cursor

        self.add_bot_response(response_data.get('response_text', 'Error: Respuesta sin texto.'))
        self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())

    def on_api_error(self, error_message: str):
        """
        Slot que se ejecuta cuando el ApiClient emite la señal `error_occurred`.
        Este método se ejecuta en el hilo principal de la GUI.
        """
        self.chat_view.undo()
        self.add_bot_response(f"<font color='red'>Error: {error_message}</font>")

    def add_bot_response(self, markdown_text: str):
        """
        Renderiza el texto Markdown a HTML y lo añade a la vista de chat.
        """
        # Reemplazar el texto plano de "pensando" por HTML para consistencia
        if markdown_text == "<i>Pensando...</i>":
            html_text = markdown_text
        else:
            html_text = self.md.render(markdown_text)
        
        self.chat_view.append(f"<b>Quimera:</b><br>{html_text}")
