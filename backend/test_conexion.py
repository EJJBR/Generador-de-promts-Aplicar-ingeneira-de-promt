import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

respuesta = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Eres un asistente que responde de forma breve."},
        {"role": "user", "content": "¿Cuánto es 15% de 200?"}
    ]
)

print(respuesta.choices[0].message.content)