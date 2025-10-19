**Crear el entorno virtual**

# Se crea
python -m venv venv

# Se activa
venv\Scripts\activate

# Instalar el requirements.txt con el entorno activo

pip install -r requirements.txt

# Ver que se haya instalado

pip list

# La salida deberá de ser lo que está escrito en el archivo de requirements.txt

**Iniciar servidor**

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000