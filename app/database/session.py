"""
Gestión de sesiones de base de datos.
Provee dependency injection para FastAPI.
"""

from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .connection import engine_local, engine_prod, engine_sqlite, get_current_engine

# ============================================
# CREAR SESSION MAKERS
# ============================================

# SessionLocal para MySQL Local
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_local
)

# SessionProd para MySQL Producción
SessionProd = None
if engine_prod:
    SessionProd = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine_prod
    )

# SessionSQLite para SQLite (modo offline)
SessionSQLite = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_sqlite
)

# ============================================
# DEPENDENCY INJECTION PARA FASTAPI
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de BD según entorno configurado.
    Uso en endpoints:
        @app.get("/usuarios")
        def get_usuarios(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: Sesión de base de datos
    """
    engine = get_current_engine()
    SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()


def get_db_local() -> Generator[Session, None, None]:
    """
    Dependency específica para MySQL Local.
    Útil cuando necesitas forzar conexión local sin importar DB_ENV.
    
    Yields:
        Session: Sesión de MySQL Local
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_prod() -> Generator[Session, None, None]:
    """
    Dependency específica para MySQL Producción.
    
    Yields:
        Session: Sesión de MySQL Producción
    
    Raises:
        ValueError: Si la configuración de producción no existe
    """
    if not SessionProd:
        raise ValueError("Sesión de producción no configurada")
    
    db = SessionProd()
    try:
        yield db
    finally:
        db.close()


def get_db_sqlite() -> Generator[Session, None, None]:
    """
    Dependency específica para SQLite (modo offline).
    Se usará en la app móvil para operaciones sin conexión.
    
    Yields:
        Session: Sesión de SQLite
    """
    db = SessionSQLite()
    try:
        yield db
    finally:
        db.close()


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def create_all_tables():
    """
    Crea todas las tablas en todas las bases de datos.
    ⚠️ Solo usar en desarrollo. En producción usar Alembic.
    """
    from .base import Base
    
    # Crear en local
    print("Creando tablas en MySQL Local...")
    Base.metadata.create_all(bind=engine_local)
    
    # Crear en producción si existe
    if engine_prod:
        print("Creando tablas en MySQL Producción...")
        Base.metadata.create_all(bind=engine_prod)
    
    # Crear en SQLite
    print("Creando tablas en SQLite...")
    Base.metadata.create_all(bind=engine_sqlite)
    
    print("✅ Todas las tablas creadas exitosamente")


def drop_all_tables():
    """
    ⚠️ PELIGRO: Elimina todas las tablas.
    Solo usar en desarrollo para resetear BD.
    """
    from .base import Base
    
    print("⚠️ Eliminando todas las tablas...")
    Base.metadata.drop_all(bind=engine_local)
    Base.metadata.drop_all(bind=engine_sqlite)
    if engine_prod:
        Base.metadata.drop_all(bind=engine_prod)
    
    print("✅ Todas las tablas eliminadas")


# ============================================
# SCRIPT DE PRUEBA
# ============================================
if __name__ == "__main__":
    print("Probando conexiones a base de datos...")
    
    # Probar conexión local
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        print("✅ Conexión MySQL Local exitosa")
        db.close()
    except Exception as e:
        print(f"❌ Error en MySQL Local: {e}")
    
    # Probar conexión SQLite
    try:
        db = SessionSQLite()
        db.execute("SELECT 1")
        print("✅ Conexión SQLite exitosa")
        db.close()
    except Exception as e:
        print(f"❌ Error en SQLite: {e}")
    
    # Probar conexión producción si existe
    if SessionProd:
        try:
            db = SessionProd()
            db.execute("SELECT 1")
            print("✅ Conexión MySQL Producción exitosa")
            db.close()
        except Exception as e:
            print(f"❌ Error en MySQL Producción: {e}")