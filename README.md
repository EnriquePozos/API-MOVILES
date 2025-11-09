# Estructura del proyecto

| Carpeta/Archivo    | ¿Qué hace?                                                              |
|--------------------|-------------------------------------------------------------------------|
| `models/`          | Tablas de BD (SQLAlchemy)                                               |
| `database/`        | Configuración de BD (conexiones, sesiones)                              |
| `schemas/`         | Validación de datos (Pydantic) que entran/salen de la API               |
| `routers/`         | Endpoints HTTP (rutas: GET, POST, PUT, DELETE)                          |
| `repositories/`    | Lógica de BD (CRUD: crear, leer, actualizar, eliminar)                  |
| `scripts/`         | Scripts que nos sirven para probar funcionalidades de la base de datos  |
| `utils/`           | Utilidades (auth, cloudinary, helpers)                                  |
| `main.py`          | Corazón de la API (registra routers, configuración general)             |


# Crear el entorno virtual

**Se crea**
``` bash
python -m venv venv
```

**Se activa**
``` bash
venv\Scripts\activate
```

**Instalar el requirements.txt con el entorno activo**
``` bash
pip install -r requirements.txt
```

**Ver que se haya instalado**
``` bash
pip list
```

**La salida deberá de ser lo que está escrito en el archivo de requirements.txt**

# Iniciar servidor
``` bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

# Validar base de datos

**Carpeta scripts/**

**test_db_config**

Seleccionar el DB_ENV que se está presente en el .env para verificar la conexión a dicha base de datos; una vez hecho esto ejecuar el archivo de la siguiente manera:

``` bash
python test_db_config.py
```

La salida de dicho comando debe indicar que la conexión fue exitosa e imprimirnos una tupla exactamante así: (1,)


**test_models**

Este archivo es para crear los modelos de la base de datos que están en la carpeta de app/models/ en la base de datos de prueba SQLite, se ejecutará el siguiente comando:

``` bash
python test_models.py
```

La salida deberá indicar la cantidad de tablas que se crearon en SQLite seguido del nombre de cada tabla con todos sus campos desglosados.


**tables_mysql**

Tiene el mismo propósito que el anterior pero para MySQL, cabe recalcar que este archivo no modifica las tablas que ya existen en la base de datos, solo las crea, por lo que si ta existen no hará nada. Ejecutar el comando:

``` bash
python tables_mysql.py
```

Este archivo lee el DB_ENV del .env, por lo que antes de ejecutarlo se deberá de seleccionar el entorno en el que se desea hacer uso de este script.




