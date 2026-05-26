FROM python:3.10-slim

WORKDIR /app

ENV MPLBACKEND=Agg

# Instalación de dependencias de Python
RUN pip install yfinance numpy pandas matplotlib seaborn google-cloud-storage

# Copiar el script principal de la aplicación
COPY main.py .

ENTRYPOINT ["python3", "main.py"]
