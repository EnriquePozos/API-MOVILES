"""
Router de Reacciones.
Endpoints para gestionar reacciones a publicaciones y comentarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.schemas.reaccion import ReaccionResponse
from app.models.reaccion import TipoReaccion

from app.repositories.reaccion import (
    add_reaccion_pub, 
    add_reaccion_comment, 
    remove_reaccion_pub, 
    remove_reaccion_comment,
    get_reacciones_publicacion,
    get_reacciones_comentario,
    get_reaccion_usuario_publicacion
)


router = APIRouter()


# ============================================
# REACCIONES A PUBLICACIONES
# ============================================

@router.post(
    "/publicacion/{id_publicacion}",
    status_code=status.HTTP_201_CREATED,
    response_model=ReaccionResponse,
    summary="Añadir reacción a publicación",
    description="Añade un like o dislike a una publicación. Si ya existe, actualiza el tipo."
)
def add_reaccion_publicacion(
    id_publicacion: str,
    id_usuario: str = Query(..., description="ID del usuario"),
    tipo_reaccion: TipoReaccion = Query(..., description="Tipo de reacción (like/dislike)"),
    db: Session = Depends(get_db)
):
    """Añade una reacción a una publicación."""
    
    resultado = add_reaccion_pub(db, id_usuario, id_publicacion, tipo_reaccion)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario o publicación no encontrada"
        )
    
    return resultado


@router.delete(
    "/publicacion/{id_publicacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reacción de publicación",
    description="Elimina la reacción del usuario de una publicación."
)
def delete_reaccion_publicacion(
    id_publicacion: str,
    id_usuario: str = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """Elimina una reacción de una publicación."""
    
    exito = remove_reaccion_pub(db, id_usuario, id_publicacion)
    
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reacción no encontrada"
        )
    
    return None


@router.get(
    "/publicacion/{id_publicacion}/conteo",
    status_code=status.HTTP_200_OK,
    summary="Obtener conteo de reacciones",
    description="Obtiene el número de likes y dislikes de una publicación."
)
def get_conteo_reacciones_publicacion(
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """Obtiene el conteo de reacciones de una publicación."""
    
    return get_reacciones_publicacion(db, id_publicacion)


@router.get(
    "/publicacion/{id_publicacion}/usuario/{id_usuario}",
    status_code=status.HTTP_200_OK,
    summary="Verificar reacción de usuario",
    description="Verifica si un usuario ha reaccionado a una publicación y qué tipo de reacción."
)
def verificar_reaccion_usuario(
    id_publicacion: str,
    id_usuario: str,
    db: Session = Depends(get_db)
):
    """Verifica la reacción de un usuario a una publicación."""
    
    reaccion = get_reaccion_usuario_publicacion(db, id_usuario, id_publicacion)
    
    if not reaccion:
        return {
            "tiene_reaccion": False,
            "tipo_reaccion": None
        }
    
    return {
        "tiene_reaccion": True,
        "tipo_reaccion": reaccion.reaccion
    }


# ============================================
# REACCIONES A COMENTARIOS
# ============================================

@router.post(
    "/comentario/{id_comentario}",
    status_code=status.HTTP_201_CREATED,
    response_model=ReaccionResponse,
    summary="Añadir reacción a comentario",
    description="Añade un like o dislike a un comentario. Si ya existe, actualiza el tipo."
)
def add_reaccion_a_comentario(
    id_comentario: str,
    id_usuario: str = Query(..., description="ID del usuario"),
    tipo_reaccion: TipoReaccion = Query(..., description="Tipo de reacción (like/dislike)"),
    db: Session = Depends(get_db)
):
    """Añade una reacción a un comentario."""
    
    resultado = add_reaccion_comment(db, id_usuario, id_comentario, tipo_reaccion)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario o comentario no encontrado"
        )
    
    return resultado


@router.delete(
    "/comentario/{id_comentario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reacción de comentario",
    description="Elimina la reacción del usuario de un comentario."
)
def delete_reaccion_comentario(
    id_comentario: str,
    id_usuario: str = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """Elimina una reacción de un comentario."""
    
    exito = remove_reaccion_comment(db, id_usuario, id_comentario)
    
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reacción no encontrada"
        )
    
    return None


@router.get(
    "/comentario/{id_comentario}/conteo",
    status_code=status.HTTP_200_OK,
    summary="Obtener conteo de reacciones de comentario",
    description="Obtiene el número de likes y dislikes de un comentario."
)
def get_conteo_reacciones_comentario(
    id_comentario: str,
    db: Session = Depends(get_db)
):
    """Obtiene el conteo de reacciones de un comentario."""
    
    return get_reacciones_comentario(db, id_comentario)