#!/bin/bash
# Ejecutar pruebas
poetry run pytest
# Verificar si las pruebas fueron exitosas
if [ $? -eq 0 ]
then
  echo "Pruebas exitosas, iniciando la aplicación..."
  poetry run python3 -m flask --app app.py --debug run --host=0.0.0.0
else
  echo "Pruebas fallidas, deteniendo el contenedor..."
  exit 1
fi