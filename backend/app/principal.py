"""Inicio del backend FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.nucleo.base_datos import Base, motor, SesionLocal
from app.rutas.rutas import rutas
from app.modelos import modelos, Usuario
from app.servicios.servicio_seguridad import crear_hash_clave
Base.metadata.create_all(bind=motor)
def crear_admin_inicial():
    db=SesionLocal()
    try:
        if not db.query(Usuario).filter(Usuario.usuario=='admin').first():
            db.add(Usuario(usuario='admin',clave_hash=crear_hash_clave('admin123'),rol='administrador',activo=True,debe_cambiar_clave=True)); db.commit()
    finally: db.close()
crear_admin_inicial()
aplicacion=FastAPI(title='Garita Colonia Ciudad Satelite',version='3.1.0')
aplicacion.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
aplicacion.include_router(rutas)
@aplicacion.get('/')
def verificar_estado(): return {'mensaje':'API Garita Colonia Ciudad Satelite funcionando'}
