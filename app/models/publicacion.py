"""
Modelo Publicacion (Recetas).
Representa la tabla Publicacion en la base de datos.
"""

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import uuid
import enum


class EstatusPublicacion(str, enum.Enum):
    """Enum para los estatus de publicación."""
    PUBLICADA = "publicada"
    BORRADOR = "borrador"
    ELIMINADA = "eliminada"


class Publicacion(Base):
    """
    Modelo de Publicacion (Recetas).
    
    Attributes:
        id: UUID único de la publicación
        titulo: Título de la receta
        descripcion: Descripción/instrucciones de la receta
        fecha_creacion: Fecha de creación automática
        fecha_publicacion: Fecha en que se publicó
        fecha_modificacion: Fecha de última modificación
        estatus: Estado (publicada, borrador, eliminada)
        id_autor: FK al usuario autor
    """
    
    __tablename__ = "Publicacion"
    
    # ============================================
    # COLUMNAS
    # ============================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID único de la publicación"
    )
    
    titulo = Column(
        String(255),
        nullable=False,
        comment="Título de la receta"
    )
    
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción e instrucciones de la receta"
    )
    
    fecha_creacion = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Fecha de creación automática"
    )
    
    fecha_publicacion = Column(
        DateTime,
        nullable=True,
        comment="Fecha en que se publicó (NULL si es borrador)"
    )
    
    fecha_modificacion = Column(
        DateTime,
        default=None,
        onupdate=func.now(),  # Se actualiza automáticamente al modificar
        nullable=True,
        comment="Fecha de última modificación"
    )
    
    estatus = Column(
        Enum(EstatusPublicacion),
        default=EstatusPublicacion.BORRADOR,
        nullable=False,
        comment="Estado: publicada, borrador, eliminada"
    )
    
    # ============================================
    # FOREIGN KEYS
    # ============================================
    id_autor = Column(
        String(36),
        ForeignKey("Usuario.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID del usuario autor"
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    # Relación con Usuario (muchas publicaciones → un autor)
    autor = relationship(
        "Usuario",
        back_populates="publicaciones"
    )
    
    # Una publicación tiene muchos comentarios
    comentarios = relationship(
        "Comentario",
        back_populates="publicacion",
        cascade="all, delete-orphan"
    )
    
    # Una publicación tiene muchas reacciones
    reacciones = relationship(
        "Reaccion",
        back_populates="publicacion",
        cascade="all, delete-orphan"
    )
    
    # Una publicación tiene muchas imágenes/videos
    multimedia = relationship(
        "Multimedia",
        back_populates="publicacion",
        cascade="all, delete-orphan"
    )
    
    # Una publicación tiene muchos favoritos
    favoritos = relationship(
        "Favorito",
        back_populates="publicacion",
        cascade="all, delete-orphan"
    )
    
    # ============================================
    # ÍNDICES
    # ============================================
    __table_args__ = (
        Index('idx_estatus', 'estatus'),
        Index('idx_autor', 'id_autor'),
        Index('idx_fecha_publicacion', 'fecha_publicacion'),
        Index('idx_titulo', 'titulo'),
        Index('idx_descripcion', 'descripcion', mysql_prefix='FULLTEXT'),  # Solo MySQL
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        return f"<Publicacion(id={self.id}, titulo={self.titulo}, estatus={self.estatus})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            "fecha_modificacion": self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            "estatus": self.estatus.value if self.estatus else None,
            "id_autor": self.id_autor
        }
    
    def publicar(self):
        """Cambia el estatus a publicada y guarda fecha de publicación."""
        self.estatus = EstatusPublicacion.PUBLICADA
        self.fecha_publicacion = func.now()
    
    def eliminar_logicamente(self):
        """Soft delete: marca como eliminada sin borrar de BD."""
        self.estatus = EstatusPublicacion.ELIMINADA