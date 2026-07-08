import json
from app.services.groq_client import get_client
from app.prompts.prompt_diagnostico import SYSTEM_PROMPT

MODEL = "llama-3.3-70b-versatile"


def clasificar_consulta(consulta: str) -> dict:
    """
    Envía la consulta del estudiante a Groq y devuelve un diccionario con:
    tema, nivel, ia_recomendada, justificacion, prompt_optimizado.

    Lanza ValueError si el modelo no devuelve un JSON válido.
    """
    client = get_client()

    respuesta = client.chat.completions.create(
        model=MODEL,
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