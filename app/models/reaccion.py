"""
Modelo Reaccion.
Permite likes y dislikes a publicaciones y comentarios.
"""

from sqlalchemy import Column, String, Enum, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base
import uuid
import enum


class TipoReaccion(str, enum.Enum):
    """Enum para tipos de reacción."""
    LIKE = "like"
    DISLIKE = "dislike"


class Reaccion(Base):
    """
    Modelo de Reaccion.
    Una reacción puede ser a una publicación O a un comentario (no ambos).
    
    Attributes:
        id: UUID único de la reacción
        reaccion: Tipo (like, dislike)
        id_usuario: FK al usuario que reaccionó
        id_publicacion: FK a la publicación (si reacciona a publicación)
        id_comentario: FK al comentario (si reacciona a comentario)
    """
    
    __tablename__ = "Reaccion"
    
    # ============================================
    # COLUMNAS
    # ============================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID único de la reacción"
    )
    
    reaccion = Column(
        Enum(TipoReaccion),
        nullable=False,
        comment="Tipo de reacción: like o dislike"
    )
    
    # ============================================
    # FOREIGN KEYS
    # ============================================
    id_usuario = Column(
        String(36),
        ForeignKey("Usuario.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que reaccionó"
    )
    
    id_publicacion = Column(
        String(36),
        ForeignKey("Publicacion.id", ondelete="CASCADE"),
        nullable=True,
        comment="Publicación reaccionada (NULL si es a comentario)"
    )
    
    id_comentario = Column(
        String(36),
        ForeignKey("Comentario.id", ondelete="CASCADE"),
        nullable=True,
        comment="Comentario reaccionado (NULL si es a publicación)"
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    usuario = relationship(
        "Usuario",
        back_populates="reacciones"
    )
    
    publicacion = relationship(
        "Publicacion",
        back_populates="reacciones"
    )
    
    comentario = relationship(
        "Comentario",
        back_populates="reacciones"
    )
    
    # ============================================
    # CONSTRAINTS E ÍNDICES
    # ============================================
    __table_args__ = (
        # CHECK: Debe reaccionar a publicación O comentario (no ambos, no ninguno)
        CheckConstraint(
            "(id_publicacion IS NOT NULL AND id_comentario IS NULL) OR "
            "(id_publicacion IS NULL AND id_comentario IS NOT NULL)",
            name="check_reaccion_a"
        ),
        
        # UNIQUE: Un usuario solo puede reaccionar una vez por publicación
        UniqueConstraint(
            'id_usuario', 
            'id_publicacion',
            name='unique_reaccion_publicacion'
        ),
        
        # UNIQUE: Un usuario solo puede reaccionar una vez por comentario
        UniqueConstraint(
            'id_usuario', 
            'id_comentario',
            name='unique_reaccion_comentario'
        ),
        
        Index('idx_reaccion_publicacion', 'id_publicacion'),
        Index('idx_comentario', 'id_comentario'),
        Index('idx_usuario', 'id_usuario'),
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        tipo = "publicación" if self.id_publicacion else "comentario"
        return f"<Reaccion(id={self.id}, tipo={self.reaccion}, a={tipo})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "reaccion": self.reaccion.value if self.reaccion else None,
            "id_usuario": self.id_usuario,
            "id_publicacion": self.id_publicacion,
            "id_comentario": self.id_comentario,
            "es_like": self.reaccion == TipoReaccion.LIKE,
            "es_dislike": self.reaccion == TipoReaccion.DISLIKE,
        }
    
    def cambiar_reaccion(self):
        """Cambia la reacción (like ↔ dislike)."""
        if self.reaccion == TipoReaccion.LIKE:
            self.reaccion = TipoReaccion.DISLIKE
        else:
            self.reaccion = TipoReaccion.LIKE
    
    def es_like(self):
        """Verifica si es un like."""
        return self.reaccion == TipoReaccion.LIKE
    
    def es_dislike(self):
        """Verifica si es un dislike."""
        return self.reaccion == TipoReaccion.DISLIKE