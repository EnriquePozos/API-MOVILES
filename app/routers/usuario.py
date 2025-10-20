"""
Router de Usuario.
Define los endpoints HTTP para operaciones de usuario.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioPerfil,
    UsuarioUpdate,
    UsuarioCambiarContraseña
)
from app.repositories.usuario import (
    crear_usuario,
    login_usuario,
    get_perfil_usuario,
    get_usuario_by_id,
    actualizar_usuario,
    cambiar_contraseña as cambiar_contraseña_repo,
    eliminar_usuario as eliminar_usuario_repo
)

import app.repositories.usuario as usuario_repo

from app.utils.auth import create_access_token
from datetime import timedelta

# Crear router
router = APIRouter()


# ============================================
# POST - REGISTRO DE USUARIO
# ============================================

@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario. El email y alias deben ser únicos."
)
def registrar_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **alias**: Nombre de usuario único
    - **contraseña**: Mínimo 10 caracteres, debe incluir mayúscula, minúscula y número
    
    Returns:
        Usuario creado (sin contraseña)
    """
    try:
        nuevo_usuario = crear_usuario(db, data)
        return nuevo_usuario
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


# ============================================
# POST - LOGIN
# ============================================

@router.post(
    "/login",
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un JWT token"
)
def login_usuario(
    email: str,
    contraseña: str,
    db: Session = Depends(get_db)
):
    """
    Inicia sesión con email y contraseña.
    
    - **email**: Email del usuario
    - **contraseña**: Contraseña del usuario
    
    Returns:
        - access_token: JWT token para autenticación
        - token_type: Tipo de token (bearer)
        - usuario: Datos del usuario
    """
    # Autenticar usuario
    usuario = usuario_repo.login_usuario(db, email, contraseña)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear JWT token
    access_token = create_access_token(
        data={"sub": usuario.id},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "alias": usuario.alias,
            "nombre": usuario.nombre,
            "foto_perfil": usuario.foto_perfil
        }
    }


# ============================================
# GET - OBTENER PERFIL DE USUARIO
# ============================================

@router.get(
    "/perfil/{usuario_id}",
    response_model=UsuarioPerfil,
    summary="Obtener perfil de usuario",
    description="Obtiene el perfil completo de un usuario con sus estadísticas"
)
def get_perfil_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil de un usuario por su ID.
    
    - **usuario_id**: ID del usuario
    
    Returns:
        Perfil del usuario con estadísticas (publicaciones, comentarios, favoritos)
    """
    perfil = usuario_repo.get_perfil_usuario(db, usuario_id)
    
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Agregar estadísticas al usuario
    usuario = perfil["usuario"]
    usuario_dict = usuario.__dict__.copy()
    usuario_dict["total_publicaciones"] = perfil["total_publicaciones"]
    usuario_dict["total_comentarios"] = perfil["total_comentarios"]
    usuario_dict["total_favoritos"] = perfil["total_favoritos"]
    
    return usuario_dict


# ============================================
# GET - OBTENER USUARIO POR ID
# ============================================

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID",
    description="Obtiene los datos básicos de un usuario"
)
def get_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene un usuario por su ID.
    
    - **usuario_id**: ID del usuario
    
    Returns:
        Datos del usuario (sin contraseña)
    """
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


# ============================================
# PUT - ACTUALIZAR USUARIO
# ============================================

@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario"
)
def actualizar_usuario(
    usuario_id: str,
    data: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un usuario.
    
    - **usuario_id**: ID del usuario a actualizar
    - Solo se actualizan los campos proporcionados
    
    Returns:
        Usuario actualizado
    """
    try:
        usuario_actualizado = usuario_repo.actualizar_usuario(db, usuario_id, data)
        
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return usuario_actualizado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# POST - CAMBIAR CONTRASEÑA
# ============================================

@router.post(
    "/{usuario_id}/cambiar-contraseña",
    summary="Cambiar contraseña",
    description="Cambia la contraseña de un usuario"
)
def cambiar_contraseña(
    usuario_id: str,
    data: UsuarioCambiarContraseña,
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña de un usuario.
    
    - **usuario_id**: ID del usuario
    - **contraseña_actual**: Contraseña actual (para verificar)
    - **contraseña_nueva**: Nueva contraseña
    
    Returns:
        Mensaje de éxito
    """
    try:
        cambiar_contraseña_repo(
            db,
            usuario_id,
            data.contraseña_actual,
            data.contraseña_nueva
        )
        
        return {
            "message": "Contraseña cambiada exitosamente"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# DELETE - ELIMINAR USUARIO
# ============================================

@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema"
)
def eliminar_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario de la base de datos.
    
    - **usuario_id**: ID del usuario a eliminar
    
    ⚠️ ADVERTENCIA: Esta acción es irreversible y eliminará también:
    - Todas las publicaciones del usuario
    - Todos los comentarios del usuario
    - Todas las reacciones del usuario
    - Todos los favoritos del usuario
    """
    eliminado = eliminar_usuario_repo(db, usuario_id)
    
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return None  # 204 No Content