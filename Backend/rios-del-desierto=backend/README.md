# Backend - Rios del Desierto S.A.S

API REST desarrollada con **Flask** y **SQLAlchemy** como ORM para la gestión de clientes, productos y compras.

## Arquitectura del Proyecto

Este proyecto está construido con **Flask**, un framework web ligero de Python, y utiliza **SQLAlchemy** como ORM (Object-Relational Mapping) para la gestión de la base de datos.

### Stack Tecnológico

- **Flask**: Framework web para crear la API REST
- **Flask-SQLAlchemy**: Integración de SQLAlchemy con Flask para el ORM
- **Flask-Migrate**: Herramienta para gestionar migraciones de base de datos (usa Alembic)
- **Flask-CORS**: Permite que el frontend consuma la API desde diferentes orígenes
- **SQLAlchemy**: ORM que mapea objetos Python a tablas de base de datos
- **pandas & openpyxl**: Para generación de reportes en Excel

## Estructura del Proyecto

```
rios-del-desierto=backend/
├── src/
│   ├── app.py              # Factory pattern para crear la aplicación Flask
│   ├── config.py           # Configuraciones (Dev/Test/Prod)
│   ├── extensions.py       # Extensiones Flask (db, migrate, cors)
│   ├── models/             # Modelos SQLAlchemy (ORM)
│   │   ├── cliente.py      # Modelo Cliente
│   │   ├── documento.py    # Modelo Documento (1:1 con Cliente)
│   │   ├── producto.py     # Modelo Producto
│   │   ├── compra.py       # Modelo Compra
│   │   ├── detalle_compra.py # Modelo DetalleCompra
│   │   └── enums.py        # Enumeraciones (TipoDocumento, EstadoCompra)
│   ├── api/
│   │   └── v1/
│   │       ├── clientes_routes.py  # Endpoints de clientes
│   │       └── reportes_routes.py  # Endpoints de reportes
│   └── db/
│       └── seed.py         # Script para poblar la base de datos
├── migrations/             # Migraciones de Alembic (Flask-Migrate)
├── instance/               # Base de datos SQLite (desarrollo)
├── run.py                  # Punto de entrada de la aplicación
├── seed_db.py              # Script para ejecutar el seed
└── requirements.txt        # Dependencias del proyecto
```

## Como Funciona el Proyecto

### Flask como Framework Web

Flask maneja las peticiones HTTP y enruta las solicitudes a los endpoints correspondientes. La aplicación se crea usando el patrón **Factory Pattern** en `src/app.py`, lo que permite crear instancias de la app con diferentes configuraciones según el entorno.

### SQLAlchemy como ORM

SQLAlchemy actúa como ORM, lo que significa que:

- **Mapea objetos Python a tablas de base de datos**: Cada modelo (Cliente, Producto, Compra, etc.) es una clase Python que representa una tabla en la base de datos.
- **Gestiona relaciones**: Define relaciones entre modelos (1:1, 1:N, N:M) usando `relationship()`.
- **Abstrae el SQL**: Permite trabajar con la base de datos usando código Python en lugar de SQL directo.
- **Valida datos**: Incluye validaciones a nivel de modelo y constraints a nivel de base de datos.

### Ejemplo de Modelo SQLAlchemy

```python
class Cliente(db.Model):
    __tablename__ = "clientes"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    correo_electronico: Mapped[str] = mapped_column(String(120), unique=True)
    
    # Relación 1:1 con Documento
    documento = relationship("Documento", back_populates="cliente")
    
    # Relación 1:N con Compra
    compras: Mapped[List["Compra"]] = relationship("Compra", back_populates="cliente")
```

## Modelo de Datos

### Entidades Principales

1. **Cliente**: Información personal del cliente
   - Relación 1:1 con `Documento`
   - Relación 1:N con `Compra`

2. **Documento**: Tipo y número de documento del cliente
   - Relación 1:1 con `Cliente`

3. **Producto**: Catálogo de productos disponibles

4. **Compra**: Transacciones de compra realizadas por clientes
   - Relación N:1 con `Cliente`
   - Relación 1:N con `DetalleCompra`

5. **DetalleCompra**: Productos específicos de cada compra
   - Relación N:1 con `Compra`
   - Relación N:1 con `Producto`

## Configuración y Uso

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

El proyecto soporta múltiples entornos:
- **Desarrollo**: SQLite (por defecto)
- **Producción**: PostgreSQL (configurado mediante variable de entorno)

Variables de entorno opcionales (`.env`):
```
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/app.db
SECRET_KEY=tu-secret-key
```

### Migraciones de Base de Datos

```bash
# Crear una nueva migración
flask --app run.py db migrate -m "nueva migracion"

# Aplicar migraciones
flask --app run.py db upgrade 
```

### Poblar Base de Datos

```bash
# Ejecutar el seed para crear datos de ejemplo
python seed_db.py
```

### Ejecutar la Aplicación del Backend:

```bash
# Desarrollo
python run.py
```

## Endpoints Disponibles

### Clientes

- `POST /api/v1/clientes` - Crear un nuevo cliente
- `GET/POST /api/v1/clientes/buscar` - Buscar cliente por documento
- `GET/POST /api/v1/clientes/exportar` - Exportar información del cliente (CSV, TXT, Excel)

### Reportes

- `GET /api/v1/reportes/clientes-fidelizacion` - Generar reporte Excel con clientes de fidelización

## Características Técnicas

- **Validaciones**: A nivel de modelo (SQLAlchemy `@validates`) y base de datos (CheckConstraint)
- **Relaciones**: CASCADE en eliminaciones donde corresponde, RESTRICT en productos
- **Enums**: Soporte para SQLite (usando `native_enum=False`) y PostgreSQL
- **CORS**: Habilitado para `/api/*` desde cualquier origen
- **Type Hints**: Uso de type hints modernos de Python con SQLAlchemy 2.0

## Notas

- El proyecto usa SQLAlchemy 2.0 con sintaxis moderna (Mapped, mapped_column)
- Las migraciones se gestionan con Flask-Migrate (Alembic)
- Los enums funcionan tanto en SQLite como PostgreSQL gracias a `native_enum=False`

