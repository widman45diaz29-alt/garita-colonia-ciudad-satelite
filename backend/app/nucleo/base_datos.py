"""Conexión a PostgreSQL usando SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.nucleo.configuracion import URL_BASE_DATOS
motor=create_engine(URL_BASE_DATOS,pool_pre_ping=True)
SesionLocal=sessionmaker(autocommit=False,autoflush=False,bind=motor)
class Base(DeclarativeBase): pass
def obtener_base_datos():
    db=SesionLocal()
    try: yield db
    finally: db.close()
