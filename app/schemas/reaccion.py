"""
Schemas de Reaccion.
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.models.reaccion import TipoReaccion


# ============================================
# ESQUEMA BASE
# ============================================
class ReaccionBase(BaseModel):
    """Campos base de Reaccion."""
    reaccion: TipoReaccion = Field(..., description="Tipo de reacción")
    
class ReaccionComment(ReaccionBase):
    """Campos base de Reaccion para comentarios."""
    id_usuario: str = Field(..., description="ID del usuario que reacciona")
    id_comentario: str = Field(..., description="ID del comentario al que se reacciona")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_usuario": "660e8400-e29b-41d4-a716-446655440000",
                "id_comentario": "550e8400-e29b-41d4-a716-446655440000",
                "tipo_reaccion": "like"
            }
        }
    


# ============================================
# ESQUEMA PARA CREAR REACCION (Request)
# ============================================
class ReaccionCreate(ReaccionBase):
    """Esquema para crear una reacción."""
    pass


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class ReaccionResponse(BaseModel):
    """Esquema genérico de respuesta para reacciones."""
    id_usuario: str
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    tipo_reaccion: TipoReaccion
    publicacion_titulo: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_usuario": "660e8400-e29b-41d4-a716-446655440000",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000",
                "id_comentario": None,
                "tipo_reaccion": "like",
                "publicacion_titulo": "Tacos al Pastor"
            }
        }