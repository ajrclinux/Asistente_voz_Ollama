#!/usr/bin/env bash
set -e
APP_DIR="$HOME/codigo_app"
cd "$APP_DIR/app"

# Activa el entorno
source "$APP_DIR/venv/bin/activate"

# Lanza Streamlit (sin abrir navegador si es servidor)
export BROWSER=xdg-open
streamlit run app.py --server.headless=false --server.address=127.0.0.1 --server.port=8501
