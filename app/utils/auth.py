"""
Utilidades de autenticación.
Maneja hashing de contraseñas y JWT tokens.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
SECRET_KEY = os.getenv("SECRET_KEY", "tu_secret_key_super_segura_cambiar_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Contexto de hashing (bcrypt)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Número de rondas de hashing
    bcrypt__ident="2b"  # Versión de bcrypt
)


# ============================================
# FUNCIONES DE HASHING
# ============================================

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    Bcrypt tiene un límite de 72 bytes, así que truncamos si es necesario.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Contraseña hasheada
    """
    # Bcrypt solo puede hashear hasta 72 bytes
    # Truncar la contraseña si es necesaria (aunque nuestras validaciones ya limitan a 100 chars)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada
        
    Returns:
        bool: True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# FUNCIONES DE JWT
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token.
    
    Args:
        data: Datos a codificar en el token (ej: {"sub": user_id})
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    # Calcular expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Crear token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT token.
    
    Args:
        token: JWT token a decodificar
        
    Returns:
        dict: Datos decodificados del token
        None: Si el token es inválido o expiró
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extrae el user_id de un JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        str: User ID
        None: Si el token es inválido
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None