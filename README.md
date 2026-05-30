# Proyecto Garita Colonia Ciudad Satelite
Elaborado por
    
              Widman Diaz Peña.
              Anderson Leonel Echeverria Ayala.
              Gendry Gabriel Hernandez Reyes.

Sistema web para control de ingreso residencial con FastAPI, PostgreSQL, React y Docker.

## Acceso inicial

```text
Usuario: admin
Contraseña: admin123
```

Al ingresar por primera vez, el sistema pedirá cambiar la contraseña temporal.

## Ejecutar

```bash
cp .env.example .env
docker compose up --build
```

Abrir:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Docs API: http://localhost:8000/docs

## Roles

- administrador: gestiona usuarios, vecinos, ingresos, QR y bitácora.
- agente: registra ingresos, valida QR y consulta bitácora.
- vecino: genera QR para su propia vivienda.
