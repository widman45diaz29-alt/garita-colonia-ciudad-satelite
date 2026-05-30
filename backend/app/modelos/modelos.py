"""Tablas del sistema."""
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.nucleo.base_datos import Base
class Usuario(Base):
    __tablename__='usuarios'
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    usuario:Mapped[str]=mapped_column(String(60),unique=True,index=True,nullable=False)
    clave_hash:Mapped[str]=mapped_column(String(128),nullable=False)
    rol:Mapped[str]=mapped_column(String(30),nullable=False)
    codigo_vecino:Mapped[str|None]=mapped_column(String(20),nullable=True)
    activo:Mapped[bool]=mapped_column(Boolean,default=True)
    debe_cambiar_clave:Mapped[bool]=mapped_column(Boolean,default=True)
    fecha_creacion:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Vecino(Base):
    __tablename__='vecinos'
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    nombre_completo:Mapped[str]=mapped_column(String(120),nullable=False)
    correo:Mapped[str]=mapped_column(String(120),nullable=False)
    numero_casa:Mapped[str]=mapped_column(String(30),unique=True,nullable=False)
    codigo_unico:Mapped[str]=mapped_column(String(20),unique=True,index=True,nullable=False)
    fecha_creacion:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    prerregistros=relationship('Prerregistro',back_populates='vecino')
    bitacoras=relationship('BitacoraIngreso',back_populates='vecino')
class Visitante(Base):
    __tablename__='visitantes'
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    nombre_completo:Mapped[str]=mapped_column(String(120),nullable=False)
    documento:Mapped[str]=mapped_column(String(60),nullable=False)
    placa_vehiculo:Mapped[str|None]=mapped_column(String(20),nullable=True)
    observaciones:Mapped[str|None]=mapped_column(Text,nullable=True)
    fecha_creacion:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    bitacoras=relationship('BitacoraIngreso',back_populates='visitante')
class Prerregistro(Base):
    __tablename__='prerregistros'
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    vecino_id:Mapped[int]=mapped_column(ForeignKey('vecinos.id'),nullable=False)
    nombre_visitante:Mapped[str]=mapped_column(String(120),nullable=False)
    documento:Mapped[str]=mapped_column(String(60),nullable=False)
    placa_vehiculo:Mapped[str|None]=mapped_column(String(20),nullable=True)
    token_qr:Mapped[str]=mapped_column(String(80),unique=True,index=True,nullable=False)
    valido_hasta:Mapped[datetime]=mapped_column(DateTime,nullable=False)
    usado:Mapped[bool]=mapped_column(Boolean,default=False)
    fecha_creacion:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    vecino=relationship('Vecino',back_populates='prerregistros')
class BitacoraIngreso(Base):
    __tablename__='bitacora_ingresos'
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    vecino_id:Mapped[int]=mapped_column(ForeignKey('vecinos.id'),nullable=False)
    visitante_id:Mapped[int]=mapped_column(ForeignKey('visitantes.id'),nullable=False)
    tipo_ingreso:Mapped[str]=mapped_column(String(30),nullable=False)
    fecha_ingreso:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    nombre_agente:Mapped[str]=mapped_column(String(100),nullable=False)
    vecino=relationship('Vecino',back_populates='bitacoras')
    visitante=relationship('Visitante',back_populates='bitacoras')
