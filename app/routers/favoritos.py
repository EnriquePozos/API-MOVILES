# Imports de FastAPI y SQLAlchemy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db

from app.schemas.favorito import FavoritoCreate, FavoritoResponse

from app.repositories.favoritos import add_favoritos, remove_favoritos


router = APIRouter()


# Añadir a favoritos
@router.post(
    "/add_favorito/{id_usuario}/{id_publicacion}",
    status_code=status.HTTP_201_CREATED,
    response_model=FavoritoResponse,
    summary="Añadir una publicación a favoritos",
    description="Añade una publicación a la lista de favoritos del usuario."
)
def add_favorito(
    id_usuario: str,
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """ Añade una publicación a favoritos del usuario."""

    data = FavoritoCreate(id_publicacion=id_publicacion)
    
    resultado = add_favoritos(db, id_usuario, data)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return resultado



# Eliminar de favoritos
@router.delete(
    "/remove_favorito/{id_usuario}/{id_publicacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una publicación de favoritos",
    description="Elimina una publicación de la lista de favoritos del usuario."
)
def remove_favorito(
    id_usuario: str,
    id_publicacion: str,
    db: Session = Depends(get_db)
):
    """ Elimina una publicación de favoritos del usuario."""
    exito = remove_favoritos(db, id_usuario, id_publicacion)
    
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorito no encontrado"
        )
    
    return None
