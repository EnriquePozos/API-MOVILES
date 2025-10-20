"""
Esquemas Pydantic para Reaccion.
Permite likes/dislikes a publicaciones y comentarios.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from app.models.reaccion import TipoReaccion


# ============================================
# ESQUEMA BASE
# ============================================
class ReaccionBase(BaseModel):
    """Campos base de Reaccion."""
    reaccion: TipoReaccion = Field(..., description="Tipo de reacción: like o dislike")


# ============================================
# ESQUEMA PARA CREAR REACCION (Request)
# ============================================
class ReaccionCreate(ReaccionBase):
    """
    Esquema para crear una reacción.
    Debe especificar si es a publicación o a comentario.
    """
    id_publicacion: Optional[str] = Field(None, description="ID de la publicación (si reacciona a publicación)")
    id_comentario: Optional[str] = Field(None, description="ID del comentario (si reacciona a comentario)")
    
    @validator('id_comentario')
    def validar_relacion(cls, v, values):
        """Valida que tenga publicación O comentario (no ambos, no ninguno)."""
        id_publicacion = values.get('id_publicacion')
        
        # Debe tener uno u otro
        if not id_publicacion and not v:
            raise ValueError('Debe especificar id_publicacion o id_comentario')
        
        # No puede tener ambos
        if id_publicacion and v:
            raise ValueError('No puede especificar ambos id_publicacion e id_comentario')
        
        return v


# ============================================
# ESQUEMA PARA ACTUALIZAR REACCION (Request)
# ============================================
class ReaccionUpdate(BaseModel):
    """
    Esquema para cambiar una reacción existente.
    Permite cambiar de like a dislike o viceversa.
    """
    reaccion: TipoReaccion = Field(..., description="Nuevo tipo de reacción")


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class ReaccionResponse(ReaccionBase):
    """Esquema para retornar una reacción."""
    id: str
    id_usuario: str
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    
    # Información del usuario
    usuario_alias: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "reaccion": "like",
                "id_usuario": "660e8400-e29b-41d4-a716-446655440000",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000",
                "id_comentario": None,
                "usuario_alias": "chef_123"
            }
        }


# ============================================
# ESQUEMA SIMPLIFICADO
# ============================================
class ReaccionSimple(BaseModel):
    """Esquema simplificado para contar reacciones."""
    total_likes: int = 0
    total_dislikes: int = 0
    reaccion_usuario: Optional[TipoReaccion] = None  # Reacción del usuario actual
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA PARA TOGGLE (like/unlike)
# ============================================
class ReaccionToggle(BaseModel):
    """
    Esquema para hacer toggle de reacción.
    Si existe, la elimina. Si no existe, la crea.
    """
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    
    @validator('id_comentario')
    def validar_relacion(cls, v, values):
        id_publicacion = values.get('id_publicacion')
        if not id_publicacion and not v:
            raise ValueError('Debe especificar id_publicacion o id_comentario')
        if id_publicacion and v:
            raise ValueError('No puede especificar ambos')
        return v