"""Endpoints protegidos del sistema."""
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.nucleo.base_datos import obtener_base_datos
from app.modelos import Usuario, Vecino, Visitante, Prerregistro, BitacoraIngreso
from app.esquemas import *
from app.servicios.servicio_seguridad import crear_hash_clave, verificar_clave, crear_token, obtener_usuario_actual, exigir_roles, bloquear_si_debe_cambiar_clave
from app.servicios.servicio_correo import notificar_vecino
from app.servicios.servicio_qr import generar_qr_base64
rutas=APIRouter(prefix='/api',tags=['Garita'])
@rutas.post('/login',response_model=LoginRespuesta)
def iniciar_sesion(datos:LoginCrear,db:Session=Depends(obtener_base_datos)):
    u=db.query(Usuario).filter(Usuario.usuario==datos.usuario).first()
    if not u or not u.activo or not verificar_clave(datos.clave,u.clave_hash): raise HTTPException(status_code=401,detail='Usuario o contraseña incorrectos')
    return LoginRespuesta(token=crear_token(u),usuario=u.usuario,rol=u.rol,codigo_vecino=u.codigo_vecino,debe_cambiar_clave=u.debe_cambiar_clave)
@rutas.post('/mi-cuenta/cambiar-clave',response_model=LoginRespuesta)
def cambiar_mi_clave(datos:CambiarClave,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    u=db.query(Usuario).filter(Usuario.id==actual['id']).first()
    if not u or not verificar_clave(datos.clave_actual,u.clave_hash): raise HTTPException(status_code=400,detail='Contraseña actual incorrecta')
    u.clave_hash=crear_hash_clave(datos.nueva_clave); u.debe_cambiar_clave=False; db.commit(); db.refresh(u)
    return LoginRespuesta(token=crear_token(u),usuario=u.usuario,rol=u.rol,codigo_vecino=u.codigo_vecino,debe_cambiar_clave=False)
@rutas.get('/usuarios',response_model=list[UsuarioRespuesta])
def listar_usuarios(db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador']); bloquear_si_debe_cambiar_clave(actual); return db.query(Usuario).order_by(Usuario.rol,Usuario.usuario).all()
@rutas.post('/usuarios',response_model=UsuarioRespuesta)
def crear_usuario(datos:UsuarioCrear,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador']); bloquear_si_debe_cambiar_clave(actual)
    if datos.rol not in ['administrador','agente','vecino']: raise HTTPException(status_code=400,detail='Rol inválido')
    if db.query(Usuario).filter(Usuario.usuario==datos.usuario).first(): raise HTTPException(status_code=400,detail='El usuario ya existe')
    if datos.rol=='vecino':
        if not datos.codigo_vecino: raise HTTPException(status_code=400,detail='Debe asociar código de vecino')
        if not db.query(Vecino).filter(Vecino.codigo_unico==datos.codigo_vecino).first(): raise HTTPException(status_code=404,detail='Código de vecino no encontrado')
    u=Usuario(usuario=datos.usuario,clave_hash=crear_hash_clave(datos.clave_temporal),rol=datos.rol,codigo_vecino=datos.codigo_vecino if datos.rol=='vecino' else None,activo=True,debe_cambiar_clave=True)
    db.add(u); db.commit(); db.refresh(u); return u
@rutas.patch('/usuarios/{usuario_id}/estado',response_model=UsuarioRespuesta)
def actualizar_estado_usuario(usuario_id:int,datos:UsuarioEstadoActualizar,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador']); bloquear_si_debe_cambiar_clave(actual); u=db.query(Usuario).filter(Usuario.id==usuario_id).first()
    if not u: raise HTTPException(status_code=404,detail='Usuario no encontrado')
    if u.id==actual['id'] and not datos.activo: raise HTTPException(status_code=400,detail='No puede desactivarse a sí mismo')
    u.activo=datos.activo; db.commit(); db.refresh(u); return u
@rutas.post('/usuarios/{usuario_id}/restablecer-clave',response_model=UsuarioRespuesta)
def restablecer_clave(usuario_id:int,datos:UsuarioResetClave,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador']); bloquear_si_debe_cambiar_clave(actual); u=db.query(Usuario).filter(Usuario.id==usuario_id).first()
    if not u: raise HTTPException(status_code=404,detail='Usuario no encontrado')
    u.clave_hash=crear_hash_clave(datos.nueva_clave_temporal); u.debe_cambiar_clave=True; db.commit(); db.refresh(u); return u
@rutas.post('/vecinos',response_model=VecinoRespuesta)
def crear_vecino(datos:VecinoCrear,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador']); bloquear_si_debe_cambiar_clave(actual)
    if db.query(Vecino).filter((Vecino.numero_casa==datos.numero_casa)|(Vecino.codigo_unico==datos.codigo_unico)).first(): raise HTTPException(status_code=400,detail='La casa o el código único ya existe')
    v=Vecino(**datos.model_dump()); db.add(v); db.commit(); db.refresh(v); return v
@rutas.get('/vecinos',response_model=list[VecinoRespuesta])
def listar_vecinos(db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador','agente']); bloquear_si_debe_cambiar_clave(actual); return db.query(Vecino).order_by(Vecino.numero_casa).all()
@rutas.post('/ingresos/normal',response_model=BitacoraRespuesta)
def registrar_ingreso_normal(datos:IngresoNormalCrear,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador','agente']); bloquear_si_debe_cambiar_clave(actual); v=db.query(Vecino).filter(Vecino.codigo_unico==datos.codigo_vecino).first()
    if not v: raise HTTPException(status_code=404,detail='Código de vecino no encontrado')
    vi=Visitante(nombre_completo=datos.nombre_visitante,documento=datos.documento,placa_vehiculo=datos.placa_vehiculo,observaciones=datos.observaciones); db.add(vi); db.flush()
    b=BitacoraIngreso(vecino_id=v.id,visitante_id=vi.id,tipo_ingreso='normal',nombre_agente=datos.nombre_agente); db.add(b); db.commit(); db.refresh(b)
    notificar_vecino(v.correo,v.nombre_completo,vi.nombre_completo,v.numero_casa,'normal'); return convertir_bitacora(b)
@rutas.post('/prerregistros',response_model=PrerregistroRespuesta)
def crear_prerregistro(datos:PrerregistroCrear,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador','agente','vecino']); bloquear_si_debe_cambiar_clave(actual); codigo=actual.get('codigo_vecino') if actual.get('rol')=='vecino' else datos.codigo_vecino
    if not codigo: raise HTTPException(status_code=400,detail='Debe indicar código del vecino')
    v=db.query(Vecino).filter(Vecino.codigo_unico==codigo).first()
    if not v: raise HTTPException(status_code=404,detail='Código de vecino no encontrado')
    token=str(uuid4()); p=Prerregistro(vecino_id=v.id,nombre_visitante=datos.nombre_visitante,documento=datos.documento,placa_vehiculo=datos.placa_vehiculo,token_qr=token,valido_hasta=datetime.utcnow()+timedelta(hours=datos.horas_validez))
    db.add(p); db.commit(); db.refresh(p); r=PrerregistroRespuesta.model_validate(p); r.imagen_qr_base64=generar_qr_base64(token); return r
@rutas.post('/ingresos/qr',response_model=BitacoraRespuesta)
def registrar_ingreso_qr(datos:ValidacionQRCrear,db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador','agente']); bloquear_si_debe_cambiar_clave(actual); p=db.query(Prerregistro).filter(Prerregistro.token_qr==datos.token_qr).first()
    if not p: raise HTTPException(status_code=404,detail='QR no encontrado')
    if p.usado: raise HTTPException(status_code=400,detail='Este QR ya fue utilizado')
    if p.valido_hasta<datetime.utcnow(): raise HTTPException(status_code=400,detail='Este QR ya venció')
    vi=Visitante(nombre_completo=p.nombre_visitante,documento=p.documento,placa_vehiculo=p.placa_vehiculo,observaciones=datos.observaciones); db.add(vi); db.flush()
    b=BitacoraIngreso(vecino_id=p.vecino_id,visitante_id=vi.id,tipo_ingreso='prerregistro',nombre_agente=datos.nombre_agente); p.usado=True; db.add(b); db.commit(); db.refresh(b)
    notificar_vecino(p.vecino.correo,p.vecino.nombre_completo,vi.nombre_completo,p.vecino.numero_casa,'prerregistro'); return convertir_bitacora(b)
@rutas.get('/bitacora',response_model=list[BitacoraRespuesta])
def listar_bitacora(db:Session=Depends(obtener_base_datos),actual:dict=Depends(obtener_usuario_actual)):
    exigir_roles(actual,['administrador','agente']); bloquear_si_debe_cambiar_clave(actual); return [convertir_bitacora(x) for x in db.query(BitacoraIngreso).order_by(desc(BitacoraIngreso.fecha_ingreso)).limit(100).all()]
def convertir_bitacora(x:BitacoraIngreso)->BitacoraRespuesta:
    return BitacoraRespuesta(id=x.id,tipo_ingreso=x.tipo_ingreso,fecha_ingreso=x.fecha_ingreso,nombre_agente=x.nombre_agente,nombre_vecino=x.vecino.nombre_completo,numero_casa=x.vecino.numero_casa,nombre_visitante=x.visitante.nombre_completo,documento=x.visitante.documento,placa_vehiculo=x.visitante.placa_vehiculo)
