"""
Esquemas Pydantic para Publicacion.
Define la estructura de datos para requests y responses de recetas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.publicacion import EstatusPublicacion

# Imports para evitar referencias circulares
if TYPE_CHECKING:
    from .multimedia import MultimediaResponse
    from .comentario import ComentarioResponse


# ============================================
# ESQUEMA BASE
# ============================================
class PublicacionBase(BaseModel):
    """Campos base de Publicacion."""
    titulo: str = Field(..., min_length=5, max_length=255, description="Título de la receta")
    descripcion: Optional[str] = Field(None, description="Descripción e instrucciones de la receta")


# ============================================
# ESQUEMA PARA CREAR PUBLICACION (Request)
# ============================================
class PublicacionCreate(PublicacionBase):
    """
    Esquema para crear una publicación nueva.
    Por defecto se crea como borrador.
    """
    estatus: Optional[EstatusPublicacion] = Field(
        default=EstatusPublicacion.BORRADOR,
        description="Estado inicial (por defecto: borrador)"
    )
    
    @validator('titulo')
    def validar_titulo(cls, v):
        """Valida que el título no sea solo espacios."""
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()


# ============================================
# ESQUEMA PARA ACTUALIZAR PUBLICACION (Request)
# ============================================
class PublicacionUpdate(BaseModel):
    """
    Esquema para actualizar una publicación.
    Todos los campos son opcionales.
    """
    titulo: Optional[str] = Field(None, min_length=5, max_length=255)
    descripcion: Optional[str] = None
    estatus: Optional[EstatusPublicacion] = None
    
    @validator('titulo')
    def validar_titulo(cls, v):
        if v and not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class PublicacionResponse(PublicacionBase):
    """
    Esquema para retornar una publicación.
    Incluye campos generados y datos del autor.
    """
    id: str
    fecha_creacion: datetime
    fecha_publicacion: Optional[datetime] = None
    fecha_modificacion: Optional[datetime] = None
    estatus: EstatusPublicacion
    id_autor: str
    
    # Información del autor (nested)
    autor_alias: Optional[str] = None
    autor_foto: Optional[str] = None
    
    # Estadísticas
    total_comentarios: int = 0
    total_reacciones: int = 0
    total_favoritos: int = 0
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "titulo": "Tacos al Pastor Auténticos",
                "descripcion": "Receta tradicional de tacos al pastor...",
                "fecha_creacion": "2025-10-19T12:00:00",
                "fecha_publicacion": "2025-10-19T14:00:00",
                "fecha_modificacion": None,
                "estatus": "publicada",
                "id_autor": "660e8400-e29b-41d4-a716-446655440000",
                "autor_alias": "chef_123",
                "autor_foto": "https://res.cloudinary.com/...",
                "total_comentarios": 5,
                "total_reacciones": 12,
                "total_favoritos": 3
            }
        }


# ============================================
# ESQUEMA SIMPLIFICADO (para listas/feed)
# ============================================
class PublicacionSimple(BaseModel):
    """Esquema simplificado para feed de publicaciones."""
    id: str
    titulo: str
    descripcion: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    estatus: EstatusPublicacion
    id_autor: str
    autor_alias: Optional[str] = None
    autor_foto: Optional[str] = None
    total_comentarios: int = 0
    total_reacciones: int = 0
    
    # Primera imagen de multimedia (opcional)
    imagen_preview: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA CON MULTIMEDIA Y COMENTARIOS
# ============================================
class PublicacionDetalle(PublicacionResponse):
    """Esquema completo con multimedia y comentarios recientes."""
    multimedia: List['MultimediaResponse'] = []
    comentarios_recientes: List['ComentarioResponse'] = []
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA PARA PUBLICAR (cambiar de borrador a publicada)
# ============================================
class PublicacionPublicar(BaseModel):
    """Esquema para publicar un borrador."""
    pass  # No necesita datos, solo cambia el estatus