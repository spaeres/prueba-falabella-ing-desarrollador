from flask import Flask, jsonify
from .config import DevConfig
from .extensions import db, migrate, cors


def create_app(config_object=DevConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # CORS: permite que el frontend consuma la API:
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar blueprints (rutas)
    # Nota: estos imports van aquí para evitar imports circulares
    from .api.v1.clientes_routes import bp as clientes_bp
    from .api.v1.reportes_routes import bp as reportes_bp

    app.register_blueprint(clientes_bp, url_prefix="/api/v1")
    app.register_blueprint(reportes_bp, url_prefix="/api/v1")

    # Importar modelos para migraciones del ORM:
    from . import models

    # Endpoint de entrada basico:
    @app.get("/")
    def home():
        return jsonify({"message": "API de Rios del desierto S.A.S"})

    # Health check de la app:
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Manejo de Errores básicos:
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"error": "Internal server error"}), 500

    return app
