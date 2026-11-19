@echo off
echo Instalando dependencias...
pip install -r requirements.txt
echo Iniciando servidor en http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000
python app.py
pause