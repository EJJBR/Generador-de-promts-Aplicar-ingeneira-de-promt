from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import generar

app = FastAPI(title="Generador de Prompts")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para la demo; en producción se restringe
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generar.router)

# Sirve el frontend directamente desde FastAPI (así no necesitas 2 servidores para la demo)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")