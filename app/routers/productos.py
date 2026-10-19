import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.schemas.producto import ProductoCreate, ProductoOut
from app.services import productos as service
from app.utils.archivos import parece_imagen, EXTENSIONES_VALIDAS

router = APIRouter(prefix="/productos", tags=["Productos"])

UPLOAD_DIR = Path("uploads/productos")
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


@router.get("/", response_model=list[ProductoOut])
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre: str | None = None,
    precio_max: float | None = Query(None, gt=0),
    categoria: str | None = None,
    db: Session = Depends(get_db),
):
    return service.listar_productos(db, skip, limit, nombre, precio_max, categoria)


@router.get("/{producto_id}", response_model=ProductoOut)
def detalle(producto_id: int, db: Session = Depends(get_db)):
    return service.obtener_producto(db, producto_id)


@router.post("/", response_model=ProductoOut, status_code=201,
             dependencies=[Depends(require_admin)])
def crear(producto: ProductoCreate, db: Session = Depends(get_db)):
    return service.crear_producto(db, producto)


@router.put("/{producto_id}", response_model=ProductoOut,
            dependencies=[Depends(require_admin)])
def actualizar(producto_id: int, producto: ProductoCreate, db: Session = Depends(get_db)):
    return service.actualizar_producto(db, producto_id, producto)


@router.delete("/{producto_id}", status_code=204,
               dependencies=[Depends(require_admin)])
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    service.eliminar_producto(db, producto_id)


# ---------------------------------------------------------------------------
# Clase 10 — subida de imagen
# ---------------------------------------------------------------------------
@router.post("/{producto_id}/imagen", response_model=ProductoOut,
             dependencies=[Depends(require_admin)])
def subir_imagen(producto_id: int, archivo: UploadFile = File(...),
                 db: Session = Depends(get_db)):
    # 1. Extensión válida (más barato)
    sufijo = Path(archivo.filename).suffix.lower()
    if sufijo not in EXTENSIONES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Extensión no permitida. Usá: {', '.join(EXTENSIONES_VALIDAS)}",
        )

    contenido = archivo.file.read()

    # 2. Tamaño
    if len(contenido) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La imagen no puede superar 2 MB",
        )

    # 3. Firma real del archivo (magic bytes)
    if not parece_imagen(contenido):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El archivo no parece una imagen válida (firma incorrecta)",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{producto_id}-{secrets.token_hex(8)}{sufijo}"
    ruta = UPLOAD_DIR / nombre_archivo
    ruta.write_bytes(contenido)

    imagen_url = f"/static/productos/{nombre_archivo}"
    return service.actualizar_imagen(db, producto_id, imagen_url)
