from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Base de datos (ORM)
db = SQLAlchemy()

# Migraciones (Alembic)
migrate = Migrate()

# CORS (para permitir llamadas desde el frontend)
cors = CORS()