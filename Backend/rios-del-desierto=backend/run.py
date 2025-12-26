# run.py
import os

from dotenv import load_dotenv
load_dotenv()

from src.app import create_app
from src.config import DevConfig, ProdConfig


def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return ProdConfig if env in ("prod", "production") else DevConfig


app = create_app(get_config())

if __name__ == "__main__":
    # En producción normalmente NO se usa app.run (se usa gunicorn),
    # pero se usa para esta prueba:
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
