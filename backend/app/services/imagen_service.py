import base64
from io import BytesIO
from fastapi import UploadFile
from PIL import Image


class ImagenValidationError(Exception):
    """Excepción para errores de validación de imagen (400)"""
    pass


async def procesar_imagen_upload(archivo: UploadFile) -> str:
    """
    Recibe un archivo de imagen y lo convierte a base64.
    
    Args:
        archivo: UploadFile de FastAPI (imagen)
        
    Returns:
        string con la imagen en base64
        
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
    
    # Validar que sea imagen real (intentar abrir con PIL)
    try:
        img = Image.open(BytesIO(contenido))
        img.verify()
    except Exception as e:
        raise ImagenValidationError(f"Archivo no es una imagen válida: {str(e)}")
    
    # Convertir a base64
    b64_image = base64.b64encode(contenido).decode("utf-8")
    return b64_image


def crear_mensaje_imagen(
    consulta: str,
    imagen_base64: str,
    mime_type: str = "image/jpeg"
) -> dict:
    """
    Crea un mensaje con imagen para enviar a Groq.
    
    Args:
        consulta: texto de la consulta del usuario
        imagen_base64: imagen codificada en base64
        mime_type: tipo MIME de la imagen (default: image/jpeg)
        
    Returns:
        dict con estructura de mensaje para Groq
    """
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
