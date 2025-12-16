# Proyecto Agente Noticias + Flask + Vanilla JS

## Estructura
- news-agent/: Agente IA con LangGraph
- backend/ : API Flask + SQLite
- frontend/ : Página estática JavaScript

## Instrucciones 

1. Crea un entorno virtual de Python y actívalo
   ```
   uv venv
   (Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
   .\.venv\Scripts\activate
   ```
2. Instala dependencias:
   ```
   uv pip install -r requirements.txt
   ```
3. Ve a la carpeta `backend/` e inicia el servidor.
   ```
   python app.py
   ```
   La base de datos SQLite (`posts.db`) se creará automáticamente.
4. Ve a la carpeta `news-agent/` y crea un fichero .env con tu API KEY de OPENAI.
5. Inicia el agente
   ```
   python main.py
   ```
5. Abre `frontend/index.html` en el navegador.

* Prompt ejemplo: "Generate a blog post with three main news from https://bbc.com"

En el backend puedes ajusta el `host` si es necesario para acceder desde otra máquina.