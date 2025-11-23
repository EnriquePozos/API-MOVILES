from sqlalchemy.orm import Session
from typing import List
from app.models.multimedia import Multimedia, TipoMultimedia
from app.schemas.multimedia import MultimediaCreate

def crear_multimedia(db: Session, data: MultimediaCreate) -> Multimedia:
    """
    Crea un registro de multimedia asociado a una publicación.
    
    Args:
        db: Sesión de base de datos
        data: Datos del multimedia (MultimediaCreate schema)
        
    Returns:
        Multimedia: Registro creado
    """
    nuevo_multimedia = Multimedia(
        url=data.url,
        tipo=data.tipo,
        id_publicacion=data.id_publicacion
    )
    
    db.add(nuevo_multimedia)
    db.commit()
    db.refresh(nuevo_multimedia)
    
    return nuevo_multimedia


def eliminar_multimedia(db: Session, multimedia_id: str) -> bool:
    """
    Elimina un registro de multimedia.
    También debería eliminar de Cloudinary.
    """
    multimedia = db.query(Multimedia).filter(Multimedia.id == multimedia_id).first()
    
    if not multimedia:
        return False
    
    # TODO: Eliminar de Cloudinary también
    # from app.utils.cloudinary import delete_cloudinary_file
    # delete_cloudinary_file(multimedia.url)
    
    db.delete(multimedia)
    db.commit()
    
    return True


def get_multimedia_by_publicacion(db: Session, publicacion_id: str) -> List[Multimedia]:
    """
    Obtiene todo el multimedia de una publicación.
    """
    return db.query(Multimedia).filter(
        Multimedia.id_publicacion == publicacion_id
    ).all()