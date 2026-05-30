"""Configuración general del backend."""
import os
from dotenv import load_dotenv
load_dotenv()
URL_BASE_DATOS = os.getenv(
    'URL_BASE_DATOS', 'postgresql+psycopg2://postgres:postgres@localhost:5432/garita_db')
CLAVE_SECRETA = os.getenv('CLAVE_SECRETA', 'clave-dev-garita')
SERVIDOR_SMTP = os.getenv('SERVIDOR_SMTP', 'smtp.gmail.com')
PUERTO_SMTP = int(os.getenv('PUERTO_SMTP', '587'))
USUARIO_SMTP = os.getenv('USUARIO_SMTP', 'wdiazp6@miumg.edu.gt')
CLAVE_SMTP = os.getenv('CLAVE_SMTP', 'kbkz xbkj eilj wzfw')
CORREO_REMITENTE = os.getenv('CORREO_REMITENTE', 'wdiazp6@miumg.edu.gt')
