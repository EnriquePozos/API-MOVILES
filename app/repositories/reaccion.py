"""
Repository de Reacciones.
Operaciones CRUD para reacciones a publicaciones y comentarios.
"""

from sqlalchemy.orm import Session
from typing import Optional

from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.reaccion import Reaccion, TipoReaccion
from app.models.comentario import Comentario


# ============================================
# REACCIONES A PUBLICACIONES
# ============================================

def add_reaccion_pub(
    db: Session, 
    id_usuario: str, 
    id_publicacion: str, 
    reaccion: TipoReaccion
) -> dict | None:
    """Añade una reacción a una publicación por parte del usuario."""
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        return None
    
    # Verificar que la publicación existe
    publicacion = db.query(Publicacion).filter(
        Publicacion.id == id_publicacion
    ).first()
    
    if not publicacion:
        return None
    
    # Verificar si ya existe una reacción
    existe = db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_publicacion == id_publicacion
    ).first()
    
    if existe:
        # Si ya existe, actualizar el tipo de reacción
        existe.reaccion = reaccion
        db.commit()
        db.refresh(existe)
        
        return {
            "id_usuario": id_usuario,
            "id_publicacion": id_publicacion,
            "id_comentario": None,
            "tipo_reaccion": existe.reaccion,
            "publicacion_titulo": publicacion.titulo
        }
    
    # Crear nueva reacción
    nueva_reaccion = Reaccion(
        id_publicacion=id_publicacion, 
        id_usuario=id_usuario,
        reaccion=reaccion
    )
    
    db.add(nueva_reaccion)
    db.commit()
    db.refresh(nueva_reaccion)
    
    return {
        "id_usuario": id_usuario,
        "id_publicacion": id_publicacion,
        "id_comentario": None,
        "tipo_reaccion": nueva_reaccion.reaccion,
        "publicacion_titulo": publicacion.titulo
    }


def remove_reaccion_pub(db: Session, id_usuario: str, id_publicacion: str) -> bool:
    """Elimina una reacción de una publicación."""
    
    reaccion = db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_publicacion == id_publicacion
    ).first()
    
    if not reaccion:
        return False
    
    db.delete(reaccion)
    db.commit()
    return True


def get_reacciones_publicacion(
    db: Session, 
    id_publicacion: str
) -> dict:
    """Obtiene el conteo de reacciones de una publicación."""
    
    likes = db.query(Reaccion).filter(
        Reaccion.id_publicacion == id_publicacion,
        Reaccion.reaccion == TipoReaccion.LIKE
    ).count()
    
    dislikes = db.query(Reaccion).filter(
        Reaccion.id_publicacion == id_publicacion,
        Reaccion.reaccion == TipoReaccion.DISLIKE
    ).count()
    
    return {
        "id_publicacion": id_publicacion,
        "likes": likes,
        "dislikes": dislikes,
        "total": likes + dislikes
    }


def get_reaccion_usuario_publicacion(
    db: Session, 
    id_usuario: str, 
    id_publicacion: str
) -> Optional[Reaccion]:
    """Obtiene la reacción de un usuario a una publicación específica."""
    
    return db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_publicacion == id_publicacion
    ).first()


# ============================================
# REACCIONES A COMENTARIOS
# ============================================


def add_reaccion_comment(
    db: Session, 
    id_usuario: str, 
    id_comentario: str, 
    reaccion: TipoReaccion
) -> dict | None:
    """Añade una reacción a un comentario por parte del usuario."""
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        return None
    
    # Verificar que el comentario existe
    comentario = db.query(Comentario).filter(
        Comentario.id == id_comentario
    ).first()
    
    if not comentario:
        return None
    
    # Obtener título de la publicación asociada
    publicacion_titulo = None
    if comentario.id_publicacion:
        publicacion = db.query(Publicacion).filter(
            Publicacion.id == comentario.id_publicacion
        ).first()
        publicacion_titulo = publicacion.titulo if publicacion else None
    
    # Verificar si ya existe una reacción
    existe = db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_comentario == id_comentario
    ).first()
    
    if existe:
        # Si ya existe, actualizar el tipo de reacción
        existe.reaccion = reaccion
        db.commit()
        db.refresh(existe)
        
        return {
            "id_usuario": id_usuario,
            "id_publicacion": comentario.id_publicacion,
            "id_comentario": id_comentario,
            "tipo_reaccion": existe.reaccion,
            "publicacion_titulo": publicacion_titulo
        }
    
    # Crear nueva reacción
    nueva_reaccion = Reaccion(
        id_comentario=id_comentario, 
        id_usuario=id_usuario,
        reaccion=reaccion
    )
    
    db.add(nueva_reaccion)
    db.commit()
    db.refresh(nueva_reaccion)
    
    return {
        "id_usuario": id_usuario,
        "id_publicacion": comentario.id_publicacion,
        "id_comentario": id_comentario,
        "tipo_reaccion": nueva_reaccion.reaccion,
        "publicacion_titulo": publicacion_titulo
    }


def remove_reaccion_comment(db: Session, id_usuario: str, id_comentario: str) -> bool:
    """Elimina una reacción de un comentario."""
    
    reaccion = db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_comentario == id_comentario
    ).first()
    
    if not reaccion:
        return False
    
    db.delete(reaccion)
    db.commit()
    return True


def get_reacciones_comentario(db: Session, id_comentario: str) -> dict:
    """Obtiene el conteo de reacciones de un comentario."""
    
    likes = db.query(Reaccion).filter(
        Reaccion.id_comentario == id_comentario,
        Reaccion.reaccion == TipoReaccion.LIKE
    ).count()
    
    dislikes = db.query(Reaccion).filter(
        Reaccion.id_comentario == id_comentario,
        Reaccion.reaccion == TipoReaccion.DISLIKE
    ).count()
    
    return {
        "id_comentario": id_comentario,
        "likes": likes,
        "dislikes": dislikes,
        "total": likes + dislikes
    }
    
    
def get_reaccion_usuario_comentario(
    db: Session, 
    id_usuario: str, 
    id_comentario: str
) -> Optional[Reaccion]:
    """Obtiene la reacción de un usuario a una comentario específica."""
    
    return db.query(Reaccion).filter(
        Reaccion.id_usuario == id_usuario,
        Reaccion.id_comentario == id_comentario
    ).first()