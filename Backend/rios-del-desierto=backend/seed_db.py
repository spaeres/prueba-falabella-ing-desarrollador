#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo.

Uso:
    python seed_db.py

O desde la raíz del proyecto:
    python seed_db.py
"""
import os
import sys

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from src.app import create_app
from src.config import DevConfig, ProdConfig
from src.extensions import db
from src.db.seed import run_seed


def get_config():
    """Obtiene la configuración según el entorno."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return ProdConfig if env in ("prod", "production") else DevConfig


def main():
    """Función principal para ejecutar el seed."""
    print("Iniciando seed de base de datos...")
    
    # Crear la aplicación Flask
    app = create_app(get_config())
    
    # Ejecutar el seed dentro del contexto de la aplicación
    with app.app_context():
        try:
            run_seed()
            print("Seed completado exitosamente.")
        except Exception as e:
            print(f"Error al ejecutar seed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

