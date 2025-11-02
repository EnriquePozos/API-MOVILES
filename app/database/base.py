"""
Base declarativa de SQLAlchemy.
Todos los modelos heredarán de esta clase.
"""

from sqlalchemy.ext.declarative import declarative_base

# Base declarativa para todos los modelos
Base = declarative_base()

# Metadata compartida
metadata = Base.metadata