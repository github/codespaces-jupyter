#!/bin/bash

# Actualización del SO
echo "Actualizando el sistema operativo..."
sudo apt update && sudo apt upgrade -y

# Instalación de Python 3.10+ y dependencias
echo "Instalando Python 3.10+ y dependencias..."
sudo apt install -y python3.10 python3-pip

# Instalación de dependencias de Python
echo "Instalando dependencias de Python..."
pip install yfinance numpy pandas matplotlib google-cloud-storage

echo "[+] Configuración de infraestructura completada."


echo "[+] Configuración de infraestructura completada."
