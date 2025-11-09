"""
Script de prueba para verificar modelos SQLAlchemy.
Ejecutar: python test_models.py
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANTE: Importar Base primero
from app.database.base import Base
from app.database.connection import engine_local, engine_sqlite

# Luego importar TODOS los modelos (esto los registra en Base.metadata)
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario
from app.models.reaccion import Reaccion
from app.models.multimedia import Multimedia
from app.models.favorito import Favorito

print("=" * 60)
print("🔍 VERIFICACIÓN DE MODELOS")
print("=" * 60)

# Verificar que todos los modelos se importaron correctamente
modelos = [Usuario, Publicacion, Comentario, Reaccion, Multimedia, Favorito]
print(f"\n✅ {len(modelos)} modelos importados correctamente:")
for modelo in modelos:
    print(f"   - {modelo.__name__}")

# Verificar tablas que se crearán
print(f"\n📋 Tablas registradas en Base.metadata:")
if Base.metadata.tables:
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")
else:
    print("   ⚠️  No hay tablas registradas (problema de importación)")

# Intentar crear las tablas en SQLite (solo prueba)
print(f"\n🧪 Intentando crear tablas en SQLite (prueba)...")
try:
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine_sqlite)
    print("✅ Comando create_all ejecutado")
    
    # Verificar que se crearon
    from sqlalchemy import inspect, text
    inspector = inspect(engine_sqlite)
    tablas_creadas = inspector.get_table_names()
    
    if tablas_creadas:
        print(f"\n✅ {len(tablas_creadas)} tablas creadas en SQLite:")
        for tabla in tablas_creadas:
            print(f"   - {tabla}")
            
            # Mostrar columnas de cada tabla
            columnas = inspector.get_columns(tabla)
            print(f"     Columnas: {', '.join([col['name'] for col in columnas])}")
    else:
        print("\n⚠️  No se crearon tablas. Verificando...")
        
        # Intentar query directo
        with engine_sqlite.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            todas_tablas = result.fetchall()
            print(f"   Tablas en SQLite: {todas_tablas}")
        
except Exception as e:
    print(f"❌ Error al crear tablas: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("💡 Si todo está OK, continúa con crear tablas en MySQL")
print("=" * 60)