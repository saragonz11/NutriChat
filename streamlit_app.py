import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Asistente Nutricional Gemini", page_icon="🍎")

# --- CONFIGURACIÓN DE API ---
# Es recomendable usar st.secrets para la API Key
GEMINI_API_KEY = "AIzaSyAQgAdKjO46CIMB3GT50Q-0XuirYXib22o"
genai.configure(api_key=GEMINI_API_KEY)

# --- SIDEBAR: USER PROFILE ---
with st.sidebar:
    st.header("👤 Perfil del Usuario")
    
    name = st.text_input("Nombre", value="Usuario")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Edad", min_value=1, max_value=120, value=25)
        height = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170)
    with col2:
        weight = st.number_input("Peso (kg)", min_value=10, max_value=300, value=70)
        trains = st.radio("¿Entrena?", ["Sí", "No"], index=0)

    goal = st.selectbox("Objetivo", ["Bajar de peso", "Mantener peso", "Ganar masa muscular"])
    
    training_type = st.text_input("Tipo de entrenamiento", placeholder="Ej: Pesas, Running...") if trains == "Sí" else "Sedentario"
    conditions = st.text_area("Condiciones especiales", placeholder="Ej: Vegano, celíaco...")

st.title("🍎 Asistente Nutricional (Gemini)")
st.info(f"Hola {name}, analicemos tu alimentación para tu objetivo de **{goal.lower()}**.")

# --- DYNAMIC SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""
Eres un asistente nutricional experto. 
Datos del usuario:
- Nombre: {name}
- Edad: {age} años
- Peso: {weight} kg | Altura: {height} cm
- Objetivo: {goal}
- Actividad: {trains} ({training_type})
- Restricciones: {conditions if conditions else "Ninguna"}

Instrucciones: Analiza las comidas del usuario, identifica faltantes nutricionales y sugiere 3 mejoras realistas basadas en su perfil.
"""

# --- CHAT LOGIC CON GEMINI ---
# Inicializamos el modelo con la instrucción del sistema
model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=SYSTEM_PROMPT
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Ej: Hoy desayuné un café y una arepa con queso..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Preparamos el historial para Gemini (formato: {'role': 'user'/'model', 'parts': [...]})
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        
        # Iniciamos chat con historial previo
        chat_session = model.start_chat(history=history)
        
        # Generar respuesta con streaming
        response_placeholder = st.empty()
        full_response = ""
        
        response_stream = chat_session.send_message(prompt, stream=True)
        
        for chunk in response_stream:
            full_response += chunk.text
            response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
    
    # Guardar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": full_response})