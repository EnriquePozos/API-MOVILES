"""
Esquemas Pydantic para Multimedia.
Maneja URLs de imágenes y videos de Cloudinary.
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
from app.models.multimedia import TipoMultimedia


# ============================================
# ESQUEMA BASE
# ============================================
class MultimediaBase(BaseModel):
    """Campos base de Multimedia."""
    url: str = Field(..., max_length=500, description="URL de Cloudinary")
    tipo: TipoMultimedia = Field(default=TipoMultimedia.IMAGEN, description="Tipo: imagen o video")
    
    @validator('url')
    def validar_url(cls, v):
        """Valida que la URL no esté vacía."""
        if not v.strip():
            raise ValueError('La URL no puede estar vacía')
        return v.strip()


# ============================================
# ESQUEMA PARA CREAR MULTIMEDIA (Request)
# ============================================
class MultimediaCreate(MultimediaBase):
    """
    Esquema para crear multimedia asociada a una publicación.
    """
    id_publicacion: str = Field(..., description="ID de la publicación asociada")


# ============================================
# ESQUEMA PARA ACTUALIZAR MULTIMEDIA (Request)
# ============================================
class MultimediaUpdate(BaseModel):
    """
    Esquema para actualizar multimedia.
    Solo permite cambiar la URL.
    """
    url: str = Field(..., max_length=500)
    
    @validator('url')
    def validar_url(cls, v):
        if not v.strip():
            raise ValueError('La URL no puede estar vacía')
        return v.strip()


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class MultimediaResponse(MultimediaBase):
    """Esquema para retornar multimedia."""
    id: str
    fecha_subida: datetime
    id_publicacion: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "990e8400-e29b-41d4-a716-446655440000",
                "url": "https://res.cloudinary.com/demo/image/upload/v1234567890/receta.jpg",
                "tipo": "imagen",
                "fecha_subida": "2025-10-19T12:00:00",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


# ============================================
# ESQUEMA SIMPLIFICADO
# ============================================
class MultimediaSimple(BaseModel):
    """Esquema simplificado para listas."""
    id: str
    url: str
    tipo: TipoMultimedia
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA PARA SUBIR ARCHIVO (antes de Cloudinary)
# ============================================
class MultimediaUpload(BaseModel):
    """
    Esquema para iniciar subida de archivo.
    En el endpoint recibirás el archivo y lo subirás a Cloudinary.
    """
    tipo: TipoMultimedia = Field(default=TipoMultimedia.IMAGEN)
    id_publicacion: str = Field(..., description="ID de la publicación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "imagen",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000"
            }
        }