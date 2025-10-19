"""
Modelo Multimedia.
Almacena URLs de imágenes y videos (Cloudinary) asociados a publicaciones.
"""

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import uuid
import enum


class TipoMultimedia(str, enum.Enum):
    """Enum para tipos de multimedia."""
    IMAGEN = "imagen"
    VIDEO = "video"


class Multimedia(Base):
    """
    Modelo de Multimedia.
    Almacena URLs de Cloudinary para imágenes/videos de publicaciones.
    
    Attributes:
        id: UUID único del archivo multimedia
        url: URL de Cloudinary
        tipo: Tipo (imagen, video)
        fecha_subida: Fecha de subida automática
        id_publicacion: FK a la publicación asociada
    """
    
    __tablename__ = "Multimedia"
    
    # ============================================
    # COLUMNAS
    # ============================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID único del archivo multimedia"
    )
    
    url = Column(
        String(500),
        nullable=False,
        comment="URL de Cloudinary (puede ser larga)"
    )
    
    tipo = Column(
        Enum(TipoMultimedia),
        default=TipoMultimedia.IMAGEN,
        nullable=False,
        comment="Tipo: imagen o video"
    )
    
    fecha_subida = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Fecha de subida automática"
    )
    
    # ============================================
    # FOREIGN KEYS
    # ============================================
    id_publicacion = Column(
        String(36),
        ForeignKey("Publicacion.id", ondelete="CASCADE"),
        nullable=False,
        comment="Publicación asociada"
    )
    
    # ============================================
    # RELACIONES (ORM)
    # ============================================
    publicacion = relationship(
        "Publicacion",
        back_populates="multimedia"
    )
    
    # ============================================
    # ÍNDICES
    # ============================================
    __table_args__ = (
        Index('idx_multimedia_publicacion', 'id_publicacion'),
    )
    
    # ============================================
    # MÉTODOS ÚTILES
    # ============================================
    def __repr__(self):
        return f"<Multimedia(id={self.id}, tipo={self.tipo}, publicacion_id={self.id_publicacion})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "url": self.url,
            "tipo": self.tipo.value if self.tipo else None,
            "fecha_subida": self.fecha_subida.isoformat() if self.fecha_subida else None,
            "id_publicacion": self.id_publicacion,
            "es_imagen": self.tipo == TipoMultimedia.IMAGEN,
            "es_video": self.tipo == TipoMultimedia.VIDEO,
        }
    
    def es_imagen(self):
        """Verifica si es una imagen."""
        return self.tipo == TipoMultimedia.IMAGEN
    
    def es_video(self):
        """Verifica si es un video."""
        return self.tipo == TipoMultimedia.VIDEO
    
    def obtener_thumbnail(self):
        """
        Genera URL de thumbnail para videos de Cloudinary.
        Para imágenes, retorna la URL original.
        """
        if self.es_video():
            # Cloudinary permite generar thumbnails de videos
            # Ejemplo: video.mp4 → video.jpg
            return self.url.replace('.mp4', '.jpg').replace('.mov', '.jpg')
        return self.url