
import sys
from PySide6.QtWidgets import QApplication

# Importamos la ventana principal desde nuestro paquete de UI
from .ui.main_window import MainWindow

def main():
    """
    Punto de entrada principal para la aplicación de escritorio Quimera.
    """
    # 1. Crear la instancia de QApplication. `sys.argv` permite pasar argumentos
    #    de línea de comandos a la aplicación, si fuera necesario.
    app = QApplication(sys.argv)

    # 2. Crear una instancia de nuestra ventana principal.
    window = MainWindow()

    # 3. Mostrar la ventana.
    window.show()

    # 4. Iniciar el bucle de eventos de la aplicación.
    #    `sys.exit(app.exec())` asegura que la aplicación se cierre limpiamente.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
