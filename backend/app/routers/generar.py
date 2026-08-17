from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.services.clasificador import clasificar_consulta, clasificar_consulta_con_imagen
from app.services.imagen_service import procesar_imagen_upload, ImagenValidationError

router = APIRouter()


class ConsultaRequest(BaseModel):
    consulta: str


@router.post("/generar-prompt")
def generar_prompt(datos: ConsultaRequest):
    if not datos.consulta.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    try:
        resultado = clasificar_consulta(datos.consulta)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e}")


@router.post("/generar-prompt/imagen")
async def generar_prompt_imagen(
    consulta: str = Form(...),
    imagen: UploadFile = File(...)
):
    """
    Endpoint para clasificar consultas con imagen adjunta.
    
    Args:
        consulta: texto de la consulta (Form)
        imagen: archivo de imagen (File, multipart/form-data)
        
    Returns:
        dict con clasificación
    """
    if not consulta.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")
    
    try:
        # Procesar imagen a base64
        imagen_b64 = await procesar_imagen_upload(imagen)
        mime_type = imagen.content_type or "image/jpeg"
        
        # Clasificar con imagen
        resultado = clasificar_consulta_con_imagen(consulta, imagen_b64, mime_type)
        return resultado
        
    except ImagenValidationError as e:
        # Error de validación de imagen = 400 (error del cliente)
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        # Error de JSON/API de Groq = 502 (error del servidor)
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")