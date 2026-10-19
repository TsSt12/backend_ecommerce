import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioOut
from app.core.security import hash_password

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me/datos", response_model=UsuarioOut)
def mis_datos(current_user: Usuario = Depends(get_current_user)):
    """Devuelve todos los datos personales almacenados (Ley 25.326, acceso)."""
    return current_user


@router.get("/me/exportar")
def exportar_datos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Descarga un JSON con todos los datos personales (Ley 25.326, portabilidad)."""
    pedidos_data = []
    for pedido in current_user.pedidos:
        items_data = [
            {
                "producto_id": item.producto_id,
                "cantidad": item.cantidad,
                "precio_unitario": str(item.precio_unitario),
            }
            for item in pedido.items
        ]
        revocacion = None
        if pedido.revocacion:
            revocacion = {
                "codigo": pedido.revocacion.codigo,
                "creada_en": str(pedido.revocacion.creada_en),
            }
        pedidos_data.append({
            "id": pedido.id,
            "estado": pedido.estado,
            "total": str(pedido.total),
            "creado_en": str(pedido.creado_en),
            "items": items_data,
            "revocacion": revocacion,
        })

    datos = {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol,
        "acepto_tratamiento": current_user.acepto_tratamiento,
        "fecha_consentimiento": str(current_user.fecha_consentimiento),
        "activo": current_user.activo,
        "pedidos": pedidos_data,
    }
    contenido = json.dumps(datos, ensure_ascii=False, indent=2)
    return Response(
        content=contenido,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="mis-datos-{current_user.id}.json"'
        },
    )


@router.delete("/me", status_code=204)
def dar_de_baja(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Anonimiza al usuario (Ley 25.326, derecho al olvido).
    No borra la fila para preservar integridad referencial de pedidos.
    Los pedidos son registros comerciales y deben conservarse.
    """
    uid = current_user.id
    current_user.nombre = f"Usuario eliminado #{uid}"
    current_user.email = f"eliminado_{uid}@anonimizado.invalid"
    current_user.hashed_password = hash_password(f"BAJA-{uid}-{datetime.utcnow().isoformat()}")
    current_user.activo = False
    current_user.fecha_baja = datetime.utcnow()
    db.commit()
