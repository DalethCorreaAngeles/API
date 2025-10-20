# Imagen base de Python # Comments should be in english, no spanish
FROM python:3.10-slim # why 3.10? why slim?


# Install curl ando other necessary utilities
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta dentro del contenedor
WORKDIR /app

# Copiar todo lo de tu proyecto a /app en el contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para arrancar la app
CMD ["python", "app.py"]
