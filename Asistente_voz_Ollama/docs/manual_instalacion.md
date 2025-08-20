# Manual de instalación — Codigo (Ubuntu)

## Requisitos
- Ubuntu 22.04/24.04/24.10
- Conexión a Internet para instalar dependencias y el modelo (opcional).
- Espacio en disco: 6–12 GB si instala Ollama + modelo `llama3.1:latest`.

## Pasos
1. Descargue y extraiga el archivo `codigo_instalador_ubuntu.zip` en su carpeta personal.
2. Haga clic derecho en la carpeta y seleccione “Abrir en terminal”.
3. Ejecute el instalador:
   ```bash
   bash scripts/install.sh
   ```
   El asistente (zenity) le guiará con: **siguiente, siguiente, aceptar**.
4. Al finalizar, se crea un acceso directo en **Menú / Buscador de aplicaciones**: **Codigo (Streamlit App)**.
5. Para desinstalar, ejecute:
   ```bash
   bash ~/codigo_app/uninstall.sh
   ```

## Notas
- Se creará un entorno virtual en `~/codigo_app/venv`.
- Las dependencias de sistema usadas: `python3-venv`, `ffmpeg`, `portaudio19-dev`, `xdg-utils`.
- Si desea instalar **Ollama** y el modelo `llama3.1:latest`, el asistente puede hacerlo por usted.
