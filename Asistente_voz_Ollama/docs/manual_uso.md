# Manual de uso — Codigo

## Inicio
- Inicie desde el acceso directo **Codigo (Streamlit App)** o con:
  ```bash
  ~/codigo_app/run_app.sh
  ```

## Dentro de la app
- **Límite de palabras** y **velocidad de voz** se configuran en la barra lateral.
- **Guardar conversación**: botón para descargar el historial en JSON.
- **Cargar conversación**: suba un JSON guardado previamente.
- **Voz**: botón “Iniciar Conversación de Voz”.
- Para finalizar conversación por voz, diga **“adiós”**.

## Requisitos de backend
- Debe estar ejecutándose **Ollama** en `http://localhost:11434/` y tener el modelo `llama3.1:latest` descargado.
  - Iniciar servicio de Ollama (si fuera necesario):
    ```bash
    ollama serve
    ```

## Solución de problemas
- Si no suena la voz: asegúrese de tener **ffmpeg** instalado.
- Para micrófono: en algunos equipos se requiere dar permisos o seleccionar dispositivo.
- PyAudio necesita `portaudio19-dev` (el instalador lo incluye).
