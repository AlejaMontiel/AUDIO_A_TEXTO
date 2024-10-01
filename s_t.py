import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Estilo CSS para mejorar la apariencia
st.markdown("""
<style>
    .title {
        text-align: center;
        color: #1E88E5;
        font-size: 48px;
        font-family: 'Arial', sans-serif;
        margin: 20px 0;
    }
    .subheader {
        text-align: center;
        color: #1565C0;
        font-size: 24px;
        font-family: 'Arial', sans-serif;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f5;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .fable {
        border: 2px solid #1E88E5;
        border-radius: 10px;
        padding: 15px;
        background-color: #e3f2fd;
        font-family: 'Georgia', serif;
        font-size: 18px;
        line-height: 1.5;
        margin: 20px 0;
    }
    .audio-section {
        border: 2px solid #1E88E5;
        border-radius: 10px;
        background-color: #e3f2fd;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }
    .button {
        background-color: #1E88E5;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        margin-top: 10px;
    }
    .button:hover {
        background-color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<h1 class='title'>TRADUCTOR</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>¡Escucho todo lo que quieres traducir!</h2>", unsafe_allow_html=True)

# Imagen de encabezado
image = Image.open('Trad.jpg')
st.image(image, width=300)

# Sidebar
with st.sidebar:
    st.subheader("Traductor")
    st.write("Presiona el botón, cuando escuches la señal, "
             "habla lo que quieres traducir. Luego selecciona "   
             "la configuración de lenguaje que necesites.")

# Instrucciones para el usuario
st.write("Haz clic en el botón y di lo que quieras traducir")

# Botón de reconocimiento de voz
stt_button = Button(label="Escuchar 🎤", width=300, height=50)

# Configuración de reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Captura del resultado del reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))

    # Crear directorio temporal si no existe
    os.makedirs("temp", exist_ok=True)

    st.title("Texto a Audio")
    translator = Translator()

    text = str(result.get("GET_TEXT"))
    
    # Selección de lenguaje de entrada
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Italiano"),
    )
    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Italiano": "it"
    }
    input_language = lang_map.get(in_lang)

    # Selección de lenguaje de salida
    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Italiano"),
    )
    output_language = lang_map.get(out_lang)

    # Selección de acento
    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canadá",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )
    tld_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    tld = tld_map.get(english_accent)

    # Función de traducción y conversión a audio
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[:20] if text else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto de salida")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"<h2>Tú audio:</h2>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"<h2>Texto de salida:</h2>", unsafe_allow_html=True)
            st.write(output_text)

    # Función para eliminar archivos temporales
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if mp3_files:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Archivo eliminado:", f)

    remove_files(7)

        
    


