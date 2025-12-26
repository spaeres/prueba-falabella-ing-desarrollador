# Dockerfile para Backend Flask
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y curl para healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio instance si no existe (para SQLite)
RUN mkdir -p instance

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000
ENV FLASK_DEBUG=0

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]

