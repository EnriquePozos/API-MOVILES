"""
Repository de Comentarios.
Operaciones CRUD para comentarios y respuestas.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.models.comentario import Comentario, EstatusComentario
from app.models.usuario import Usuario
from app.models.publicacion import Publicacion
from app.models.reaccion import Reaccion

from app.schemas.comentario import ComentarioCreate, ComentarioUpdate
from app.utils.datetime_utils import now


# ============================================
# CREAR COMENTARIO
# ============================================

def crear_comentario(
    db: Session, 
    id_usuario: str, 
    data: ComentarioCreate
) -> dict | None:
    """
    Crea un nuevo comentario o respuesta.
    
    Args:
        db: Sesión de base de datos
        id_usuario: ID del usuario que comenta
        data: Datos del comentario
    
    Returns:
        Diccionario con datos del comentario o None si falla
    """
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        return None
    
    # Si es comentario a publicación, verificar que existe
    if data.id_publicacion:
        publicacion = db.query(Publicacion).filter(
            Publicacion.id == data.id_publicacion
        ).first()
        if not publicacion:
            return None
    
    # Si es respuesta, verificar que el comentario padre existe
    if data.id_comentario:
        comentario_padre = db.query(Comentario).filter(
            Comentario.id == data.id_comentario,
            Comentario.estatus == EstatusComentario.ACTIVO
        ).first()
        if not comentario_padre:
            return None
    
    # Crear el comentario
    nuevo_comentario = Comentario(
        comentario=data.comentario,
        id_usuario=id_usuario,
        id_publicacion=data.id_publicacion,
        id_comentario=data.id_comentario,
        estatus=EstatusComentario.ACTIVO
    )
    
    db.add(nuevo_comentario)
    db.commit()
    db.refresh(nuevo_comentario)
    
    return {
        "id": nuevo_comentario.id,
        "comentario": nuevo_comentario.comentario,
        "estatus": nuevo_comentario.estatus,
        "fecha_creacion": nuevo_comentario.fecha_creacion,
        "id_usuario": id_usuario,
        "id_publicacion": nuevo_comentario.id_publicacion,
        "id_comentario": nuevo_comentario.id_comentario,
        "usuario_alias": usuario.alias,
        "usuario_foto": usuario.foto_perfil,
        "es_respuesta": nuevo_comentario.id_comentario is not None,
        "total_respuestas": 0,
        "total_reacciones": 0
    }


# ============================================
# OBTENER COMENTARIOS
# ============================================

def get_comentario_by_id(db: Session, id_comentario: str) -> Optional[Comentario]:
    """Obtiene un comentario por su ID."""
    return db.query(Comentario).filter(
        Comentario.id == id_comentario
    ).first()


def get_comentarios_publicacion(
    db: Session, 
    id_publicacion: str,
    skip: int = 0,
    limit: int = 20
) -> List[dict]:
    """
    Obtiene los comentarios raíz de una publicación.
    No incluye respuestas (solo comentarios de primer nivel).
    """
    comentarios = db.query(Comentario).filter(
        Comentario.id_publicacion == id_publicacion,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).order_by(
        Comentario.fecha_creacion.desc()
    ).offset(skip).limit(limit).all()
    
    resultado = []
    for c in comentarios:
        # Obtener datos del usuario
        usuario = db.query(Usuario).filter(Usuario.id == c.id_usuario).first()
        
        # Contar respuestas
        total_respuestas = db.query(Comentario).filter(
            Comentario.id_comentario == c.id,
            Comentario.estatus == EstatusComentario.ACTIVO
        ).count()
        
        # Contar reacciones
        total_reacciones = db.query(Reaccion).filter(
            Reaccion.id_comentario == c.id
        ).count()
        
        resultado.append({
            "id": c.id,
            "comentario": c.comentario,
            "estatus": c.estatus,
            "fecha_creacion": c.fecha_creacion,
            "id_usuario": c.id_usuario,
            "id_publicacion": c.id_publicacion,
            "id_comentario": c.id_comentario,
            "usuario_alias": usuario.alias if usuario else None,
            "usuario_foto": usuario.foto_perfil if usuario else None,
            "es_respuesta": False,
            "total_respuestas": total_respuestas,
            "reacciones": c.reacciones,
            "total_reacciones": total_reacciones
        })
    
    return resultado


def get_respuestas_comentario(
    db: Session, 
    id_comentario: str,
    skip: int = 0,
    limit: int = 20
) -> List[dict]:
    """Obtiene las respuestas a un comentario."""
    respuestas = db.query(Comentario).filter(
        Comentario.id_comentario == id_comentario,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).order_by(
        Comentario.fecha_creacion.asc()
    ).offset(skip).limit(limit).all()
    
    resultado = []
    for r in respuestas:
        usuario = db.query(Usuario).filter(Usuario.id == r.id_usuario).first()
        
        total_reacciones = db.query(Reaccion).filter(
            Reaccion.id_comentario == r.id
        ).count()
        
        # Contar respuestas anidadas
        total_respuestas = db.query(Comentario).filter(
            Comentario.id_comentario == r.id,
            Comentario.estatus == EstatusComentario.ACTIVO
        ).count()
        
        resultado.append({
            "id": r.id,
            "comentario": r.comentario,
            "estatus": r.estatus,
            "fecha_creacion": r.fecha_creacion,
            "id_usuario": r.id_usuario,
            "id_publicacion": r.id_publicacion,
            "id_comentario": r.id_comentario,
            "usuario_alias": usuario.alias if usuario else None,
            "usuario_foto": usuario.foto_perfil if usuario else None,
            "es_respuesta": True,
            "total_respuestas": total_respuestas,
            "total_reacciones": total_reacciones
        })
    
    return resultado


def get_comentarios_usuario(
    db: Session, 
    id_usuario: str,
    skip: int = 0,
    limit: int = 20
) -> List[Comentario]:
    """Obtiene todos los comentarios de un usuario."""
    return db.query(Comentario).filter(
        Comentario.id_usuario == id_usuario,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).order_by(
        Comentario.fecha_creacion.desc()
    ).offset(skip).limit(limit).all()


# ============================================
# ACTUALIZAR COMENTARIO
# ============================================

def actualizar_comentario(
    db: Session, 
    id_comentario: str,
    id_usuario: str,
    data: ComentarioUpdate
) -> dict | None:
    """
    Actualiza el texto de un comentario.
    Solo el autor puede editar su comentario.
    """
    comentario = db.query(Comentario).filter(
        Comentario.id == id_comentario,
        Comentario.id_usuario == id_usuario,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).first()
    
    if not comentario:
        return None
    
    comentario.comentario = data.comentario
    
    db.commit()
    db.refresh(comentario)
    
    # Obtener datos del usuario
    usuario = db.query(Usuario).filter(Usuario.id == comentario.id_usuario).first()
    
    # Contar respuestas y reacciones
    total_respuestas = db.query(Comentario).filter(
        Comentario.id_comentario == comentario.id,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).count()
    
    total_reacciones = db.query(Reaccion).filter(
        Reaccion.id_comentario == comentario.id
    ).count()
    
    return {
        "id": comentario.id,
        "comentario": comentario.comentario,
        "estatus": comentario.estatus,
        "fecha_creacion": comentario.fecha_creacion,
        "id_usuario": comentario.id_usuario,
        "id_publicacion": comentario.id_publicacion,
        "id_comentario": comentario.id_comentario,
        "usuario_alias": usuario.alias if usuario else None,
        "usuario_foto": usuario.foto_perfil if usuario else None,
        "es_respuesta": comentario.id_comentario is not None,
        "total_respuestas": total_respuestas,
        "total_reacciones": total_reacciones
    }


# ============================================
# ELIMINAR COMENTARIO
# ============================================

def eliminar_comentario(
    db: Session, 
    id_comentario: str,
    id_usuario: str
) -> bool:
    """
    Elimina lógicamente un comentario (soft delete).
    Solo el autor puede eliminar su comentario.
    """
    comentario = db.query(Comentario).filter(
        Comentario.id == id_comentario,
        Comentario.id_usuario == id_usuario,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).first()
    
    if not comentario:
        return False
    
    # Soft delete
    comentario.estatus = EstatusComentario.ELIMINADO
    #comentario.comentario = "[Comentario eliminado]"
    
    db.commit()
    return True


def eliminar_comentario_admin(db: Session, id_comentario: str) -> bool:
    """Elimina un comentario (solo para administradores)."""
    comentario = db.query(Comentario).filter(
        Comentario.id == id_comentario
    ).first()
    
    if not comentario:
        return False
    
    comentario.estatus = EstatusComentario.ELIMINADO
    comentario.comentario = "[Comentario eliminado por moderador]"
    
    db.commit()
    return True


# ============================================
# CONTEOS Y ESTADÍSTICAS
# ============================================

def contar_comentarios_publicacion(db: Session, id_publicacion: str) -> int:
    """Cuenta el total de comentarios activos de una publicación."""
    return db.query(Comentario).filter(
        Comentario.id_publicacion == id_publicacion,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).count()


def contar_respuestas_comentario(db: Session, id_comentario: str) -> int:
    """Cuenta el total de respuestas a un comentario."""
    return db.query(Comentario).filter(
        Comentario.id_comentario == id_comentario,
        Comentario.estatus == EstatusComentario.ACTIVO
    ).count()