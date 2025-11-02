"""
Esquemas Pydantic de la aplicación.
Exporta todos los esquemas para facilitar importaciones.
"""

# Usuario
from .usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioCambiarContraseña,
    UsuarioResponse,
    UsuarioSimple,
    UsuarioPerfil
)

# Publicacion
from .publicacion import (
    PublicacionBase,
    PublicacionCreate,
    PublicacionUpdate,
    PublicacionResponse,
    PublicacionSimple,
    PublicacionDetalle,
    PublicacionPublicar
)

# Comentario
from .comentario import (
    ComentarioBase,
    ComentarioCreate,
    ComentarioUpdate,
    ComentarioResponse,
    ComentarioConRespuestas,
    ComentarioSimple
)

# Reaccion
from .reaccion import (
    ReaccionBase,
    ReaccionCreate,
    ReaccionUpdate,
    ReaccionResponse,
    ReaccionSimple,
    ReaccionToggle
)

# Multimedia
from .multimedia import (
    MultimediaBase,
    MultimediaCreate,
    MultimediaUpdate,
    MultimediaResponse,
    MultimediaSimple,
    MultimediaUpload
)

# Favorito
from .favorito import (
    FavoritoBase,
    FavoritoCreate,
    FavoritoResponse,
    FavoritoConPublicacion,
    FavoritoCheck
)

__all__ = [
    # Usuario
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioCambiarContraseña",
    "UsuarioResponse",
    "UsuarioSimple",
    "UsuarioPerfil",
    
    # Publicacion
    "PublicacionBase",
    "PublicacionCreate",
    "PublicacionUpdate",
    "PublicacionResponse",
    "PublicacionSimple",
    "PublicacionDetalle",
    "PublicacionPublicar",
    
    # Comentario
    "ComentarioBase",
    "ComentarioCreate",
    "ComentarioUpdate",
    "ComentarioResponse",
    "ComentarioConRespuestas",
    "ComentarioSimple",
    
    # Reaccion
    "ReaccionBase",
    "ReaccionCreate",
    "ReaccionUpdate",
    "ReaccionResponse",
    "ReaccionSimple",
    "ReaccionToggle",
    
    # Multimedia
    "MultimediaBase",
    "MultimediaCreate",
    "MultimediaUpdate",
    "MultimediaResponse",
    "MultimediaSimple",
    "MultimediaUpload",
    
    # Favorito
    "FavoritoBase",
    "FavoritoCreate",
    "FavoritoResponse",
    "FavoritoConPublicacion",
    "FavoritoCheck",
]