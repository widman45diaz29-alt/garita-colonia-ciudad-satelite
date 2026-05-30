"""Hash de contraseñas, tokens y permisos."""
import base64, hashlib, hmac, json, time
from fastapi import Header, HTTPException
from app.nucleo.configuracion import CLAVE_SECRETA
from app.modelos import Usuario
def crear_hash_clave(clave:str)->str: return hashlib.sha256((CLAVE_SECRETA+clave).encode()).hexdigest()
def verificar_clave(clave:str, clave_hash:str)->bool: return hmac.compare_digest(crear_hash_clave(clave), clave_hash)
def crear_token(usuario:Usuario)->str:
    datos={'id':usuario.id,'usuario':usuario.usuario,'rol':usuario.rol,'codigo_vecino':usuario.codigo_vecino,'debe_cambiar_clave':usuario.debe_cambiar_clave,'exp':int(time.time())+60*60*8}
    cuerpo=base64.urlsafe_b64encode(json.dumps(datos).encode()).decode()
    firma=hmac.new(CLAVE_SECRETA.encode(),cuerpo.encode(),hashlib.sha256).hexdigest()
    return f'{cuerpo}.{firma}'
def leer_token(token:str)->dict:
    try:
        cuerpo,firma=token.split('.')
        firma_ok=hmac.new(CLAVE_SECRETA.encode(),cuerpo.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma,firma_ok): raise ValueError()
        datos=json.loads(base64.urlsafe_b64decode(cuerpo.encode()).decode())
        if datos.get('exp',0)<int(time.time()): raise ValueError()
        return datos
    except Exception: raise HTTPException(status_code=401,detail='Sesión inválida o vencida')
def obtener_usuario_actual(authorization:str|None=Header(default=None))->dict:
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(status_code=401,detail='Debe iniciar sesión')
    return leer_token(authorization.replace('Bearer ',''))
def exigir_roles(actual:dict, roles:list[str]):
    if actual.get('rol') not in roles: raise HTTPException(status_code=403,detail='No tiene permisos para esta acción')
def bloquear_si_debe_cambiar_clave(actual:dict):
    if actual.get('debe_cambiar_clave'): raise HTTPException(status_code=403,detail='Debe cambiar su contraseña antes de continuar')
