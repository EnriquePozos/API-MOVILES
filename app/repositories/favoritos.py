from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models.usuario import Usuario
from app.models.favorito import Favorito
from app.models.publicacion import Publicacion
from app.schemas.favorito import FavoritoCreate

from app.utils.datetime_utils import now

def add_favoritos(db: Session, id_usuario: str, data: FavoritoCreate) -> dict | None:
    """Añade una publicación a la lista de favoritos del usuario."""
    
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        return None
    
    # Verificar si ya existe
    existe = db.query(Favorito).filter(
        Favorito.id_usuario == id_usuario,
        Favorito.id_publicacion == data.id_publicacion
    ).first()
    
    if existe:
        # Obtener datos de la publicación
        publicacion = db.query(Publicacion).filter(
            Publicacion.id == data.id_publicacion
        ).first()
        
        return {
            "id_usuario": id_usuario,
            "id_publicacion": data.id_publicacion,
            "fecha_guardado": existe.fecha_guardado,
            "publicacion_titulo": publicacion.titulo if publicacion else None
        }
    
    # Obtener datos de la publicación
    publicacion = db.query(Publicacion).filter(
        Publicacion.id == data.id_publicacion
    ).first()
    
    if not publicacion:
        return None  # O podrías lanzar una excepción
    
    #ahora = now()  # Tu utilidad de datetime
    
    nuevo_favorito = Favorito(
        id_publicacion=data.id_publicacion, 
        id_usuario=id_usuario
    )
    
    db.add(nuevo_favorito)
    db.commit()
    db.refresh(nuevo_favorito)
    
    return {
        "id_usuario": id_usuario,
        "id_publicacion": data.id_publicacion,
        "fecha_guardado": nuevo_favorito.fecha_guardado,
        "publicacion_titulo": publicacion.titulo
    }
    

def remove_favoritos(db: Session, id_usuario: str, id_publicacion: str) -> bool:
    """Elimina una publicación de la lista de favoritos del usuario."""
    
    favorito = db.query(Favorito).filter(
        Favorito.id_usuario == id_usuario,
        Favorito.id_publicacion == id_publicacion
    ).first()
    
    if not favorito:
        return False
    
    db.delete(favorito)
    db.commit()
    
    return True