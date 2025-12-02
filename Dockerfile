# Usamos una imagen base ligera de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el script al contenedor
COPY main.py .

# (Opcional) Si tuvieras dependencias:
COPY requirements.txt .
RUN pip install paho-mqtt==1.6.1

# Ejecutamos el script
# -u : Unbuffered (crítico para ver logs en Docker al instante)
CMD ["python", "-u", "main.py"] 
