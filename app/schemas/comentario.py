"""
Esquemas Pydantic para Comentario.
Soporta comentarios jerárquicos (comentarios y respuestas).
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.comentario import EstatusComentario


# ============================================
# ESQUEMA BASE
# ============================================
class ComentarioBase(BaseModel):
    """Campos base de Comentario."""
    comentario: str = Field(..., min_length=1, max_length=1000, description="Texto del comentario")


# ============================================
# ESQUEMA PARA CREAR COMENTARIO (Request)
# ============================================
class ComentarioCreate(ComentarioBase):
    """
    Esquema para crear un comentario.
    Debe especificar si es comentario a publicación o respuesta a comentario.
    """
    id_publicacion: Optional[str] = Field(None, description="ID de la publicación (si es comentario raíz)")
    id_comentario: Optional[str] = Field(None, description="ID del comentario padre (si es respuesta)")
    
    @validator('comentario')
    def validar_comentario(cls, v):
        """Valida que el comentario no sea solo espacios."""
        if not v.strip():
            raise ValueError('El comentario no puede estar vacío')
        return v.strip()
    
    @validator('id_comentario')
    def validar_relacion(cls, v, values):
        """Valida que tenga publicación O comentario padre (no ambos, no ninguno)."""
        id_publicacion = values.get('id_publicacion')
        
        # Debe tener uno u otro
        if not id_publicacion and not v:
            raise ValueError('Debe especificar id_publicacion o id_comentario')
        
        # No puede tener ambos
        if id_publicacion and v:
            raise ValueError('No puede especificar ambos id_publicacion e id_comentario')
        
        return v


# ============================================
# ESQUEMA PARA ACTUALIZAR COMENTARIO (Request)
# ============================================
class ComentarioUpdate(BaseModel):
    """Esquema para editar un comentario."""
    comentario: str = Field(..., min_length=1, max_length=1000)
    
    @validator('comentario')
    def validar_comentario(cls, v):
        if not v.strip():
            raise ValueError('El comentario no puede estar vacío')
        return v.strip()


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class ComentarioResponse(ComentarioBase):
    """
    Esquema para retornar un comentario.
    Incluye información del usuario y estadísticas.
    """
    id: str
    estatus: EstatusComentario
    fecha_creacion: datetime
    id_usuario: str
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    
    # Información del usuario
    usuario_alias: Optional[str] = None
    usuario_foto: Optional[str] = None
    
    # Indicadores
    es_respuesta: bool = False
    total_respuestas: int = 0
    total_reacciones: int = 0
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "comentario": "¡Excelente receta! La probé y quedó deliciosa",
                "estatus": "activo",
                "fecha_creacion": "2025-10-19T15:00:00",
                "id_usuario": "660e8400-e29b-41d4-a716-446655440000",
                "id_publicacion": "550e8400-e29b-41d4-a716-446655440000",
                "id_comentario": None,
                "usuario_alias": "chef_123",
                "usuario_foto": "https://res.cloudinary.com/...",
                "es_respuesta": False,
                "total_respuestas": 2,
                "total_reacciones": 5
            }
        }


# ============================================
# ESQUEMA CON RESPUESTAS (jerárquico)
# ============================================
class ComentarioConRespuestas(ComentarioResponse):
    """Esquema de comentario con sus respuestas anidadas."""
    respuestas: List[ComentarioResponse] = []
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA SIMPLIFICADO
# ============================================
class ComentarioSimple(BaseModel):
    """Esquema simplificado para listas."""
    id: str
    comentario: str
    fecha_creacion: datetime
    usuario_alias: Optional[str] = None
    total_respuestas: int = 0
    
    class Config:
        from_attributes = True