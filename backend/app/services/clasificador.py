import json
from app.services.groq_client import get_client
from app.prompts.prompt_diagnostico import SYSTEM_PROMPT
from app.services.imagen_service import crear_mensaje_imagen

MODEL_TEXTO = "llama-3.3-70b-versatile"
MODEL_VISION = "qwen/qwen3-32b"


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
    """
    Envía consulta + imagen a Groq usando modelo de visión (Qwen).
    Devuelve clasificación con tema, nivel, ia_recomendada, justificacion, prompt_optimizado.
    
    Args:
        consulta: texto de la consulta del estudiante
        imagen_base64: imagen codificada en base64
        mime_type: tipo MIME de la imagen (default: image/jpeg)
        
    Returns:
        dict con clasificación
        
    Raises:
        ValueError: si el modelo no devuelve JSON válido
    """
    client = get_client()
    
    mensaje_usuario = crear_mensaje_imagen(consulta, imagen_base64, mime_type)
    
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