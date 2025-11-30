"""
Repository de publicación.
Contiene las operaciones CRUD para el modelo Publicacion.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List

from app.models.publicacion import EstatusPublicacion, Publicacion
from app.models.comentario import Comentario
from app.models.favorito import Favorito
from app.schemas.publicacion import PublicacionCreate, PublicacionUpdate
from app.utils.datetime_utils import now, utc_now

# Helper para serializar el JSON de respuesta de publicaciones
def serialize(publicaciones):
    for pub in publicaciones:
        pub.autor_alias = pub.autor.alias if pub.autor else None
        pub.autor_foto = pub.autor.foto_perfil if pub.autor else None
        pub.total_comentarios = len(pub.comentarios)
        pub.fecha_creacion = pub.fecha_creacion if pub.fecha_creacion else None
        pub.fecha_publicacion = pub.fecha_publicacion if pub.fecha_publicacion else None
        pub.total_reacciones = len(pub.reacciones)
        pub.imagen_preview = pub.multimedia[0].url if pub.multimedia else None
        pub.multimedia_list = pub.multimedia
    
    return publicaciones


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

# Obtener publicaciones para feed
def get_feed_pubs(db: Session) -> List[Publicacion]:
    """
    Obtiene publicaciones del feed (no eliminadas) con autor y multimedia.
    Optimizado con eager loading.
    """
    publicaciones = db.query(Publicacion).options(
        joinedload(Publicacion.autor),
        joinedload(Publicacion.multimedia),
        joinedload(Publicacion.comentarios).joinedload(Comentario.usuario)
    ).filter(
        Publicacion.estatus == EstatusPublicacion.PUBLICADA
    ).order_by(
        Publicacion.fecha_publicacion.desc()
    ).all()
    
    publicaciones = serialize(publicaciones)
    
    return publicaciones

# Obtener publicaciones de un usuario ()
def get_user_pubs(db: Session, id_autor: str, estatus: EstatusPublicacion) -> List[Publicacion]:
    """
    Obtiene publicaciones con un estatus indicado de un usuario con autor y multimedia.
    """
    publicaciones = db.query(Publicacion).options(
        joinedload(Publicacion.autor),
        joinedload(Publicacion.multimedia),
        joinedload(Publicacion.comentarios).joinedload(Comentario.usuario)
    ).filter(
        Publicacion.estatus == estatus,
        Publicacion.id_autor == id_autor
    ).order_by(
        Publicacion.fecha_publicacion.desc()
    ).all()
        
    publicaciones = serialize(publicaciones)
    
    return publicaciones


def get_fav_pubs(db: Session, id_usuario: str) -> List[Publicacion]:
    """ Obtiene publicaciones marcadas como favoritas por el usuario."""
    favoritos = db.query(Favorito).filter(
        Favorito.id_usuario == id_usuario
    ).all()
    
    # Obtener las publicaciones favoritas
    favoritas_ids = {fav.id_publicacion for fav in favoritos}
    fav_pubs = db.query(Publicacion).filter(Publicacion.id.in_(favoritas_ids)).all()
    
    fav_pubs = serialize(fav_pubs)
    
    return fav_pubs


