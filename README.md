# Generador de Prompts — Tesis

Sistema web que recibe consultas simples de estudiantes de secundaria, aplica técnicas de ingeniería de prompts y recomienda qué modelo de IA (Claude, GPT, Gemini, DeepSeek, etc.) conviene usar para resolverlas, junto con el prompt ya optimizado.

Este proyecto es el instrumento experimental de la tesis:

> **Diseño e implementación de un generador de prompts y su efecto en la percepción de la competencia resuelve problemas de gestión de datos e incertidumbre**
> I.E. Juan Pablo Vizcardo y Guzmán, Comas — 3er año de secundaria.

## Objetivo del sistema

Un estudiante escribe su consulta (por ejemplo, una duda sobre estadística) y el sistema:

1. **Clasifica** la consulta por tema y nivel de complejidad
2. **Recomienda** la IA más adecuada según el tipo de tarea (documentación paso a paso → Claude, explicaciones detalladas → GPT, diagramas → Gemini, consultas largas → DeepSeek)
3. **Genera** un prompt optimizado (aplicando técnicas como Chain-of-Thought, few-shot, persona prompting) listo para que el alumno lo pegue en la IA recomendada

## Arquitectura (3 capas)

```
Consulta del alumno
        │
        ▼
┌─────────────────────┐
│ 1. Diagnóstico       │  → clasifica tema + nivel de complejidad
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 2. Selección de      │  → decide qué IA recomendar
│    intención          │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ 3. Salida restringida │  → genera el prompt final optimizado
└─────────────────────┘
        │
        ▼
Resultado: IA recomendada + prompt listo para usar
```

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python + FastAPI |
| Modelo de clasificación | Groq API (`llama-3.3-70b-versatile`) |
| Frontend | HTML / CSS / JS |
| Despliegue | Backend en Render/Railway · Frontend estático |

No se usa GPU ni modelos locales en producción — el servidor en la nube solo hace llamadas HTTP a la API de Groq, lo que mantiene el hosting ligero y de bajo costo.

## Estructura del proyecto

```
generador-prompts/
├── backend/
│   ├── app/
│   │   ├── main.py              # arranque de FastAPI
│   │   ├── config.py            # variables de entorno / API key
│   │   ├── routers/
│   │   │   └── generar.py       # endpoint /generar-prompt
│   │   ├── services/
│   │   │   ├── groq_client.py   # conexión a la API de Groq
│   │   │   ├── clasificador.py  # Capa 1: diagnóstico
│   │   │   └── recomendador.py  # Capa 2: selección + prompt final
│   │   └── prompts/
│   │       ├── prompt_diagnostico.py
│   │       └── prompt_seleccion.py
│   ├── tests/
│   │   └── test_clasificador.py # pruebas con consultas típicas de estadística
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── docs/                        # matriz de consistencia, artículo, cronograma
```

## Configuración local

1. Clonar el repositorio
2. Crear entorno virtual e instalar dependencias:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
3. Copiar `.env.example` a `.env` y agregar tu API key de Groq:
   ```
   GROQ_API_KEY=tu_api_key_aqui
   ```
4. Ejecutar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

**Importante:** el archivo `.env` nunca se sube a GitHub (ya está en `.gitignore`). Cada quien usa su propia API key localmente, y en producción se configura como variable de entorno en el panel del proveedor de hosting.

## Contexto de la investigación

- **Población:** 56 estudiantes de 3er año de secundaria (secciones A y B)
- **Grupo control:** sección A (28 alumnos, sin el sistema)
- **Grupo experimental:** sección B (28 alumnos, usando el generador de prompts)
- **Tema curricular:** Estadística (implementación a mediados de agosto)
- **Diseño:** Cuasi-experimental, cuantitativo, con pretest y postest (escala de percepción tipo Likert)

## Estado del proyecto

- [x] Matriz de consistencia definida
- [x] Elección de stack y API (Groq)
- [x] Estructura de carpetas
- [ ] Capa de diagnóstico (clasificación tema + nivel)
- [ ] Capa de selección de intención (recomendación de IA)
- [ ] Generación del prompt optimizado
- [ ] Endpoint FastAPI
- [ ] Frontend
- [ ] Pruebas con consultas reales de estadística
- [ ] Validación con la docente del curso
- [ ] Despliegue en la nube