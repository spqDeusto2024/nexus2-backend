FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /code

# Instala las dependencias necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev build-essential gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia y instala las dependencias de Python
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install -r /code/requirements.txt

# Copia el código fuente
COPY ./app /code/app

# Comando por defecto para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
