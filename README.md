# Proyecto Agente Noticias + Flask + Vanilla JS

## Estructura
- news-agent/: Agente IA con LangGraph
- backend/ : API Flask + SQLite
- frontend/ : Página estática JS

## Instrucciones 

1. Crea un entorno virtual de Python y actívalo
   ```
   uv venv
   .\venv\Scripts\activate
   ```
2. Instala dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Ve a la carpeta `backend/` e inicia el servidor.
   ```
   python app.py
   ```
   La base de datos SQLite (`posts.db`) se creará automáticamente.
4. Ve a la carpeta `news-agent/` e inicia el agente.
   ```
   python main.py
   ```
5. Abre `frontend/index.html` en el navegador.

En el backend puedes ajusta el `host` si es necesario para acceder desde otra máquina.