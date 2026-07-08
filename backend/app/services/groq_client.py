import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = None


def get_client() -> Groq:
    """Devuelve una instancia única (singleton) del cliente de Groq."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "No se encontró GROQ_API_KEY. Revisa que exista un archivo .env "
                "en la carpeta backend/ con tu API key configurada."
            )
        _client = Groq(api_key=api_key)
    return _client