"""Generación de QR."""
import base64
from io import BytesIO
import qrcode
def generar_qr_base64(token:str)->str:
    imagen=qrcode.make(token); memoria=BytesIO(); imagen.save(memoria,format='PNG')
    return base64.b64encode(memoria.getvalue()).decode('utf-8')
