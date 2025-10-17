import os
import streamlit as st
import base64
from openai import OpenAI

# ------------------------- CONFIGURACIÓN GENERAL -------------------------
st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")

# ------------------------- ENCABEZADO VISUAL -------------------------
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color:#4A90E2;'>🔍 Análisis Visual con IA</h1>
        <p style='font-size:18px;'>Sube una imagen y deja que el modelo la describa, analice o responda tus preguntas </p>
    </div>
    <hr style='border:1px solid #ddd; margin-top:15px; margin-bottom:25px;'>
""", unsafe_allow_html=True)

# ------------------------- SELECTOR DE TEMA -------------------------
theme = st.radio("Elige un tema:", ["Claro", "Oscuro"], horizontal=True)
if theme == "Oscuro":
    st.markdown("""
        <style>
            body, .stApp {
                background-color: #121212;
                color: #f5f5f5;
            }
            .stTextInput>div>div>input, .stTextArea textarea {
                background-color: #1E1E1E !important;
                color: #f5f5f5 !important;
                border: 1px solid #333 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body, .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
        </style>
    """, unsafe_allow_html=True)

# ------------------------- FUNCIONES -------------------------
def encode_image(image_file):
    """Codifica la imagen a base64 para enviarla al modelo."""
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ------------------------- INTERFAZ PRINCIPAL -------------------------
st.subheader("🔑 Ingresa tu clave de API")
ke = st.text_input('Tu Clave OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY')

client = OpenAI(api_key=api_key) if api_key else None

uploaded_file = st.file_uploader("📁 Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("📷 Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.toggle("💬 Quiero preguntar algo específico sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area("Añade aquí tu pregunta o contexto:")

analyze_button = st.button("🚀 Analizar imagen", type="primary")

# ------------------------- PROCESAMIENTO -------------------------
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("🔎 Analizando la imagen... por favor espera ⏳"):
        base64_image = encode_image(uploaded_file)
        prompt_text = "Describe lo que ves en la imagen en español."

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            # ------------------------- TARJETA DE RESULTADO -------------------------
            st.markdown("<h3 style='color:#4A90E2;'>🧠 Resultado del análisis:</h3>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="
                    background-color: {'#1E1E1E' if theme=='🌙 Oscuro' else '#f7f9fc'};
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
                    font-size: 16px;
                    line-height: 1.6;
                    color: {'#f5f5f5' if theme=='🌙 Oscuro' else '#000000'};
                ">
                    {full_response}
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

else:
    if not uploaded_file and analyze_button:
        st.warning("⚠️ Por favor sube una imagen antes de analizar.")
    if not api_key:
        st.warning("🔑 Ingresa tu API key para continuar.")

