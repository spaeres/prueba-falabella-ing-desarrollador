# src/config.py
import os
from pathlib import Path

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta instance/
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    """
    Configuración base.
    Usa variables de entorno si existen,
    pero tiene valores por defecto para que la app corra sin .env
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


class DevConfig(Config):
    DEBUG = True

    # Asegura que exista instance/
    INSTANCE_DIR.mkdir(exist_ok=True)

    # SQLite por defecto (funciona sin .env)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"
    )


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProdConfig(Config):
    DEBUG = False
    # En prod se espera que DATABASE_URL venga del entorno
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
