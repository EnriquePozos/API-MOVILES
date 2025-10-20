"""
Esquemas Pydantic para Favorito.
Relación N:M entre Usuario y Publicacion.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================
# ESQUEMA BASE
# ============================================
class FavoritoBase(BaseModel):
    """Campos base de Favorito."""
    id_publicacion: str = Field(..., description="ID de la publicación a guardar")


# ============================================
# ESQUEMA PARA CREAR FAVORITO (Request)
# ============================================
class FavoritoCreate(FavoritoBase):
    """
    Esquema para agregar una publicación a favoritos.
    El id_usuario se obtiene del token de autenticación.
    """
    pass


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class FavoritoResponse(FavoritoBase):
    """Esquema para retornar un favorito."""
    id_usuario: str
    fecha_guardado: datetime
    
    # Información de la publicación (nested)
    publicacion_titulo: Optional[str] = None
    publicacion_imagen: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_usuario": "660e8400-e29b-41d4-a716-446655440000",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000",
                "fecha_guardado": "2025-10-19T16:00:00",
                "publicacion_titulo": "Tacos al Pastor",
                "publicacion_imagen": "https://res.cloudinary.com/..."
            }
        }


# ============================================
# ESQUEMA SIMPLIFICADO (con info de publicación)
# ============================================
class FavoritoConPublicacion(BaseModel):
    """Esquema de favorito con información completa de la publicación."""
    from .publicacion import PublicacionSimple
    
    fecha_guardado: datetime
    publicacion: PublicacionSimple
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA PARA VERIFICAR SI ES FAVORITO
# ============================================
class FavoritoCheck(BaseModel):
    """Esquema para verificar si una publicación está en favoritos."""
    id_publicacion: str
    es_favorito: bool
    fecha_guardado: Optional[datetime] = None