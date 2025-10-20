from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuario

# Metadata de la API
app = FastAPI(
    title="El Sazón de Toto API",
    description="API para la red social de recetas 'El Sazón de Toto'",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Configurar CORS para permitir peticiones desde Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REGISTRAR ROUTERS
# ============================================
app.include_router(
    usuario.router,
    prefix="/api/usuarios",
    tags=["Usuarios"]
)

# ============================================
# RUTA RAÍZ
# ============================================
@app.get("/")
async def root():
    return {
        "message": "¡Bienvenido a El Sazón de Toto API!",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 API iniciada correctamente")
    print("📚 Documentación: http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 API detenida")