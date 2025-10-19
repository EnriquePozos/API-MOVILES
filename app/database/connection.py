"""
Configuración de conexiones a bases de datos.
Soporta MySQL (local y producción) y SQLite (offline).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================
# CONFIGURACIÓN GENERAL
# ============================================
DB_ENV = os.getenv("DB_ENV", "local")  # local, prod, sqlite

# ============================================
# MYSQL LOCAL
# ============================================
DB_LOCAL_HOST = os.getenv("DB_LOCAL_HOST", "localhost")
DB_LOCAL_PORT = os.getenv("DB_LOCAL_PORT", "3306")
DB_LOCAL_USER = os.getenv("DB_LOCAL_USER", "root")
DB_LOCAL_PASSWORD = os.getenv("DB_LOCAL_PASSWORD", "")
DB_LOCAL_NAME = os.getenv("DB_LOCAL_NAME", "PSM")

DATABASE_URL_LOCAL = (
    f"mysql+pymysql://{DB_LOCAL_USER}:{DB_LOCAL_PASSWORD}"
    f"@{DB_LOCAL_HOST}:{DB_LOCAL_PORT}/{DB_LOCAL_NAME}"
    f"?charset=utf8mb4"
)

# ============================================
# MYSQL PRODUCCIÓN (Railway)
# ============================================
DB_PROD_HOST = os.getenv("DB_PROD_HOST", "")
DB_PROD_PORT = os.getenv("DB_PROD_PORT", "3306")
DB_PROD_USER = os.getenv("DB_PROD_USER", "")
DB_PROD_PASSWORD = os.getenv("DB_PROD_PASSWORD", "")
DB_PROD_NAME = os.getenv("DB_PROD_NAME", "PSM")

DATABASE_URL_PROD = (
    f"mysql+pymysql://{DB_PROD_USER}:{DB_PROD_PASSWORD}"
    f"@{DB_PROD_HOST}:{DB_PROD_PORT}/{DB_PROD_NAME}"
    f"?charset=utf8mb4"
    if DB_PROD_HOST  # Solo crear URL si existe configuración
    else None
)

# ============================================
# SQLITE OFFLINE
# ============================================
DB_SQLITE_PATH = os.getenv("DB_SQLITE_PATH", "./offline_db.sqlite")
DATABASE_URL_SQLITE = f"sqlite:///{DB_SQLITE_PATH}"

# ============================================
# CREAR ENGINES
# ============================================

# Engine para MySQL Local
engine_local = create_engine(
    DATABASE_URL_LOCAL,
    echo=True if os.getenv("ENV") == "development" else False,  # Log de SQL en dev
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_recycle=3600,   # Recicla conexiones cada hora
)

# Engine para MySQL Producción
engine_prod = None
if DATABASE_URL_PROD:
    engine_prod = create_engine(
        DATABASE_URL_PROD,
        echo=False,  # No mostrar logs en producción
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Engine para SQLite (modo offline)
engine_sqlite = create_engine(
    DATABASE_URL_SQLITE,
    echo=True if os.getenv("ENV") == "development" else False,
    connect_args={"check_same_thread": False},  # Necesario para SQLite
    poolclass=StaticPool,  # Pool estático para SQLite
)

# ============================================
# FUNCIÓN PARA OBTENER URL SEGÚN ENTORNO
# ============================================
def get_db_url() -> str:
    """
    Retorna la URL de la base de datos según DB_ENV.
    
    Returns:
        str: URL de conexión a la base de datos
    """
    if DB_ENV == "prod":
        if not DATABASE_URL_PROD:
            raise ValueError("DATABASE_URL_PROD no está configurado en .env")
        return DATABASE_URL_PROD
    elif DB_ENV == "sqlite":
        return DATABASE_URL_SQLITE
    else:  # local por defecto
        return DATABASE_URL_LOCAL


def get_current_engine():
    """
    Retorna el engine según el entorno configurado.
    
    Returns:
        Engine: Motor de SQLAlchemy correspondiente
    """
    if DB_ENV == "prod":
        if not engine_prod:
            raise ValueError("Engine de producción no está configurado")
        return engine_prod
    elif DB_ENV == "sqlite":
        return engine_sqlite
    else:  # local por defecto
        return engine_local


# ============================================
# INFORMACIÓN DE CONFIGURACIÓN
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    print(f"Entorno actual: {DB_ENV}")
    print(f"URL Local: {DATABASE_URL_LOCAL}")
    print(f"URL Prod: {DATABASE_URL_PROD if DATABASE_URL_PROD else 'No configurado'}")
    print(f"URL SQLite: {DATABASE_URL_SQLITE}")
    print(f"Engine activo: {get_current_engine()}")
    print("=" * 50)