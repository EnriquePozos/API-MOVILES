"""
Script para crear todas las tablas en MySQL.
Ejecutar: python create_tables_mysql.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base
from app.database.connection import engine_local, engine_prod, DB_ENV
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario
from app.models.reaccion import Reaccion
from app.models.multimedia import Multimedia
from app.models.favorito import Favorito

print("=" * 60)
print("🚀 CREACIÓN DE TABLAS EN MYSQL")
print("=" * 60)

print(f"\n📌 Entorno configurado: {DB_ENV}")

# Preguntar confirmación
print("\n⚠️  ADVERTENCIA:")
print("   Este script creará todas las tablas en MySQL.")
print("   Si las tablas ya existen, NO las modificará.")
print("   Para modificar tablas existentes, usa Alembic.")

respuesta = input("\n¿Continuar? (s/n): ").lower()

if respuesta != 's':
    print("\n❌ Operación cancelada")
    sys.exit(0)

# Decidir qué base de datos usar
if DB_ENV == 'prod':
    print("\n🌐 Creando tablas en MySQL PRODUCCIÓN (Railway)...")
    engine = engine_prod
    if not engine:
        print("❌ Error: Engine de producción no configurado")
        sys.exit(1)
elif DB_ENV == 'local':
    print("\n💻 Creando tablas en MySQL LOCAL...")
    engine = engine_local
else:
    print(f"❌ Error: DB_ENV={DB_ENV} no es válido para MySQL")
    print("   Debe ser 'local' o 'prod'")
    sys.exit(1)

try:
    # Crear todas las tablas
    print("\n🔨 Ejecutando CREATE TABLE...")
    Base.metadata.create_all(bind=engine)
    print("✅ Comando ejecutado exitosamente")
    
    # Verificar tablas creadas
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    
    if tablas:
        print(f"\n✅ {len(tablas)} tablas verificadas en MySQL:")
        for tabla in tablas:
            columnas = inspector.get_columns(tabla)
            indices = inspector.get_indexes(tabla)
            fks = inspector.get_foreign_keys(tabla)
            
            print(f"\n   📋 {tabla}")
            print(f"      Columnas: {len(columnas)}")
            print(f"      Índices: {len(indices)}")
            print(f"      Foreign Keys: {len(fks)}")
            
            # Mostrar columnas
            for col in columnas:
                tipo = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"         - {col['name']}: {tipo} {nullable}")
    else:
        print("\n⚠️  No se encontraron tablas")
        
except Exception as e:
    print(f"\n❌ Error al crear tablas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ PROCESO COMPLETADO")
print("=" * 60)
# print("\n💡 Próximos pasos:")
# print("   1. Verifica las tablas en MySQL Workbench o phpMyAdmin")
# print("   2. Configura Alembic para migraciones futuras")
# print("   3. Crea los esquemas Pydantic para validación")
# print("=" * 60)