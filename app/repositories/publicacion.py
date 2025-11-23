"""
Repository de publicación.
Contiene las operaciones CRUD para el modelo Publicacion.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models.publicacion import EstatusPublicacion, Publicacion
from app.schemas.publicacion import PublicacionCreate, PublicacionUpdate
from app.utils.datetime_utils import now, utc_now


# Crear publicación
def crear_publicacion( 
    db: Session, 
    data: PublicacionCreate,
    p_id_autor: str
) -> Publicacion:
    """"
    Crea una nueva publicación en la base de datos.
    
    Args:
        db: Sesión de base de datos
        data: Datos de la publicación (PublicacionCreate schema)
        
    Returns:
        Publicacion: Publicación creada
    """
    fecha_publicacion = now() if data.estatus == EstatusPublicacion.PUBLICADA else None
    
    nueva_publicacion = Publicacion(
        titulo=data.titulo,
        descripcion=data.descripcion,
        estatus=data.estatus,
        fecha_publicacion=fecha_publicacion,
        id_autor=p_id_autor
    )
    
    db.add(nueva_publicacion)
    db.commit()
    db.refresh(nueva_publicacion)
    
    return nueva_publicacion

# Actualizar publicación
def actualizar_publicacion( 
    db: Session, 
    data: PublicacionUpdate,
    pub: Publicacion,
) -> Publicacion:
    """" Actualiza una publicación en la base de datos."""
    if pub.estatus == EstatusPublicacion.BORRADOR and data.estatus == EstatusPublicacion.PUBLICADA:
        pub.fecha_publicacion = now()
    
    # ✅ Actualizar solo campos proporcionados (más Pythonic)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pub, field, value)
        
    pub.fecha_modificacion = now()
    
    db.commit()
    db.refresh(pub)
    
    return pub

def eliminar_publicacion(db: Session, pub: Publicacion) -> bool:
    """ Marca una publicación como eliminada. """
    pub.estatus = EstatusPublicacion.ELIMINADA
    pub.fecha_modificacion = now()
    
    db.commit()
    db.refresh(pub)

# Obtener publicación por ID
def get_publicacion_by_id(db: Session, publicacion_id: str) -> Optional[Publicacion]:
    """ Obtiene una publicación por su ID."""
    return db.query(Publicacion).filter(Publicacion.id == publicacion_id).first()