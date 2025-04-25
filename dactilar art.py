import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente')

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://pbs.twimg.com/media/F2sr38KWYAAj0bc.jpg:large");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título principal en rojo
st.markdown("<h1 style='color: red;'>Tablero Inteligente FNSM</h1>", unsafe_allow_html=True)

# Panel lateral
with st.sidebar:
    # Subheaders en azul
    st.markdown("<h3 style='color: blue;'>Acerca de:</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto, mucho más que números.</h3>", unsafe_allow_html=True)

# Subtítulo principal
st.markdown("<h3 style='color: blue;'>Dibuja el boceto en el panel y presiona el botón para analizarl.</h3>", unsafe_allow_html=True)

# Parámetros del canvas
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

# Componente de dibujo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color de relleno con opacidad
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Entrada de clave API
ke = st.text_input('Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente OpenAI
client = OpenAI(api_key=api_key)

# Botón para análisis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Procesamiento de la imagen
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe in spanish briefly the image"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()
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

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
