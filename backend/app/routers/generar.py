from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.clasificador import clasificar_consulta

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