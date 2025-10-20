"""
Repository para Usuario.
Contiene toda la lógica de base de datos para la entidad Usuario.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.utils.auth import hash_password, verify_password


# ============================================
# CREAR USUARIO (Registro)
# ============================================

def crear_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario en la base de datos.
    
    Args:
        db: Sesión de base de datos
        data: Datos del usuario (UsuarioCreate schema)
        
    Returns:
        Usuario: Usuario creado
        
    Raises:
        ValueError: Si el email o alias ya existen
    """
    # Verificar si el email ya existe
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise ValueError("El email ya está registrado")
    
    # Verificar si el alias ya existe
    if db.query(Usuario).filter(Usuario.alias == data.alias).first():
        raise ValueError("El alias ya está en uso")
    
    # Hashear contraseña
    hashed_password = hash_password(data.contraseña)
    
    # Crear modelo Usuario
    nuevo_usuario = Usuario(
        email=data.email,
        alias=data.alias,
        contraseña=hashed_password,
        nombre=data.nombre,
        apellido_paterno=data.apellido_paterno,
        apellido_materno=data.apellido_materno,
        telefono=data.telefono,
        direccion=data.direccion,
        foto_perfil=data.foto_perfil
    )
    
    # Guardar en BD
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


# ============================================
# LOGIN (Autenticación)
# ============================================

def login_usuario(db: Session, email: str, contraseña: str) -> Optional[Usuario]:
    """
    Autentica un usuario con email y contraseña.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        contraseña: Contraseña en texto plano
        
    Returns:
        Usuario: Usuario autenticado
        None: Si las credenciales son incorrectas
    """
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return None
    
    # Verificar contraseña
    if not verify_password(contraseña, usuario.contraseña):
        return None
    
    return usuario


# ============================================
# OBTENER USUARIO
# ============================================

def get_usuario_by_id(db: Session, usuario_id: str) -> Optional[Usuario]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Usuario: Usuario encontrado
        None: Si no existe
    """
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    """
    Obtiene un usuario por su email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        
    Returns:
        Usuario: Usuario encontrado
        None: Si no existe
    """
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_usuario_by_alias(db: Session, alias: str) -> Optional[Usuario]:
    """
    Obtiene un usuario por su alias.
    
    Args:
        db: Sesión de base de datos
        alias: Alias del usuario
        
    Returns:
        Usuario: Usuario encontrado
        None: Si no existe
    """
    return db.query(Usuario).filter(Usuario.alias == alias).first()


# ============================================
# ACTUALIZAR USUARIO
# ============================================

def actualizar_usuario(db: Session, usuario_id: str, data: UsuarioUpdate) -> Optional[Usuario]:
    """
    Actualiza los datos de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario a actualizar
        data: Datos a actualizar (UsuarioUpdate schema)
        
    Returns:
        Usuario: Usuario actualizado
        None: Si no existe
        
    Raises:
        ValueError: Si el email o alias ya están en uso por otro usuario
    """
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        return None
    
    # Actualizar solo los campos que no son None
    update_data = data.dict(exclude_unset=True)
    
    # Verificar si el email cambió y ya existe
    if 'email' in update_data and update_data['email'] != usuario.email:
        if db.query(Usuario).filter(Usuario.email == update_data['email']).first():
            raise ValueError("El email ya está en uso")
    
    # Verificar si el alias cambió y ya existe
    if 'alias' in update_data and update_data['alias'] != usuario.alias:
        if db.query(Usuario).filter(Usuario.alias == update_data['alias']).first():
            raise ValueError("El alias ya está en uso")
    
    # Actualizar campos
    for campo, valor in update_data.items():
        setattr(usuario, campo, valor)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


# ============================================
# CAMBIAR CONTRASEÑA
# ============================================

def cambiar_contraseña(
    db: Session,
    usuario_id: str,
    contraseña_actual: str,
    contraseña_nueva: str
) -> bool:
    """
    Cambia la contraseña de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        contraseña_actual: Contraseña actual (para verificar)
        contraseña_nueva: Nueva contraseña
        
    Returns:
        bool: True si se cambió exitosamente
        
    Raises:
        ValueError: Si la contraseña actual es incorrecta
    """
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        raise ValueError("Usuario no encontrado")
    
    # Verificar contraseña actual
    if not verify_password(contraseña_actual, usuario.contraseña):
        raise ValueError("Contraseña actual incorrecta")
    
    # Hashear y actualizar nueva contraseña
    usuario.contraseña = hash_password(contraseña_nueva)
    
    db.commit()
    return True


# ============================================
# ELIMINAR USUARIO
# ============================================

def eliminar_usuario(db: Session, usuario_id: str) -> bool:
    """
    Elimina un usuario de la base de datos.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario a eliminar
        
    Returns:
        bool: True si se eliminó exitosamente
    """
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        return False
    
    db.delete(usuario)
    db.commit()
    
    return True


# ============================================
# OBTENER PERFIL CON ESTADÍSTICAS
# ============================================

def get_perfil_usuario(db: Session, usuario_id: str) -> Optional[dict]:
    """
    Obtiene el perfil completo de un usuario con estadísticas.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        dict: Perfil del usuario con estadísticas
        None: Si no existe
    """
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        return None
    
    # Contar publicaciones
    total_publicaciones = len(usuario.publicaciones)
    
    # Contar comentarios
    total_comentarios = len(usuario.comentarios)
    
    # Contar favoritos
    total_favoritos = len(usuario.favoritos)
    
    return {
        "usuario": usuario,
        "total_publicaciones": total_publicaciones,
        "total_comentarios": total_comentarios,
        "total_favoritos": total_favoritos
    }