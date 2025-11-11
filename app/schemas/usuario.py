"""
Esquemas Pydantic para Usuario.
Define la estructura de datos para requests y responses.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============================================
# ESQUEMA BASE (campos comunes)
# ============================================
class UsuarioBase(BaseModel):
    """Campos base de Usuario (sin contraseña)."""
    email: EmailStr = Field(..., description="Correo electrónico único")
    alias: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario único")
    nombre: Optional[str] = Field(None, max_length=255)
    apellido_paterno: Optional[str] = Field(None, max_length=255)
    apellido_materno: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=150)
    foto_perfil: Optional[str] = Field(None, max_length=500, description="URL de Cloudinary")


# ============================================
# ESQUEMA PARA CREAR USUARIO (Request)
# ============================================
class UsuarioCreate(UsuarioBase):
    """
    Esquema para crear un usuario nuevo.
    Incluye contraseña (que luego se hasheará).
    """
    contraseña: str = Field(
        ..., 
        min_length=10, 
        max_length=100, 
        description="Contraseña (mínimo 10 caracteres, debe incluir mayúscula, minúscula y número)"
    )
    
    @validator('contraseña')
    def validar_contraseña(cls, v):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad:
        - Mínimo 10 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        """
        if len(v) < 10:
            raise ValueError('La contraseña debe tener al menos 10 caracteres')
        
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        return v
    
    @validator('alias')
    def validar_alias(cls, v):
        """Valida que el alias no contenga espacios ni caracteres especiales."""
        if not v.replace('_', '').isalnum():
            raise ValueError('El alias solo puede contener letras, números y guiones bajos')
        return v.lower()  # Convertir a minúsculas
    
    @validator('email')
    def validar_email(cls, v):
        """Convierte el email a minúsculas."""
        return v.lower()


# ============================================
# ESQUEMA PARA ACTUALIZAR USUARIO (Request)
# ============================================
class UsuarioUpdate(BaseModel):
    """
    Esquema para actualizar un usuario.
    Todos los campos son opcionales.
    """
    email: Optional[EmailStr] = None
    alias: Optional[str] = Field(None, min_length=3, max_length=100)
    nombre: Optional[str] = Field(None, max_length=255)
    apellido_paterno: Optional[str] = Field(None, max_length=255)
    apellido_materno: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=150)
    foto_perfil: Optional[str] = Field(None, max_length=500)
    
    @validator('alias')
    def validar_alias(cls, v):
        if v and not v.isalnum() and '_' not in v:
            raise ValueError('El alias solo puede contener letras, números y guiones bajos')
        return v.lower() if v else v


# ============================================
# ESQUEMA PARA CAMBIAR CONTRASEÑA
# ============================================
class UsuarioCambiarContraseña(BaseModel):
    """Esquema para cambiar la contraseña."""
    contraseña_actual: str = Field(..., description="Contraseña actual")
    contraseña_nueva: str = Field(
        ..., 
        min_length=10, 
        max_length=100, 
        description="Nueva contraseña (mínimo 10 caracteres, debe incluir mayúscula, minúscula y número)"
    )
    
    @validator('contraseña_nueva')
    def validar_contraseña_nueva(cls, v, values):
        """Valida que la nueva contraseña cumpla requisitos y sea diferente a la actual."""
        # Verificar longitud
        if len(v) < 10:
            raise ValueError('La contraseña debe tener al menos 10 caracteres')
        
        # Verificar mayúscula
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        # Verificar minúscula
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        # Verificar número
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        # Verificar que sea diferente a la actual
        if 'contraseña_actual' in values and v == values['contraseña_actual']:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        
        return v


# ============================================
# ESQUEMA DE RESPUESTA (Response)
# ============================================
class UsuarioResponse(UsuarioBase):
    """
    Esquema para retornar un usuario.
    Incluye campos generados por la BD (id, fecha_registro).
    NO incluye contraseña.
    """
    id: str
    fecha_registro: datetime
    
    class Config:
        from_attributes = True  # Permite crear desde modelo SQLAlchemy
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "usuario@example.com",
                "alias": "chef_123",
                "nombre": "Juan",
                "apellido_paterno": "Pérez",
                "apellido_materno": "García",
                "telefono": "1234567890",
                "direccion": "Calle Principal 123",
                "fecha_registro": "2025-10-19T12:00:00",
                "foto_perfil": "https://res.cloudinary.com/..."
            }
        }


# ============================================
# ESQUEMA SIMPLIFICADO (para listas)
# ============================================
class UsuarioSimple(BaseModel):
    """Esquema simplificado para listas de usuarios."""
    id: str
    alias: str
    foto_perfil: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA CON ESTADÍSTICAS (para perfil)
# ============================================
class UsuarioPerfil(UsuarioResponse):
    """Esquema extendido con estadísticas del usuario."""
    total_publicaciones: int = 0
    total_comentarios: int = 0
    total_favoritos: int = 0
    
    class Config:
        from_attributes = True