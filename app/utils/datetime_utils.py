from datetime import datetime
from zoneinfo import ZoneInfo

# Configurar tu zona horaria
TIMEZONE = ZoneInfo("America/Mexico_City")  # O la que uses

def now():
    """Retorna el datetime actual en la zona horaria configurada."""
    return datetime.now(TIMEZONE)

def utc_now():
    """Retorna el datetime actual en UTC."""
    return datetime.now(ZoneInfo("UTC"))