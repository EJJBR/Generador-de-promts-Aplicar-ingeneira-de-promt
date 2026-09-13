import json
import logging
import os
from datetime import datetime, timezone

from app.services.groq_client import get_client
from app.prompts.prompt_diagnostico import SYSTEM_PROMPT as SYSTEM_PROMPT_TEXTO
from app.prompts.prompt_seleccion import SYSTEM_PROMPT as SYSTEM_PROMPT_VISUAL
from app.services.imagen_service import crear_mensaje_imagen, crear_mensaje_varias_imagenes

logger = logging.getLogger(__name__)

MODEL_TEXTO = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
MODEL_VISION = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")
MODEL_VISION_FALLBACK = os.getenv("GROQ_VISION_FALLBACK_MODEL", "qwen/qwen3.8-27b")


def _extract_json_from_content(contenido: str) -> dict:
    """Intenta cargar una respuesta JSON de Groq y la convierte en dict."""
    try:
        resultado = json.loads(contenido)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"El modelo no devolvió un JSON válido.\nRespuesta cruda:\n{contenido}"
        ) from e
    return resultado


def _es_groq_rate_limit_error(exc: Exception) -> bool:
    """Detecta fallos de Groq por cuota/OTPM o salida por minuto."""
    texto = str(exc).lower()
    return (
        "rate_limit_exceeded" in texto
        or "otpm" in texto
        or "output tokens per minute" in texto
        or "request too large" in texto
        or "max completion tokens" in texto
        or "429" in texto
    )


def clasificar_consulta(consulta: str) -> dict:
    """
    Envía la consulta del estudiante a Groq y devuelve un diccionario con:
    tema, nivel, ia_recomendada, justificacion, prompt_optimizado.

    Lanza ValueError si el modelo no devuelve un JSON válido.
    """
    client = get_client()
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("groq_text_route_attempt model=%s at=%s", MODEL_TEXTO, timestamp)

    try:
        respuesta = client.chat.completions.create(
            model=MODEL_TEXTO,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_TEXTO},
                {"role": "user", "content": consulta},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        contenido = respuesta.choices[0].message.content
        return _extract_json_from_content(contenido)
    except Exception as exc:
        logger.warning("groq_text_route_failed model=%s at=%s error=%s", MODEL_TEXTO, timestamp, str(exc))
        raise


def clasificar_consulta_con_imagen(
    consulta: str, imagen_base64: str, mime_type: str = "image/jpeg"
) -> dict:
    """Compatibilidad: envía una sola imagen a Groq usando modelo de visión."""
    return clasificar_consulta_con_varias_imagenes(consulta, [(imagen_base64, mime_type)])


def clasificar_consulta_con_varias_imagenes(
    consulta: str, imagenes: list[tuple[str, str]]
) -> dict:
    """Envía consulta + varias imágenes a Groq usando modelo de visión.

    Si el modelo visual principal se satura por cuota o rate limit, intenta un
    modelo visual de fallback y, si ese también falla, degrada a texto.
    """
    if not imagenes:
        raise ValueError("Debe enviarse al menos una imagen.")

    client = get_client()
    mensaje_usuario = crear_mensaje_varias_imagenes(consulta, imagenes)
    last_error = None

    for model in (MODEL_VISION, MODEL_VISION_FALLBACK):
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(
            "groq_image_route_attempt model=%s at=%s images=%d consulta_len=%d",
            model,
            timestamp,
            len(imagenes),
            len(consulta),
        )
        try:
            respuesta = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_VISUAL},
                    mensaje_usuario,
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            contenido = respuesta.choices[0].message.content
            return _extract_json_from_content(contenido)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "groq_image_route_failed model=%s at=%s error=%s",
                model,
                timestamp,
                str(exc),
            )
            if not _es_groq_rate_limit_error(exc):
                raise

    # Degradación a texto: si el multimodal falla por rate limits, se hace
    # un intento de respuesta textual sin imagen. Esto evita romper el flujo.
    degrade_at = datetime.now(timezone.utc).isoformat()
    logger.warning(
        "groq_image_degrade_to_text at=%s models=%s,%s reason=%s",
        degrade_at,
        MODEL_VISION,
        MODEL_VISION_FALLBACK,
        str(last_error),
    )
    try:
        logger.info(
            "groq_text_fallback_attempt model=%s at=%s",
            MODEL_TEXTO,
            datetime.now(timezone.utc).isoformat(),
        )
        return clasificar_consulta(consulta)
    except Exception as text_exc:
        logger.warning(
            "groq_text_fallback_failed model=%s at=%s error=%s",
            MODEL_TEXTO,
            datetime.now(timezone.utc).isoformat(),
            str(text_exc),
        )
        # Si el fallback textual tampoco se puede resolver, devolvemos el
        # error original de rate limit para no enmascarar el origen del problema.
        raise last_error or ValueError("No fue posible procesar la consulta con imagen.")