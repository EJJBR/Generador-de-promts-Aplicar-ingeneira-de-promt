import json
import os
from app.services.groq_client import get_client
from app.prompts.prompt_diagnostico import SYSTEM_PROMPT
from app.services.imagen_service import crear_mensaje_imagen, crear_mensaje_varias_imagenes

MODEL_TEXTO = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
MODEL_VISION = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")


def clasificar_consulta(consulta: str) -> dict:
    """
    Envía la consulta del estudiante a Groq y devuelve un diccionario con:
    tema, nivel, ia_recomendada, justificacion, prompt_optimizado.

    Lanza ValueError si el modelo no devuelve un JSON válido.
    """
    client = get_client()

    respuesta = client.chat.completions.create(
        model=MODEL_TEXTO,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": consulta},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    contenido = respuesta.choices[0].message.content

    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El modelo no devolvió un JSON válido.\nRespuesta cruda:\n{contenido}"
        ) from e

    return resultado


def clasificar_consulta_con_imagen(
    consulta: str, imagen_base64: str, mime_type: str = "image/jpeg"
) -> dict:
    """Compatibilidad: envía una sola imagen a Groq usando modelo de visión."""
    return clasificar_consulta_con_varias_imagenes(consulta, [(imagen_base64, mime_type)])


def clasificar_consulta_con_varias_imagenes(
    consulta: str, imagenes: list[tuple[str, str]]
) -> dict:
    """Envía consulta + varias imágenes a Groq usando modelo de visión."""
    if not imagenes:
        raise ValueError("Debe enviarse al menos una imagen.")

    client = get_client()
    mensaje_usuario = crear_mensaje_varias_imagenes(consulta, imagenes)

    respuesta = client.chat.completions.create(
        model=MODEL_VISION,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            mensaje_usuario,
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    contenido = respuesta.choices[0].message.content

    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El modelo no devolvió un JSON válido.\nRespuesta cruda:\n{contenido}"
        ) from e

    return resultado