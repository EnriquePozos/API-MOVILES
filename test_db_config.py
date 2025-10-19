"""
Script de prueba para verificar configuración de base de datos.
Ejecutar: python test_db_config.py
"""

import sys
sys.path.append('./app')

from database.connection import (
    get_db_url, 
    get_current_engine,
    DATABASE_URL_LOCAL,
    DATABASE_URL_SQLITE,
    DB_ENV
)

print("=" * 60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE BASE DE DATOS")
print("=" * 60)

print(f"\n📌 Entorno actual: {DB_ENV}")
print(f"\n🔗 URLs configuradas:")
print(f"   Local:  {DATABASE_URL_LOCAL}")
print(f"   SQLite: {DATABASE_URL_SQLITE}")

print(f"\n✅ URL activa: {get_db_url()}")

try:
    from sqlalchemy import text
    
    engine = get_current_engine()
    print(f"\n✅ Engine creado exitosamente")
    print(f"   Tipo: {type(engine)}")
    print(f"   Dialect: {engine.dialect.name}")
    
    # Intentar conexión
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"\n✅ Conexión exitosa a la base de datos")
        print(f"   Resultado de prueba: {result.fetchone()}")
        
except Exception as e:
    print(f"\n❌ Error al conectar: {e}")
    print("\n💡 Soluciones:")
    if "mysql" in str(e).lower():
        print("   1. Verifica que MySQL esté corriendo")
        print("   2. Verifica credenciales en .env")
        print("   3. Verifica que la base de datos 'PSM' exista")
    else:
        print(f"   Error inesperado: {type(e).__name__}")

print("\n" + "=" * 60)