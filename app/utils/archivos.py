"""
Detección de tipo real de archivo por magic bytes.
Se usa en el endpoint de subida de imágenes para evitar
que un atacante renombre un archivo ejecutable como .jpg.
"""

# Firmas (magic bytes) de los formatos permitidos
_FIRMAS: dict[bytes, str] = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"RIFF": "webp",   # completamos con 'WEBP' en offset 8
}

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp"}


def parece_imagen(contenido: bytes) -> bool:
    """Devuelve True si el contenido tiene las magic bytes de jpg, png o webp."""
    if contenido[:3] == b"\xff\xd8\xff":
        return True
    if contenido[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return True
    return False
