import streamlit as st
import os
import json
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
import requests
from pydub import AudioSegment
from pydub.playback import play

# 1. --- Requiere que ollama esté instalado en el sistema ---
# Instalacion de ollama:
        # curl -fsSL https://ollama.com/install.sh | sh

# 2. --- También requiere que el modelo "llama3.1:latest" esté instalado en el sistema ---
# Descarga modelo:
        # ollama pull llama3.1:latest

# 3. --- Crear entorno ---
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# streamlit run app.py

# 4. --- NOTA DE DEPENDENCIAS ---
# Este script requiere librerías adicionales. Instálalas con:
# pip install streamlit gTTS pydub SpeechRecognition requests PyAudio

# 5. --- requirements.txt ---
# streamlit
# gTTS
# pydub
# SpeechRecognition
# requests
# PyAudio



# --- Configuración de la Página y Ollama ---
OLAMMA_SERVER = "http://localhost:11434"

# Constantes de la aplicación
APP_VERSION = "v.2.0.0"
APP_DATE = "19/08/2025"
APP_AUTHOR = "@jrclinux"
USER_ICON = "👤"
ASSISTANT_ICON = "🧠"

# Configuración de la página
st.set_page_config(
    page_title=f"{APP_AUTHOR}'s v.{APP_VERSION}",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de Gestión de Conversación ---
def new_conversation():
    """Limpia el historial de mensajes para iniciar una nueva conversación."""
    st.session_state.messages = []

def load_conversation(uploaded_file):
    """Carga el historial de mensajes desde un archivo JSON."""
    if uploaded_file:
        try:
            string_data = uploaded_file.getvalue().decode("utf-8")
            st.session_state.messages = json.loads(string_data)
        except json.JSONDecodeError:
            st.error("El archivo no es un JSON válido. No se pudo cargar la conversación.")
        except Exception as e:
            st.error(f"Ocurrió un error al cargar el archivo: {e}")

# --- Funciones Principales de Audio y LLM ---
def voice_to_text():
    """Captura audio del micrófono y lo convierte a texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Escuchando... Di 'adiós' para terminar.")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="es-ES")
            print(f"Usuario dijo: {text}")
            return text.lower()
        except sr.UnknownValueError:
            st.warning("No se pudo entender el audio. Inténtalo de nuevo.")
            return ""
        except sr.RequestError as e:
            st.error(f"Error en el servicio de reconocimiento de voz; {e}")
            return ""


def text_to_speech(text, speed=1.0):
    """
    Convierte texto a voz, ajusta la velocidad usando pydub y lo reproduce.
    """
    try:
        # 1. Generar el audio con gTTS
        tts = gTTS(text=text, lang='es', slow=False)
        filename = 'response.mp3'
        tts.save(filename)

        # 2. Cargar el audio con pydub
        audio = AudioSegment.from_mp3(filename)

        # 3. Modificar la velocidad del audio
        # Cambiar el frame rate es una forma de acelerar/ralentizar.
        # Puede afectar ligeramente el tono, lo cual es aceptable para la voz.
        if speed != 1.0:
            sound_with_altered_speed = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed)
            })
        else:
            sound_with_altered_speed = audio

        # 4. Reproducir el audio modificado
        play(sound_with_altered_speed)

        # 5. Limpiar el archivo temporal
        os.remove(filename)

    except Exception as e:
        st.error(f"Error al reproducir la respuesta de audio: {e}")
        st.warning("Asegúrate de tener 'ffmpeg' instalado en tu sistema. Es necesario para procesar el audio.")

def generate_response(prompt, max_words):
    """Envía un prompt a Ollama y obtiene una respuesta."""
    endpoint = f"{OLAMMA_SERVER}/api/generate"
    headers = {"Content-Type": "application/json"}

    history = "\n".join([f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}" for msg in st.session_state.messages])
    final_prompt = f"{history}\n\nUsuario: {prompt}\nAsistente (responde en un máximo de {max_words} palabras):"

    data = {"model": "llama3.1:latest", "prompt": final_prompt, "stream": False}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        st.error(f"No se pudo conectar con el servidor de Ollama: {e}")
        return "Lo siento, no pude obtener una respuesta del servidor."
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
        return "Lo siento, ocurrió un error al generar la respuesta."

def voice_conversation_loop():
    """
    Inicia y gestiona un bucle de conversación de voz continua.
    """
    st.session_state.is_conversing = True

    while st.session_state.get('is_conversing', False):
        user_text = voice_to_text()

        if user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user", avatar=USER_ICON):
                st.markdown(user_text)

            if "adiós" in user_text.lower():
                st.session_state.is_conversing = False
                final_message = "¡Hasta luego Antonio!"
                st.success(final_message)
                text_to_speech(final_message, st.session_state.speech_speed)
                # text_to_speech(final_message)
                break

            with st.spinner("Pensando..."):
                # Pasa el valor del slider a la función de generación
                response = generate_response(user_text, st.session_state.max_words)

            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant", avatar=ASSISTANT_ICON):
                st.markdown(response)

            print(f"Asistente responde: {response}")
            text_to_speech(response, st.session_state.speech_speed)

def main():
    """Interfaz Principal de la Aplicación"""
    # Inicialización del estado de sesión
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_conversing" not in st.session_state:
        st.session_state.is_conversing = False
    if 'max_words' not in st.session_state:
        st.session_state.max_words = 150
    if 'speech_speed' not in st.session_state:
        st.session_state.speech_speed = 1.15
        # st.session_state.speech_speed = 1.0

    # --- Barra Lateral (Sidebar) ---
    with st.sidebar:
        st.header("Configuración de Respuesta")
        st.session_state.max_words = st.slider(
            "Máximo de palabras en la respuesta:",
            min_value=20, max_value=800, value=st.session_state.max_words, step=10
        )
        st.session_state.speech_speed = st.slider(
            "Velocidad de reproducción del audio:",
            min_value=0.5, max_value=2.0, value=st.session_state.speech_speed, step=0.1
        )

        st.header("Gestión de Chat")
        if st.button("🗑️ Nueva Conversación", help="Inicia una conversación desde cero."):
            new_conversation()
            st.rerun()

        if st.session_state.messages:
            chat_json = json.dumps(st.session_state.messages, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Guardar Conversación",
                data=chat_json,
                file_name=f"conversacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Guarda la conversación actual en un archivo JSON."
            )

        uploaded_file = st.file_uploader(
            "📂 Cargar Conversación", type="json", help="Carga una conversación desde un archivo JSON."
        )
        if uploaded_file is not None:
            load_conversation(uploaded_file)
            st.rerun()

        st.markdown("---")
        st.header("Control de Voz")
        if st.button("▶️ Iniciar Conversación de Voz", type="primary"):
            voice_conversation_loop()

        st.markdown("---")

    # --- Contenedor Principal del Chat ---
    # Se muestra el historial de chat existente
    for message in st.session_state.messages:
        avatar = USER_ICON if message["role"] == "user" else ASSISTANT_ICON
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # --- Lógica de entrada de texto (CORREGIDA) ---
    # Se procesa la nueva entrada después de mostrar el historial
    if prompt := st.chat_input("¡Hola! Antonio. Dime cómo puedo ayudarte"):
        # 1. Añadir mensaje de usuario
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Generar respuesta
        with st.spinner("Pensando..."):
            response = generate_response(prompt, st.session_state.max_words)

        # 3. Añadir respuesta del asistente
        st.session_state.messages.append({"role": "assistant", "content": response})

        # 4. Reproducir el audio de la respuesta
        text_to_speech(response, st.session_state.speech_speed)

        # 5. Refrescar la UI para mostrar los nuevos mensajes
        st.rerun()

if __name__ == "__main__":
    main()

# --- Pie de Página ---
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: gray; font-size: small;">
       @jrclinux_app | Asistente Conversacional | Desarrollado para Ubuntu 24.10 | NVIDIA RTX 4060 | AMD Ryzen 7 7735HS | v. {APP_VERSION} <br> {APP_DATE} <br> {APP_AUTHOR} ®
    </div>
    """,
    unsafe_allow_html=True
)
