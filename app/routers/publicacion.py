"""
Router de publicaciones
"""

# Imports para archivos y cloudinary
import tempfile
import os

from app.utils.cloudinary import upload_image, upload_media, detectar_tipo_multimedia
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
    eliminar_publicacion,
    get_user_pubs
)

# Guardar en tabla Multimedia
from app.repositories.multimedia import crear_multimedia
from app.schemas.multimedia import MultimediaCreate

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

# Obtener publicaciones activas de un usuario
@router.get(
    "/get_user_active_pubs/{id_usuario}", 
    response_model=List[PublicacionListFeed],
    status_code=status.HTTP_200_OK,
    summary="Obtener las publicaciones de un usuario (activas)",
    description="Obtiene todas las publicaciones (recetas) de un usuario que están activas."
)
def get_users_active_pubs(
    id_usuario: str,
    db: Session = Depends(get_db)
):
    """ Obtiene las publicaciones para el feed (no eliminadas)."""
    
    publicacion = get_user_pubs(db, id_usuario, EstatusPublicacion.PUBLICADA)
        
    if len(publicacion) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay publicaciones disponibles"
        )
        
    return publicacion

# Obtener publicaciones de borrador de un usuario
@router.get(
    "/get_user_drafts/{id_usuario}", 
    response_model=List[PublicacionListFeed],
    status_code=status.HTTP_200_OK,
    summary="Obtener las publicaciones de un usuario (borradores)",
    description="Obtiene todas las publicaciones (recetas) de un usuario que son borradores."
)
def get_users_active_pubs(
    id_usuario: str,
    db: Session = Depends(get_db)
):
    """ Obtiene las publicaciones para el feed (no eliminadas)."""
    
    publicacion = get_user_pubs(db, id_usuario, EstatusPublicacion.BORRADOR)
        
    if len(publicacion) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay publicaciones disponibles"
        )
        
    return publicacion


# Crear nueva publicación
@router.post(
    "/crear_publicacion",
    response_model=PublicacionDetalle,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación con multimedia",
    description="Crea una nueva publicación (receta) con imágenes/videos opcionales."
)
async def crear_nueva_publicacion(
    titulo: str = Form(..., min_length=5, max_length=255),
    descripcion: str = Form(None),
    estatus: EstatusPublicacion = Form(...),
    id_autor: str = Form(...),
    archivos: List[UploadFile] = File(None),  # ← Cambiado de "imagenes" a "archivos"
    db: Session = Depends(get_db)
):
    """Crea una nueva publicación con multimedia (imágenes y/o videos)."""
    try:
        # 1. Validar y crear publicación
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
        
        # 2. Procesar archivos multimedia
        if archivos:
            multimedia_urls = []
            
            for archivo in archivos:
                if archivo and archivo.filename:
                    # Detectar tipo
                    tipo_multimedia = detectar_tipo_multimedia(archivo)
                    
                    # Guardar temporalmente
                    extension = os.path.splitext(archivo.filename)[1]
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=extension
                    ) as tmp_file:
                        content = await archivo.read()
                        tmp_file.write(content)
                        tmp_file_path = tmp_file.name
                    
                    try:
                        # Determinar resource_type para Cloudinary
                        resource_type = "video" if tipo_multimedia == "video" else "image"
                        
                        # Subir a Cloudinary
                        result = upload_media(
                            file_path=tmp_file_path,
                            folder="sazon_toto/publicaciones",
                            public_id=f"pub_{nueva_publicacion.id}_{len(multimedia_urls)}",
                            resource_type=resource_type
                        )
                        
                        if result:
                            # Guardar en BD
                            multimedia_data = MultimediaCreate(
                                url=result["url"],
                                tipo=tipo_multimedia,
                                id_publicacion=nueva_publicacion.id
                            )
                            
                            crear_multimedia(db, multimedia_data)
                            multimedia_urls.append(result["url"])
                            
                    finally:
                        os.unlink(tmp_file_path)
            
        
        db.refresh(nueva_publicacion)
        return nueva_publicacion
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error al crear publicación: {str(e)}")


# Actualizar publicación
@router.put(
    "/update_pub/{id_publicacion}",
    response_model=PublicacionDetalle,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una publicación existente",
    description="Actualiza una publicación (receta)."
)
async def update_publicacion(
    id_publicacion: str,
    titulo: str = Form(..., min_length=5, max_length=255),
    descripcion: str = Form(None),
    estatus: EstatusPublicacion = Form(None),
    archivos: List[UploadFile] = File(None),
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
    
    # 2. Procesar archivos multimedia
    if archivos:
        multimedia_urls = []
        
        # Si hay archivos borro toda la multimedia anterior
        actualizada.multimedia.clear()
        db.commit()
        db.refresh(actualizada)
        
        for archivo in archivos:
            if archivo and archivo.filename:
                # Detectar tipo
                tipo_multimedia = detectar_tipo_multimedia(archivo)
                
                # Guardar temporalmente
                extension = os.path.splitext(archivo.filename)[1]
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=extension
                ) as tmp_file:
                    content = await archivo.read()
                    tmp_file.write(content)
                    tmp_file_path = tmp_file.name
                
                try:
                    # Determinar resource_type para Cloudinary
                    resource_type = "video" if tipo_multimedia == "video" else "image"
                    
                    # Subir a Cloudinary
                    result = upload_media(
                        file_path=tmp_file_path,
                        folder="sazon_toto/publicaciones",
                        public_id=f"pub_{actualizada.id}_{len(multimedia_urls)}",
                        resource_type=resource_type
                    )
                    
                    if result:
                        # Guardar en BD
                        multimedia_data = MultimediaCreate(
                            url=result["url"],
                            tipo=tipo_multimedia,
                            id_publicacion=actualizada.id
                        )
                        
                        crear_multimedia(db, multimedia_data)
                        multimedia_urls.append(result["url"])
                        
                finally:
                    os.unlink(tmp_file_path)
            
        db.refresh(actualizada)
    
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
        
    
