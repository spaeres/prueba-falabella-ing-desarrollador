# Rios del Desierto S.A.S - Aplicación de Gestión de Clientes

## Descripción

Aplicación web para la gestión de clientes, compras y reportes de fidelización de Rios del Desierto S.A.S.

## Arquitectura

- **Backend**: Flask + SQLAlchemy (Python 3.11)
- **Frontend**: React + Vite
- **Base de datos**: SQLite (archivo persistente)

## Modelo de Datos

El modelo de datos incluye las siguientes entidades y sus relaciones:

- **Cliente**: Información personal de los clientes
- **Documento**: Documento de identificación (1:1 con Cliente)
- **Compra**: Registro de compras realizadas (N:1 con Cliente)
- **DetalleCompra**: Detalles de productos en cada compra (N:1 con Compra y Producto)
- **Producto**: Catálogo de productos disponibles

![Modelo de Datos](docs/modelo-datos.png)


## Video de Prueba de funcionamiento



## Requisitos

- Docker
- Docker Compose

## Instalación y Ejecución con Docker

### Opción 1: Usar Docker Compose (Opción Recomendada)

1. **Clonar o navegar al directorio del proyecto**

2. **Construir y ejecutar los contenedores:**
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la aplicación:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/health

### Opción 2: Construir y ejecutar manualmente (NO SE RECOMIENDA)

#### Backend

```bash
cd Backend/rios-del-desierto=backend
docker build -t rios-backend .
docker run -p 8000:8000 -v $(pwd)/instance:/app/instance rios-backend
```

#### Frontend

```bash
cd Frontend/rios-del-desierto-frontend
docker build -t rios-frontend --build-arg VITE_API_BASE=http://localhost:8000/api/v1 .
docker run -p 3000:80 rios-frontend
```

## Comandos Docker Compose Útiles

- **Iniciar servicios**: `docker-compose up`
- **Iniciar en segundo plano**: `docker-compose up -d`
- **Detener servicios**: `docker-compose down`
- **Ver logs**: `docker-compose logs -f`
- **Reconstruir**: `docker-compose up --build`
- **Limpiar todo**: `docker-compose down -v`

## Estructura del Proyecto

```
.
├── Backend/
│   └── rios-del-desierto=backend/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── run.py
│       ├── instance/
│       │   └── app.db          # Base de datos SQLite
│       └── src/
│           ├── app.py
│           ├── config.py
│           ├── models/
│           └── api/
│               └── v1/
├── Frontend/
│   └── rios-del-desierto-frontend/
│       ├── Dockerfile
│       ├── package.json
│       └── src/
│           ├── App.jsx
│           ├── components/
│           ├── pages/
│           └── utils/
└── docker-compose.yml
```

## Base de Datos SQLite

### Ubicación

La base de datos SQLite se encuentra en:
```
Backend/rios-del-desierto=backend/instance/app.db
```

Este archivo se crea automáticamente cuando se ejecuta la aplicación por primera vez o cuando se ejecutan las migraciones. La carpeta `instance/` es donde Flask almacena archivos específicos de la instancia de la aplicación (como la base de datos en desarrollo).

### Creación y Poblado de la Base de Datos

#### 1. Crear las Tablas (Migraciones)

Primero, es necesario crear las tablas en la base de datos ejecutando las migraciones:

```bash
cd Backend/rios-del-desierto=backend
flask --app run.py db upgrade
```

Este comando aplica todas las migraciones pendientes y crea las tablas necesarias:
- `clientes`
- `documentos`
- `productos`
- `compras`
- `detalles_compra`

#### 2. Poblar la Base de Datos con Datos de Ejemplo (Seed)

Una vez creadas las tablas, puedes poblar la base de datos con datos de ejemplo usando el script de seed:

```bash
cd Backend/rios-del-desierto=backend
python seed_db.py
```

#### ¿Qué hace el seed?

El script `seed_db.py` crea los siguientes datos de ejemplo:

**Clientes:**
- **Juan Pérez** - Cédula: 123456789
  - Compras del último mes que superan 5'000.000 COP
- **María González** - Cédula: 987654321
  - Compras del último mes que superan 5'000.000 COP (6'100.000 COP)
- **Pedro Martínez** - Cédula: 456789123
  - Compras del último mes que NO superan 5'000.000 COP (4'100.000 COP)
- **Ana Rodríguez** - Pasaporte: AB123456
  - Cliente con pasaporte, compra de 2'500.000 COP
- **Empresa Comercial S.A.S.** - NIT: 900123456-7
  - Cliente empresa con NIT, compra grande de 8'500.000 COP

**Productos:**
- Televisor 65 pulgadas: $3'000.000 COP
- Portátil Gamer: $2'500.000 COP
- Barra de Sonido: $600.000 COP

**Compras:**
- Se crean compras de ejemplo para cada cliente
- Algunas compras son del último mes (últimos 30 días)
- Algunas compras son más antiguas (para pruebas)
- Los montos están configurados para probar el reporte de fidelización

#### Notas sobre el Seed

- El script verifica si ya existen datos en la base de datos antes de ejecutarse
- Si ya hay datos, el seed se omite para evitar duplicados
- Para ejecutar el seed nuevamente, primero debes eliminar o limpiar la base de datos
- El seed crea relaciones completas entre clientes, documentos, productos, compras y detalles de compra
```

## Notas Importantes

- La base de datos SQLite se persiste en `Backend/rios-del-desierto=backend/instance/app.db`
- El backend se inicia primero y el frontend espera a que esté saludable
- El frontend está configurado para comunicarse con el backend en `http://localhost:8000/api/v1`
- Si cambias el puerto del backend, actualiza `VITE_API_BASE` en el Dockerfile del frontend
- En Docker, la base de datos se persiste mediante un volumen montado en `instance/`

## Desarrollo Local (sin Docker)

### Backend

```bash
cd Backend/rios-del-desierto=backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend

```bash
cd Frontend/rios-del-desierto-frontend
npm install
npm run dev
```

## Endpoints API

- `GET /` - Mensaje de bienvenida
- `GET /health` - Health check
- `POST /api/v1/clientes` - Crear cliente
- `GET/POST /api/v1/clientes/buscar` - Buscar cliente por documento
- `GET/POST /api/v1/clientes/exportar` - Exportar datos del cliente
- `GET /api/v1/reportes/clientes-fidelizacion` - Reporte de fidelización

