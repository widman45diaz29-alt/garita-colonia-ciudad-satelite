"""Notificación por correo o simulación en consola."""

import smtplib
from email.message import EmailMessage

from app.nucleo.configuracion import (
    SERVIDOR_SMTP,
    PUERTO_SMTP,
    USUARIO_SMTP,
    CLAVE_SMTP,
    CORREO_REMITENTE,
)


def notificar_vecino(
    correo_destino,
    nombre_vecino,
    nombre_visitante,
    numero_casa,
    tipo_ingreso
):

    cuerpo = f"""
Hola {nombre_vecino},

Se registró una visita para la vivienda {numero_casa}.

Visitante: {nombre_visitante}
Tipo: {tipo_ingreso}
"""

    if not SERVIDOR_SMTP or not USUARIO_SMTP or not CLAVE_SMTP:
        print("===== CORREO SIMULADO =====")
        print("Para:", correo_destino)
        print(cuerpo)
        return

    mensaje = EmailMessage()
    mensaje["Subject"] = "Notificación de visita en garita"
    mensaje["From"] = CORREO_REMITENTE
    mensaje["To"] = correo_destino
    mensaje.set_content(cuerpo)

    print("====================================")
    print("Intentando enviar correo")
    print("Servidor:", SERVIDOR_SMTP)
    print("Puerto:", PUERTO_SMTP)
    print("Usuario:", USUARIO_SMTP)
    print("Destino:", correo_destino)
    print("====================================")

    try:
        with smtplib.SMTP(SERVIDOR_SMTP, PUERTO_SMTP) as servidor:
            servidor.starttls()
            servidor.login(USUARIO_SMTP, CLAVE_SMTP)
            servidor.send_message(mensaje)

        print("Correo enviado correctamente")

    except Exception as e:
        print("Error al enviar correo")
        print(type(e).__name__)
        print(str(e))
