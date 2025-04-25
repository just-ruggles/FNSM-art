import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ---- Configuración de página ----
st.set_page_config(page_title='Tablero Inteligente', layout="centered")

# ---- Estilos personalizados ----
st.markdown("""
    <style>
    .title-style {
        color: red;
        font-size: 40px;
        text-align: center;
        font-weight: bold;
    }
    .subheader-style {
        color: blue;
        font-size: 20px;
        margin-top: 20px;
    }
    .styled-button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .styled-button:hover {
        background-color: #FF7777;
    }
    .canvas-box {
        border: 2px solid #DDD;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        padding: 10px;
        background-color: #fdfdfd;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Título ----
st.markdown("<h1 class='title-style'>Tablero Inteligente</h1>", unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.markdown("<div class='subheader-style'>Acerca de:</div>", unsafe_allow_html=True)
    st.markdown("<div class='subheader-style'>En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto</div>", unsafe_allow_html=True)
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

# ---- Subtítulo ----
st.markdown("<div class='subheader-style'>Dibuja el boceto en el panel y presiona el botón para analizarla</div>", unsafe_allow_html=True)

# ---- Canvas ----
stroke_color = "#000000" 
bg_color = '#FFFFFF'
drawing_mode = "freedraw"

st.markdown("<div class='canvas-box'>", unsafe_allow_html=True)
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)
st.markdown("</div>", unsafe_allow_html=True)

# ---- Clave API ----
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# ---- Botón estilizado ----
analyze_button = st.markdown("""
    <form action="" method="post">
        <button class="styled-button" name="analyze" type="submit">Analiza la imagen</button>
    </form>
""", unsafe_allow_html=True)

# Streamlit no detecta clicks en botones HTML directamente.
# Usamos workaround con checkbox oculto.
trigger = st.checkbox("Presiona aquí después del botón", value=False)

# ---- Procesamiento ----
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

if canvas_result.image_data is not None and api_key and trigger:

    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        if base64_image is None:
            st.error("No se pudo codificar la imagen.")
        else:
            prompt_text = "Describe in spanish briefly the image"
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )
                content = response.choices[0].message.content
                st.success("Resultado:")
                st.write(content)

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

elif not api_key:
    st.warning("Por favor ingresa tu API key.")
