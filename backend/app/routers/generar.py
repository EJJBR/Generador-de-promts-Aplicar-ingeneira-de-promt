from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.services.clasificador import (
    clasificar_consulta,
    clasificar_consulta_con_varias_imagenes,
)
from app.services.imagen_service import (
    procesar_imagenes_upload,
    ImagenValidationError,
)

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
    imagenes: List[UploadFile] = File(default_factory=list),
    imagen: Optional[UploadFile] = File(default=None),
):
    """Endpoint para clasificar consultas con una o varias imágenes adjuntas."""
    if not consulta.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    archivos = list(imagenes or [])
    if imagen is not None:
        archivos.append(imagen)

    if not archivos:
        raise HTTPException(status_code=400, detail="Debe adjuntar al menos una imagen.")

    try:
        imagenes_procesadas = await procesar_imagenes_upload(archivos)
        resultado = clasificar_consulta_con_varias_imagenes(consulta, imagenes_procesadas)
        return resultado
    except ImagenValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")