"""
Utilidades para Cloudinary.
Maneja subida y obtención de archivos multimedia.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURACIÓN DE CLOUDINARY
# ============================================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "")
)


# ============================================
# FUNCIONES DE SUBIDA
# ============================================

def upload_image(
    file_path: str,
    folder: str = "sazon_toto",
    public_id: Optional[str] = None,
    overwrite: bool = True
) -> Optional[Dict]:
    """
    Sube una imagen a Cloudinary.
    
    Args:
        file_path: Ruta del archivo a subir (puede ser path local o URL)
        folder: Carpeta en Cloudinary donde se guardará
        public_id: ID público personalizado (opcional)
        overwrite: Si True, sobrescribe archivo existente
        
    Returns:
        dict: Información del archivo subido (url, public_id, etc.)
        None: Si falla la subida
        
    Example:
        >>> result = upload_image("foto_perfil.jpg", folder="usuarios", public_id="user_123")
        >>> print(result['secure_url'])
        'https://res.cloudinary.com/...'
    """
    try:
        upload_options = {
            "folder": folder,
            "overwrite": overwrite,
            "resource_type": "image"
        }
        
        if public_id:
            upload_options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **upload_options)
        
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at")
        }
        
    except Exception as e:
        print(f"Error al subir imagen a Cloudinary: {e}")
        return None


def upload_video(
    file_path: str,
    folder: str = "sazon_toto/videos",
    public_id: Optional[str] = None,
    overwrite: bool = True
) -> Optional[Dict]:
    """
    Sube un video a Cloudinary.
    
    Args:
        file_path: Ruta del archivo de video
        folder: Carpeta en Cloudinary
        public_id: ID público personalizado
        overwrite: Si True, sobrescribe archivo existente
        
    Returns:
        dict: Información del video subido
        None: Si falla la subida
    """
    try:
        upload_options = {
            "folder": folder,
            "overwrite": overwrite,
            "resource_type": "video"
        }
        
        if public_id:
            upload_options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(file_path, **upload_options)
        
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "duration": result.get("duration"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at")
        }
        
    except Exception as e:
        print(f"Error al subir video a Cloudinary: {e}")
        return None


# ============================================
# FUNCIONES DE OBTENCIÓN
# ============================================

def get_cloudinary_url(public_id: str, resource_type: str = "image") -> Optional[str]:
    """
    Obtiene la URL de un recurso en Cloudinary.
    
    Args:
        public_id: ID público del recurso
        resource_type: Tipo de recurso ('image', 'video', 'raw')
        
    Returns:
        str: URL segura del recurso
        None: Si no existe
    """
    try:
        # Construir URL
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        if not cloud_name:
            return None
        
        url = f"https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{public_id}"
        return url
        
    except Exception as e:
        print(f"Error al obtener URL de Cloudinary: {e}")
        return None


def get_image_info(public_id: str) -> Optional[Dict]:
    """
    Obtiene información de una imagen en Cloudinary.
    
    Args:
        public_id: ID público de la imagen
        
    Returns:
        dict: Información de la imagen
        None: Si no existe o falla
    """
    try:
        result = cloudinary.api.resource(public_id, resource_type="image")
        
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes"),
            "created_at": result.get("created_at")
        }
        
    except Exception as e:
        print(f"Error al obtener info de imagen: {e}")
        return None


# ============================================
# FUNCIONES DE ELIMINACIÓN
# ============================================

def delete_cloudinary_file(public_id: str, resource_type: str = "image") -> bool:
    """
    Elimina un archivo de Cloudinary.
    
    Args:
        public_id: ID público del recurso
        resource_type: Tipo de recurso ('image', 'video', 'raw')
        
    Returns:
        bool: True si se eliminó, False si falló
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get("result") == "ok"
        
    except Exception as e:
        print(f"Error al eliminar archivo de Cloudinary: {e}")
        return False


# ============================================
# FUNCIONES DE TRANSFORMACIÓN
# ============================================

def get_thumbnail_url(public_id: str, width: int = 300, height: int = 300) -> str:
    """
    Genera URL de thumbnail de una imagen.
    
    Args:
        public_id: ID público de la imagen
        width: Ancho del thumbnail
        height: Alto del thumbnail
        
    Returns:
        str: URL del thumbnail
    """
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    return f"https://res.cloudinary.com/{cloud_name}/image/upload/w_{width},h_{height},c_fill/{public_id}"