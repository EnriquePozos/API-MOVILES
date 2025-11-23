"""
Router de publicaciones
"""

# Imports para archivos y cloudinary
import tempfile
import os

from app.utils.cloudinary import upload_image
# Imports de FastAPI y SQLAlchemy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import Form, File, UploadFile

from app.models.publicacion import EstatusPublicacion

from app.database.session import get_db
from app.schemas.publicacion import (
    PublicacionCreate,
    PublicacionUpdate,
    PublicacionSimple,
    PublicacionDetalle,
    PublicacionListFeed
)
from app.repositories.publicacion import (
    crear_publicacion,
    get_publicacion_by_id,
    get_feed_pubs,
    actualizar_publicacion,
    # publicar_publicacion,
    eliminar_publicacion
)

import app.repositories.publicacion as pub_repo
import app.repositories.usuario as user_repo

#from app.utils.auth import create_access_token
from datetime import timedelta

# Crear router
router = APIRouter()


# Obtener publicaciones para el feed
@router.get(
    "/get_feed", 
    response_model=List[PublicacionListFeed],
    status_code=status.HTTP_200_OK,
    summary="Obtener las publicaciones del feed",
    description="Obtiene todas las publicaciones (recetas) para el feed."
)
def get_feed_publicaciones(
    db: Session = Depends(get_db)
):
    """ Obtiene las publicaciones para el feed (no eliminadas)."""
    
    publicacion = get_feed_pubs(db)
        
    if len(publicacion) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay publicaciones disponibles"
        )
        
    return publicacion

# Obtener publicación por ID
@router.get(
    "/{id_publicacion}",
    response_model=PublicacionDetalle,
    status_code=status.HTTP_200_OK,
    summary="Obtener una publicación por ID",
    description="Obtiene una publicación (receta) mediante su ID."
)
def get_publicacion(
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """ Obtiene una publicación por su ID."""
    
    publicacion = get_publicacion_by_id(db, id_publicacion)
        
    if not publicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada"
        )
        
    return publicacion


# Crear nueva publicación
@router.post(
    "/crear_publicacion",
    response_model=PublicacionSimple,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación",
    description="Crea una nueva publicación (receta)."
)
def crear_nueva_publicacion(
    titulo: str = Form(..., min_length=5, max_length=255),
    descripcion: str = Form(None),
    estatus: EstatusPublicacion = Form(None),
    id_autor: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva publicación en estado borrador.
    
    Args:
        publicacion: Datos de la publicación (PublicacionCreate schema)
        db: Sesión de base de datos
        usuario_actual: Usuario autenticado
        
    Returns:
        PublicacionSimple: Publicación creada
    """
    
    data = PublicacionCreate(
        titulo=titulo,
        descripcion=descripcion,
        estatus=estatus
    )
    
    nueva_publicacion = crear_publicacion(
        db=db,
        data=data,
        p_id_autor=id_autor
    )
    return nueva_publicacion


# Actualizar publicación
@router.put(
    "/update_pub/{id_publicacion}",
    response_model=PublicacionSimple,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una publicación existente",
    description="Actualiza una publicación (receta)."
)
def update_publicacion(
    id_publicacion: str,
    titulo: str = Form(..., min_length=5, max_length=255),
    descripcion: str = Form(None),
    estatus: EstatusPublicacion = Form(None),
    db: Session = Depends(get_db)
):
    """ Actualiza una publicación existente."""
    
    publicacion = get_publicacion_by_id(db, id_publicacion)
        
    if not publicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada"
        )
        
    data = PublicacionUpdate(
        titulo=titulo,
        descripcion=descripcion,
        estatus=estatus
    )

    actualizada = actualizar_publicacion(
        db=db,
        data=data,
        pub=publicacion,
    )
    
    return actualizada
    
    
# Eliminar publicación (lógica de borrado)
@router.delete(
    "/delete_pub/{id_publicacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una publicación",
    description="Elimina una publicación (receta) mediante borrado lógico."
)
def delete_publicacion(
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """ Elimina una publicación mediante borrado lógico."""
    
    publicacion = get_publicacion_by_id(db, id_publicacion)
        
    if not publicacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada"
        )
        
    eliminar_publicacion(db, publicacion)
        
    
