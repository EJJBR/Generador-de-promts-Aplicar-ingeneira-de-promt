import base64
from io import BytesIO
from typing import List, Tuple
from fastapi import UploadFile
from PIL import Image


class ImagenValidationError(Exception):
    """Excepción para errores de validación de imagen (400)"""
    pass


# Configuración de optimización de imágenes para Render free tier
MAX_IMAGEN_DIMENSION = 1024  # máximo ancho o alto en píxeles
CALIDAD_JPEG = 85  # 0-100, balance entre calidad y tamaño


async def procesar_imagen_upload(archivo: UploadFile) -> str:
    """
    Recibe un archivo de imagen, lo redimensiona, optimiza y convierte a base64.
    Esto reduce el tamaño de datos para el free tier de Render.
    
    Args:
        archivo: UploadFile de FastAPI (imagen)
        
    Returns:
        string con la imagen optimizada en base64
        
    Raises:
        ImagenValidationError: si el archivo no es una imagen válida
    """
    # Validar que sea imagen
    tipos_validos = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if archivo.content_type not in tipos_validos:
        raise ImagenValidationError(
            f"Tipo de archivo no soportado: {archivo.content_type}. "
            f"Formatos válidos: {', '.join(tipos_validos)}"
        )
    
    # Leer contenido
    contenido = await archivo.read()
    
    # Validar y procesar imagen (intentar abrir con PIL)
    try:
        img = Image.open(BytesIO(contenido))
        
        # Convertir RGBA a RGB si es necesario (para JPEG)
        if img.mode in ("RGBA", "LA", "P"):
            # Crear fondo blanco
            fondo = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            fondo.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = fondo
        
        # Redimensionar si es necesario (mantener aspecto)
        if img.width > MAX_IMAGEN_DIMENSION or img.height > MAX_IMAGEN_DIMENSION:
            img.thumbnail((MAX_IMAGEN_DIMENSION, MAX_IMAGEN_DIMENSION), Image.Resampling.LANCZOS)
        
        # Optimizar y convertir a base64
        output = BytesIO()
        # Usar JPEG para mejor compresión (más importante para free tier)
        formato = "JPEG" if archivo.content_type != "image/png" else "PNG"
        
        if formato == "JPEG":
            img.save(output, format="JPEG", quality=CALIDAD_JPEG, optimize=True)
        else:
            img.save(output, format="PNG", optimize=True)
        
        contenido_optimizado = output.getvalue()
        b64_image = base64.b64encode(contenido_optimizado).decode("utf-8")
        return b64_image
        
    except Exception as e:
        raise ImagenValidationError(f"Archivo no es una imagen válida: {str(e)}")


async def procesar_imagenes_upload(archivos: List[UploadFile]) -> List[Tuple[str, str]]:
    """Procesa varias imágenes y devuelve una lista con (base64, mime_type)"""
    if not archivos:
        return []

    resultado = []
    for archivo in archivos:
        resultado.append((await procesar_imagen_upload(archivo), archivo.content_type or "image/jpeg"))
    return resultado


def crear_mensaje_imagen(
    consulta: str,
    imagen_base64: str,
    mime_type: str = "image/jpeg"
) -> dict:
    """Crea un mensaje con una imagen para enviar a Groq."""
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": consulta},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{imagen_base64}"}
            }
        ]
    }


def crear_mensaje_varias_imagenes(
    consulta: str,
    imagenes: List[Tuple[str, str]]
) -> dict:
    """Crea un mensaje con varias imágenes para enviar a Groq."""
    contenido = [{"type": "text", "text": consulta}]

    for imagen_base64, mime_type in imagenes:
        contenido.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{imagen_base64}"}
        })

    return {"role": "user", "content": contenido}
