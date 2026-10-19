from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import auth, pedidos, productos, usuarios

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "API REST de e-commerce de stickers. "
        "Cumple con la Ley 24.240, Disposición 954/2025 y Ley 25.326."
    ),
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(productos.router)
app.include_router(auth.router)
app.include_router(pedidos.router)
app.include_router(usuarios.router)

# ---------------------------------------------------------------------------
# Archivos estáticos: imágenes subidas + demo
# ---------------------------------------------------------------------------
Path("uploads").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Imágenes de demo (sí se suben al repo)
Path("app/static/demo").mkdir(parents=True, exist_ok=True)
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")


# ---------------------------------------------------------------------------
# Raíz
# ---------------------------------------------------------------------------
@app.get("/", tags=["Raíz"])
def raiz():
    return {
        "mensaje": "Bienvenido a la API de Stickers",
        "tipo": "API de e-commerce sujeta a la Ley 24.240 de Defensa del Consumidor",
        "docs": "/docs",
        "redoc": "/redoc",
    }
