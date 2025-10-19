"""
Modelos de la aplicación.
Exporta todos los modelos para facilitar importaciones.
"""

from .usuario import Usuario
from .publicacion import Publicacion, EstatusPublicacion
from .comentario import Comentario, EstatusComentario
from .reaccion import Reaccion, TipoReaccion
from .multimedia import Multimedia, TipoMultimedia
from .favorito import Favorito

# Exportar todos los modelos
__all__ = [
    "Usuario",
    "Publicacion",
    "EstatusPublicacion",
    "Comentario",
    "EstatusComentario",
    "Reaccion",
    "TipoReaccion",
    "Multimedia",
    "TipoMultimedia",
    "Favorito",
]