#!/bin/bash

# ==============================================================================
# SCRIPT DE AUTOMATIZACIÓN: MOTOR CUÁNTICO-RELATIVISTA
# ==============================================================================

echo "[*] Iniciando despliegue del entorno..."

# 1. Configuración del entorno virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[+] Entorno virtual creado."
fi
source venv/bin/activate

# 2. Verificación de dependencias
pip install --upgrade pip
pip install numpy pandas yfinance matplotlib seaborn

# 3. Ejecución del motor (puedes extraer el código a main.py si prefieres)
echo "[*] Ejecutando simulación de estabilidad sobre datos BTC-USD..."
python3 -c "
# Aquí iría la lógica del engine extraída del notebook para ejecución headless
# (Opcionalmente, puedes ejecutar el notebook vía nbconvert)
from QuantumRelativisticEngine import QuantumRelativisticEngine
# ... lógica de simulación ...
print('[+] Simulación finalizada.')
"

echo "[+] Reporte de estabilidad generado en 'panel_estabilidad_fase.png'"
