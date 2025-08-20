#!/usr/bin/env bash
set -e

# --- util: zenity or whiptail fallback ---
has_zenity=false
if command -v zenity >/dev/null 2>&1; then
  has_zenity=true
fi

say_info () {
  if $has_zenity; then
    zenity --info --title="Instalador - Codigo" --text="$1" || true
  else
    echo -e "\n[INFO] $1\n"
  fi
}

ask_yesno () {
  if $has_zenity; then
    zenity --question --title="Instalador - Codigo" --text="$1"
    return $?
  else
    read -p "$1 [s/N]: " resp
    [[ "$resp" == "s" || "$resp" == "S" || "$resp" == "y" || "$resp" == "Y" ]]
    return $?
  fi
}

progress () {
  if $has_zenity; then
    (
      "$@"
      echo "100"
    ) | zenity --progress --title="Instalando Codigo" --percentage=0 --auto-close || true
  else
    "$@"
  fi
}

# --- Begin ---
say_info "Bienvenido al instalador de 'Codigo'.\nSe instalará en su carpeta personal."

# Requiere apt / sudo para dependencias del sistema
if ! command -v sudo >/dev/null 2>&1; then
  say_info "No se encontró 'sudo'. Es posible que se requieran permisos de administrador para instalar dependencias."
fi

# Instalar zenity si no está (mejor experiencia)
if ! $has_zenity; then
  if ask_yesno "¿Desea instalar 'zenity' para un asistente gráfico (recomendado)?"; then
    sudo apt-get update || true
    sudo apt-get install -y zenity || true
    if command -v zenity >/dev/null 2>&1; then
      has_zenity=true
    fi
  fi
fi

INSTALL_DIR="$HOME/codigo_app"
SRC_DIR="$(cd "$(dirname "$0")"/.. && pwd)"

progress bash -c 'echo "0"; sleep 0.2'

# Paquete del sistema necesarios
say_info "Comprobando e instalando dependencias del sistema (python3-venv, ffmpeg, portaudio, xdg-utils)…"
if ask_yesno "¿Instalar dependencias del sistema con apt-get? (Recomendado)"; then
  sudo apt-get update || true
  sudo apt-get install -y python3-venv python3-pip ffmpeg portaudio19-dev xdg-utils || true
fi

# Crear carpeta destino
mkdir -p "$INSTALL_DIR"
cp -r "$SRC_DIR/app" "$INSTALL_DIR/"
cp "$SRC_DIR/scripts/run_app.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/run_app.sh"

# Crear venv e instalar requerimientos
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip wheel setuptools
pip install -r "$INSTALL_DIR/app/requirements.txt"

# Crear .desktop en el sistema del usuario
DESKTOP_FILE="$HOME/.local/share/applications/codigo.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" <<'EOF'
[Desktop Entry]
Name=Codigo (Streamlit App)
Comment=Inicia la aplicación de conversación local
Exec=bash -c "$HOME/codigo_app/run_app.sh"
Terminal=false
Type=Application
Icon=utilities-terminal
Categories=Utility;Education;
EOF

# Registra el escritorio (si procede)
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

# Crear desinstalador
UNINSTALL="$INSTALL_DIR/uninstall.sh"
cat > "$UNINSTALL" <<'EOFU'
#!/usr/bin/env bash
set -e
has_zenity=false
if command -v zenity >/dev/null 2>&1; then has_zenity=true; fi
confirm () {
  if $has_zenity; then
    zenity --question --title="Desinstalador - Codigo" --text="¿Desea desinstalar 'Codigo' y borrar todos sus archivos?"
    return $?
  else
    read -p "¿Desea desinstalar 'Codigo'? [s/N]: " r; [[ "$r" =~ ^[sS]$|^[yY]$ ]]
    return $?
  fi
}

if confirm; then
  pkill -f "streamlit run app.py" 2>/dev/null || true
  rm -f "$HOME/.local/share/applications/codigo.desktop"
  rm -rf "$HOME/codigo_app"
  echo "Desinstalación completada."
else
  echo "Operación cancelada."
fi
EOFU
chmod +x "$UNINSTALL"

# Comprobar Ollama y modelo
if ! command -v ollama >/dev/null 2>&1; then
  if ask_yesno "No se encontró 'ollama'. ¿Desea instalarlo ahora?"; then
    curl -fsSL https://ollama.com/install.sh | sh || true
  fi
fi

if command -v ollama >/dev/null 2>&1; then
  say_info "Comprobando modelo 'llama3.1:latest'…"
  if ! ollama list | grep -q "llama3.1:latest"; then
    if ask_yesno "¿Descargar modelo 'llama3.1:latest' ahora? (~4-8GB)"; then
      ollama pull llama3.1:latest || true
    fi
  fi
fi

say_info "Instalación completada.\nPuede iniciar la app desde el menú o con:\n$HOME/codigo_app/run_app.sh"
