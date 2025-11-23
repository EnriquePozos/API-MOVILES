"""
Router de Comentarios.
Endpoints para gestionar comentarios y respuestas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.schemas.comentario import (
    ComentarioCreate,
    ComentarioUpdate,
    ComentarioResponse,
    ComentarioSimple
)

from app.repositories.comentario import (
    crear_comentario,
    get_comentario_by_id,
    get_comentarios_publicacion,
    get_respuestas_comentario,
    get_comentarios_usuario,
    actualizar_comentario,
    eliminar_comentario,
    contar_comentarios_publicacion,
    contar_respuestas_comentario
)


router = APIRouter()


# ============================================
# CREAR COMENTARIOS
# ============================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ComentarioResponse,
    summary="Crear comentario o respuesta",
    description="Crea un comentario en una publicación o una respuesta a otro comentario."
)
def create_comentario(
    data: ComentarioCreate,
    id_usuario: str = Query(..., description="ID del usuario que comenta"),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo comentario.
    
    - Si se proporciona `id_publicacion`: es un comentario raíz
    - Si se proporciona `id_comentario`: es una respuesta a otro comentario
    """
    resultado = crear_comentario(db, id_usuario, data)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario, publicación o comentario padre no encontrado"
        )
    
    return resultado


@router.post(
    "/publicacion/{id_publicacion}",
    status_code=status.HTTP_201_CREATED,
    response_model=ComentarioResponse,
    summary="Comentar en publicación",
    description="Crea un comentario directamente en una publicación."
)
def comentar_publicacion(
    id_publicacion: str,
    comentario: str = Query(..., min_length=1, max_length=1000, description="Texto del comentario"),
    id_usuario: str = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """Endpoint simplificado para comentar en una publicación."""
    
    data = ComentarioCreate(
        comentario=comentario,
        id_publicacion=id_publicacion
    )
    
    resultado = crear_comentario(db, id_usuario, data)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario o publicación no encontrada"
        )
    
    return resultado


@router.post(
    "/respuesta/{id_comentario_padre}",
    status_code=status.HTTP_201_CREATED,
    response_model=ComentarioResponse,
    summary="Responder a comentario",
    description="Crea una respuesta a un comentario existente."
)
def responder_comentario(
    id_comentario_padre: str,
    comentario: str = Query(..., min_length=1, max_length=1000, description="Texto de la respuesta"),
    id_usuario: str = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    """Endpoint simplificado para responder a un comentario."""
    
    data = ComentarioCreate(
        comentario=comentario,
        id_comentario=id_comentario_padre
    )
    
    resultado = crear_comentario(db, id_usuario, data)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario o comentario padre no encontrado"
        )
    
    return resultado


# ============================================
# OBTENER COMENTARIOS
# ============================================

@router.get(
    "/{id_comentario}",
    status_code=status.HTTP_200_OK,
    response_model=ComentarioResponse,
    summary="Obtener comentario por ID",
    description="Obtiene un comentario específico por su ID."
)
def get_comentario(
    id_comentario: str,
    db: Session = Depends(get_db)
):
    """Obtiene un comentario por su ID."""
    
    comentario = get_comentario_by_id(db, id_comentario)
    
    if not comentario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )
    
    return comentario


@router.get(
    "/publicacion/{id_publicacion}",
    status_code=status.HTTP_200_OK,
    response_model=List[ComentarioResponse],
    summary="Obtener comentarios de publicación",
    description="Obtiene los comentarios raíz de una publicación (sin respuestas anidadas)."
)
def get_comentarios_de_publicacion(
    id_publicacion: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """Obtiene los comentarios de una publicación."""
    
    return get_comentarios_publicacion(db, id_publicacion, skip, limit)


@router.get(
    "/{id_comentario}/respuestas",
    status_code=status.HTTP_200_OK,
    response_model=List[ComentarioResponse],
    summary="Obtener respuestas de comentario",
    description="Obtiene las respuestas a un comentario específico."
)
def get_respuestas_de_comentario(
    id_comentario: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """Obtiene las respuestas a un comentario."""
    
    return get_respuestas_comentario(db, id_comentario, skip, limit)


@router.get(
    "/usuario/{id_usuario}",
    status_code=status.HTTP_200_OK,
    response_model=List[ComentarioResponse],
    summary="Obtener comentarios de usuario",
    description="Obtiene todos los comentarios realizados por un usuario."
)
def get_comentarios_de_usuario(
    id_usuario: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """Obtiene los comentarios de un usuario."""
    
    return get_comentarios_usuario(db, id_usuario, skip, limit)


# ============================================
# ACTUALIZAR COMENTARIO
# ============================================

@router.put(
    "/{id_comentario}",
    status_code=status.HTTP_200_OK,
    response_model=ComentarioResponse,
    summary="Actualizar comentario",
    description="Actualiza el texto de un comentario. Solo el autor puede editarlo."
)
def update_comentario(
    id_comentario: str,
    data: ComentarioUpdate,
    id_usuario: str = Query(..., description="ID del usuario (debe ser el autor)"),
    db: Session = Depends(get_db)
):
    """Actualiza un comentario existente."""
    
    resultado = actualizar_comentario(db, id_comentario, id_usuario, data)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado o no tienes permiso para editarlo"
        )
    
    return resultado


# ============================================
# ELIMINAR COMENTARIO
# ============================================

@router.delete(
    "/{id_comentario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar comentario",
    description="Elimina un comentario (soft delete). Solo el autor puede eliminarlo."
)
def delete_comentario(
    id_comentario: str,
    id_usuario: str = Query(..., description="ID del usuario (debe ser el autor)"),
    db: Session = Depends(get_db)
):
    """Elimina un comentario (soft delete)."""
    
    exito = eliminar_comentario(db, id_comentario, id_usuario)
    
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado o no tienes permiso para eliminarlo"
        )
    
    return None


# ============================================
# CONTEOS
# ============================================

@router.get(
    "/publicacion/{id_publicacion}/conteo",
    status_code=status.HTTP_200_OK,
    summary="Contar comentarios de publicación",
    description="Obtiene el número total de comentarios de una publicación."
)
def conteo_comentarios_publicacion(
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """Cuenta los comentarios de una publicación."""
    
    total = contar_comentarios_publicacion(db, id_publicacion)
    
    return {
        "id_publicacion": id_publicacion,
        "total_comentarios": total
    }


@router.get(
    "/{id_comentario}/conteo-respuestas",
    status_code=status.HTTP_200_OK,
    summary="Contar respuestas de comentario",
    description="Obtiene el número de respuestas a un comentario."
)
def conteo_respuestas_comentario(
    id_comentario: str,
    db: Session = Depends(get_db)
):
    """Cuenta las respuestas a un comentario."""
    
    total = contar_respuestas_comentario(db, id_comentario)
    
    return {
        "id_comentario": id_comentario,
        "total_respuestas": total
    }