import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from typing import Dict, Any, List

from .mcp_base import MCPPlugin, ToolSignature

# --- Configuración de Credenciales (desde .env) ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587)) # Puerto estándar para TLS
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # O token de aplicación
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# --- Lista Blanca de Destinatarios (REGEX) ---
# Define aquí los patrones REGEX de las direcciones de correo permitidas.
# Ejemplo: [r".*@tuempresa\.com$", r"jefe@dominio\.com$"]
# Por seguridad, empieza con una lista vacía o muy restrictiva.
ALLOWED_RECIPIENT_PATTERNS = [
    r".*@.*$"
    #r".*@example\.com$", # Permite cualquier dirección en example.com
    #r"tu\.correo@gmail\.com$", # Permite tu correo personal
    #r"rasparecords@gmail\\.com$"
]

class EmailClientPlugin(MCPPlugin):
    """
    Un plugin que permite a Quimera enviar correos electrónicos de forma segura
    a destinatarios pre-aprobados.
    """

    @property
    def name(self) -> str:
        return "email_client"

    def get_tools(self) -> List[ToolSignature]:
        return [
            ToolSignature(
                name="send_email",
                description="Envía un correo electrónico a un destinatario autorizado. Requiere confirmación del usuario.",
                parameters={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "La dirección de correo electrónico del destinatario."},
                        "subject": {"type": "string", "description": "El asunto del correo electrónico."},
                        "body": {"type": "string", "description": "El cuerpo del mensaje del correo electrónico."}
                    },
                    "required": ["to", "subject", "body"]
                }
            )
        ]

    def _is_recipient_allowed(self, recipient_email: str) -> bool:
        """
        Verifica si la dirección de correo electrónico del destinatario está en la lista blanca.
        """
        for pattern in ALLOWED_RECIPIENT_PATTERNS:
            if re.match(pattern, recipient_email):
                return True
        return False

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name == "send_email":
            to_email = kwargs.get("to")
            subject = kwargs.get("subject")
            body = kwargs.get("body")

            if not all([to_email, subject, body]):
                return {"status": "error", "error_message": "Faltan argumentos para enviar el correo electrónico (to, subject, body)."}

            if not self._is_recipient_allowed(to_email):
                return {"status": "error", "error_message": f"Destinatario '{to_email}' no autorizado. No está en la lista blanca de patrones permitidos."}

            # --- Mecanismo de Confirmación (Temporal en Consola) ---
            print(f"\n--- CONFIRMACIÓN DE ENVÍO DE CORREO ---")
            print(f"A: {to_email}")
            print(f"Asunto: {subject}")
            print(f"Cuerpo: {body[:100]}... (truncado)")
            confirm = input("¿Deseas enviar este correo electrónico? (s/n): ").lower().strip()
            if confirm != 's':
                return {"status": "cancelled", "result": "Envío de correo cancelado por el usuario."}
            # --- Fin Mecanismo de Confirmación ---

            try:
                msg = MIMEMultipart()
                msg['From'] = SENDER_EMAIL
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls() # Habilitar seguridad TLS
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.send_message(msg)
                
                return {"status": "success", "result": f"Correo electrónico enviado exitosamente a {to_email}."}
            except Exception as e:
                return {"status": "error", "error_message": f"Error al enviar el correo electrónico: {e}"}
        else:
            return {"status": "error", "error_message": f"La herramienta '{tool_name}' no es reconocida por el plugin {self.name}."}
