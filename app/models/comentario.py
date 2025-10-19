"""
Modelo Comentario.
Soporta comentarios jerárquicos (comentarios y respuestas).
"""

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import uuid
import enum


class EstatusComentario(str, enum.Enum):
    """Enum para el estatus del comentario."""
    ACTIVO = "activo"
    ELIMINADO = "eliminado"


class Comentario(Base):
    """
    Modelo de Comentario.
    Soporta jerarquía: comentarios a publicaciones y respuestas a comentarios.
    
    Attributes:
        id: UUID único del comentario
        estatus: Estado (activo, eliminado)
        comentario: Texto del comentario
        fecha_creacion: Fecha de creación automática
        id_usuario: FK al usuario que comentó
        id_publicacion: FK a la publicación (si es comentario raíz)
        id_comentario: FK al comentario padre (si es respuesta)
    """
    
    __tablename__ = "Comentario"
    
    # ============================================
    # COLUMNAS
    # ============================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID único del comentario"
    )
    
    estatus = Column(
        Enum(EstatusComentario),
        default=EstatusComentario.ACTIVO,
        nullable=False,
        comment="Estado: activo, eliminado"
    )
    
    comentario = Column(
        Text,
        nullable=False,
        comment="Texto del comentario"
    )
    
    fecha_creacion = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Fecha de creación automática"
    )
    
    # ============================================
    # FOREIGN KEYS
    # ============================================
    id_usuario = Column(
        String(36),
        ForeignKey("Usuario.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que hizo el comentario"
    )
    
    id_publicacion = Column(
        String(36),
        ForeignKey("Publicacion.id", ondelete="CASCADE"),
        nullable=True,
        comment="Publicación comentada (NULL si es respuesta)"
    )
    
    # Self-join: un comentario puede tener un comentario padre
    id_comentario = Column(
        String(36),
        ForeignKey("Comentario.id", ondelete="CASCADE"),
        nullable=True,
        comment="Comentario padre (NULL si es comentario raíz)"
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    # Relación con Usuario
    usuario = relationship(
        "Usuario",
        back_populates="comentarios"
    )
    
    # Relación con Publicacion
    publicacion = relationship(
        "Publicacion",
        back_populates="comentarios"
    )
    
    # Self-join: comentarios padre e hijos
    # Un comentario puede tener muchas respuestas
    respuestas = relationship(
        "Comentario",
        back_populates="comentario_padre",
        cascade="all, delete-orphan",
        foreign_keys=[id_comentario]
    )
    
    # Un comentario puede tener un padre
    comentario_padre = relationship(
        "Comentario",
        back_populates="respuestas",
        remote_side=[id],
        foreign_keys=[id_comentario]
    )
    
    # Un comentario tiene muchas reacciones
    reacciones = relationship(
        "Reaccion",
        back_populates="comentario",
        cascade="all, delete-orphan"
    )
    
    # ============================================
    # CONSTRAINTS E ÍNDICES
    # ============================================
    __table_args__ = (
        # CHECK: Debe tener publicación O comentario padre (no ambos, no ninguno)
        CheckConstraint(
            "(id_publicacion IS NOT NULL AND id_comentario IS NULL) OR "
            "(id_publicacion IS NULL AND id_comentario IS NOT NULL)",
            name="check_comentario_pertenece_a"
        ),
        Index('idx_comentario_publicacion', 'id_publicacion'),
        Index('idx_comentario_padre', 'id_comentario'),
        Index('idx_comentario_usuario', 'id_usuario'),
        Index('idx_comentario_fecha', 'fecha_creacion'),
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        tipo = "respuesta" if self.id_comentario else "comentario"
        return f"<Comentario(id={self.id}, tipo={tipo}, estatus={self.estatus})>"
    
    def to_dict(self, incluir_respuestas=False):
        """Convierte el modelo a diccionario."""
        data = {
            "id": self.id,
            "estatus": self.estatus.value if self.estatus else None,
            "comentario": self.comentario,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "id_usuario": self.id_usuario,
            "id_publicacion": self.id_publicacion,
            "id_comentario": self.id_comentario,
            "es_respuesta": self.id_comentario is not None
        }
        
        # Incluir respuestas si se solicita
        if incluir_respuestas and self.respuestas:
            data["respuestas"] = [r.to_dict(incluir_respuestas=False) for r in self.respuestas]
        
        return data
    
    def eliminar_logicamente(self):
        """Soft delete: marca como eliminado sin borrar de BD."""
        self.estatus = EstatusComentario.ELIMINADO
        self.comentario = "[Comentario eliminado]"
    
    def es_comentario_raiz(self):
        """Verifica si es un comentario raíz (no es respuesta)."""
        return self.id_comentario is None
    
    def es_respuesta(self):
        """Verifica si es una respuesta a otro comentario."""
        return self.id_comentario is not None