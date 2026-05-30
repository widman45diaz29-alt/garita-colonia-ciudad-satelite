"""Validación de datos con Pydantic."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
class LoginCrear(BaseModel): usuario:str; clave:str
class LoginRespuesta(BaseModel):
    token:str; usuario:str; rol:str; codigo_vecino:str|None=None; debe_cambiar_clave:bool
class UsuarioCrear(BaseModel):
    usuario:str=Field(...,min_length=3); clave_temporal:str=Field(...,min_length=4); rol:str; codigo_vecino:str|None=None
class UsuarioRespuesta(BaseModel):
    id:int; usuario:str; rol:str; codigo_vecino:str|None; activo:bool; debe_cambiar_clave:bool; fecha_creacion:datetime
    class Config: from_attributes=True
class UsuarioEstadoActualizar(BaseModel): activo:bool
class UsuarioResetClave(BaseModel): nueva_clave_temporal:str=Field(...,min_length=4)
class CambiarClave(BaseModel): clave_actual:str; nueva_clave:str=Field(...,min_length=4)
class VecinoCrear(BaseModel):
    nombre_completo:str=Field(...,min_length=3); correo:EmailStr; numero_casa:str; codigo_unico:str=Field(...,min_length=4)
class VecinoRespuesta(VecinoCrear):
    id:int; fecha_creacion:datetime
    class Config: from_attributes=True
class IngresoNormalCrear(BaseModel):
    codigo_vecino:str; nombre_visitante:str; documento:str; placa_vehiculo:str|None=None; observaciones:str|None=None; nombre_agente:str
class PrerregistroCrear(BaseModel):
    codigo_vecino:str|None=None; nombre_visitante:str; documento:str; placa_vehiculo:str|None=None; horas_validez:int=Field(default=24,ge=1,le=168)
class PrerregistroRespuesta(BaseModel):
    id:int; vecino_id:int; nombre_visitante:str; documento:str; placa_vehiculo:str|None; token_qr:str; valido_hasta:datetime; usado:bool; imagen_qr_base64:str|None=None
    class Config: from_attributes=True
class ValidacionQRCrear(BaseModel): token_qr:str; nombre_agente:str; observaciones:str|None=None
class BitacoraRespuesta(BaseModel):
    id:int; tipo_ingreso:str; fecha_ingreso:datetime; nombre_agente:str; nombre_vecino:str; numero_casa:str; nombre_visitante:str; documento:str; placa_vehiculo:str|None
