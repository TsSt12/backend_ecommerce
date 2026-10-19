"""
seed.py — datos de demo para poblar la base.
Uso: python app/seed.py
Requiere que las tablas ya existan (alembic upgrade head).
"""
from app.db.database import SessionLocal
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.core.security import hash_password
from datetime import datetime, timezone

PRODUCTOS = [
    dict(nombre="Pack Gatos Ninja x10",      categoria="Animales",   precio_final=2500,
         cuotas_cantidad=3, cuotas_valor=833.33, garantia_meses=3, stock=40,
         imagen_url="/demo/gatos-ninja.png"),
    dict(nombre="Pack Gamer Retro x8",        categoria="Gamer",      precio_final=2800,
         cuotas_cantidad=3, cuotas_valor=933.33, garantia_meses=3, stock=35,
         imagen_url="/demo/gamer-retro.png"),
    dict(nombre="Frases Motivadoras x12",     categoria="Frases",     precio_final=2200,
         cuotas_cantidad=3, cuotas_valor=733.33, garantia_meses=3, stock=50,
         imagen_url="/demo/frases.png"),
    dict(nombre="Plantas y Suculentas x10",   categoria="Naturaleza", precio_final=2400,
         cuotas_cantidad=3, cuotas_valor=800.00, garantia_meses=3, stock=30,
         imagen_url="/demo/plantas.png"),
    dict(nombre="Astronautas y Planetas x9",  categoria="Espacio",    precio_final=2600,
         cuotas_cantidad=3, cuotas_valor=866.67, garantia_meses=3, stock=25,
         imagen_url="/demo/espacio.png"),
    dict(nombre="Sticker Holográfico Gigante",categoria="Premium",    precio_final=1800,
         cuotas_cantidad=1, cuotas_valor=1800,   garantia_meses=6, stock=15,
         imagen_url="/demo/holografico.png"),
]

USUARIOS_DEMO = [
    dict(nombre="Admin Stickers", email="admin@stickers.com", password="Admin1234!",
         rol="admin"),
    dict(nombre="Cliente Demo",   email="cliente@demo.com",   password="Cliente123!",
         rol="customer"),
]


def seed():
    db = SessionLocal()
    try:
        # Productos
        if db.query(Producto).count() == 0:
            for p in PRODUCTOS:
                db.add(Producto(**p))
            print(f"✓ {len(PRODUCTOS)} productos insertados")
        else:
            print("· Productos ya existen, se omiten")

        # Usuarios
        for u in USUARIOS_DEMO:
            if not db.query(Usuario).filter(Usuario.email == u["email"]).first():
                db.add(Usuario(
                    nombre=u["nombre"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    rol=u["rol"],
                    acepto_tratamiento=True,
                    fecha_consentimiento=datetime.now(timezone.utc),
                ))
                print(f"✓ Usuario {u['email']} insertado")
            else:
                print(f"· Usuario {u['email']} ya existe")

        db.commit()
        print("\n✅ Seed completo")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
