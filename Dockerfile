# Usa una imagen base oficial de Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias primero (para aprovechar la caché de Docker)
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto que usará la app (Render asigna automáticamente $PORT)
EXPOSE $PORT

# Comando para ejecutar la aplicación
CMD python3 main.py
