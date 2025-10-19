"""
Modelo Favorito.
Tabla asociativa entre Usuario y Publicacion (relación N:M).
Representa las publicaciones favoritas de cada usuario.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Favorito(Base):
    """
    Modelo de Favorito.
    Representa la relación muchos-a-muchos entre Usuario y Publicacion.
    
    Attributes:
        id_usuario: FK al usuario (parte de PK compuesta)
        id_publicacion: FK a la publicación (parte de PK compuesta)
        fecha_guardado: Fecha en que se guardó como favorito
    """
    
    __tablename__ = "Favoritos"
    
    # ============================================
    # COLUMNAS (Primary Key Compuesta)
    # ============================================
    id_usuario = Column(
        String(36),
        ForeignKey("Usuario.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que guardó el favorito"
    )
    
    id_publicacion = Column(
        String(36),
        ForeignKey("Publicacion.id", ondelete="CASCADE"),
        nullable=False,
        comment="Publicación guardada como favorita"
    )
    
    fecha_guardado = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Fecha en que se guardó como favorito"
    )
    
    # ============================================
    # PRIMARY KEY COMPUESTA
    # ============================================
    __table_args__ = (
        PrimaryKeyConstraint('id_usuario', 'id_publicacion', name='pk_favoritos'),
        Index('idx_favorito_usuario', 'id_usuario'),
        Index('idx_favorito_publicacion', 'id_publicacion'),
        Index('idx_favorito_fecha', 'fecha_guardado'),
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    usuario = relationship(
        "Usuario",
        back_populates="favoritos"
    )
    
    publicacion = relationship(
        "Publicacion",
        back_populates="favoritos"
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        return f"<Favorito(usuario_id={self.id_usuario}, publicacion_id={self.id_publicacion})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            "id_usuario": self.id_usuario,
            "id_publicacion": self.id_publicacion,
            "fecha_guardado": self.fecha_guardado.isoformat() if self.fecha_guardado else None,
        }