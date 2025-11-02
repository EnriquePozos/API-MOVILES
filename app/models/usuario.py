"""
Modelo Usuario.
Representa la tabla Usuario en la base de datos.
"""

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import uuid


class Usuario(Base):
    """
    Modelo de Usuario.
    
    Attributes:
        id: UUID único del usuario (Primary Key)
        email: Correo electrónico único
        alias: Nombre de usuario único
        contraseña: Hash de la contraseña (bcrypt)
        nombre: Nombre del usuario
        apellido_paterno: Apellido paterno
        apellido_materno: Apellido materno
        telefono: Número de teléfono
        direccion: Dirección del usuario
        fecha_registro: Fecha de registro automática
        foto_perfil: URL de Cloudinary
    """
    
    __tablename__ = "Usuario"
    
    # ============================================
    # COLUMNAS
    # ============================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # Genera UUID automáticamente
        comment="UUID único del usuario"
    )
    
    email = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Correo electrónico único"
    )
    
    alias = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Nombre de usuario único"
    )
    
    contraseña = Column(
        String(100),
        nullable=False,
        comment="Hash de contraseña (bcrypt)"
    )
    
    nombre = Column(
        String(255),
        nullable=True,
        comment="Nombre del usuario"
    )
    
    apellido_paterno = Column(
        String(255),
        nullable=True
    )
    
    apellido_materno = Column(
        String(255),
        nullable=True
    )
    
    telefono = Column(
        String(20),
        nullable=True
    )
    
    direccion = Column(
        String(150),
        nullable=True
    )
    
    fecha_registro = Column(
        DateTime,
        default=func.now(),  # CURRENT_TIMESTAMP automático
        nullable=False,
        comment="Fecha de registro automática"
    )
    
    foto_perfil = Column(
        String(500),
        nullable=True,
        comment="URL de Cloudinary para foto de perfil"
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    # Un usuario tiene muchas publicaciones
    publicaciones = relationship(
        "Publicacion",
        back_populates="autor",
        cascade="all, delete-orphan"  # Si borras usuario, borras sus publicaciones
    )
    
    # Un usuario tiene muchos comentarios
    comentarios = relationship(
        "Comentario",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    
    # Un usuario tiene muchas reacciones
    reacciones = relationship(
        "Reaccion",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    
    # Un usuario tiene muchos favoritos
    favoritos = relationship(
        "Favorito",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    
    # ============================================
    # ÍNDICES (Performance)
    # ============================================
    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_alias', 'alias'),
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        """Representación string del objeto."""
        return f"<Usuario(id={self.id}, alias={self.alias}, email={self.email})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario (útil para JSON)."""
        return {
            "id": self.id,
            "email": self.email,
            "alias": self.alias,
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "foto_perfil": self.foto_perfil
        }