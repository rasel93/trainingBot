import streamlit as st
import json
import os

# Archivo para guardar los datos de los usuarios (Base de datos gratuita)
DATA_FILE = "usuarios_data.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f)

st.set_page_config(page_title="Mi Entrenador IA", page_icon="🏋️‍♂️")
st.title("🏋️‍♂️ Tu Entrenador Personal IA")
st.write("Entrenamientos en casa y nutrición realista. Sin excusas.")

# Sistema de Login sencillo
usuario = st.text_input("Ingresa tu nombre de usuario para acceder a tu perfil:")

if usuario:
    datos = cargar_datos()
    
    # Registro de nuevo usuario
    if usuario not in datos:
        st.warning("Nuevo usuario detectado. Vamos a crear tu perfil.")
        edad = st.number_input("Edad", min_value=12, max_value=100, value=25)
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
        altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
        sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
        objetivo = st.selectbox("Objetivo",["Perder grasa", "Ganar masa muscular", "Mantenerse en forma"])
        nivel = st.selectbox("Nivel de experiencia", ["Principiante", "Intermedio", "Avanzado"])
        
        if st.button("Guardar Mi Perfil"):
            datos[usuario] = {
                "edad": edad, "peso": peso, "altura": altura, 
                "sexo": sexo, "objetivo": objetivo, "nivel": nivel,
                "historial_peso": [peso]
            }
            guardar_datos(datos)
            st.success("¡Perfil creado! Recarga la página o presiona Enter en el nombre para entrar.")
            
    # Perfil existente
    else:
        st.success(f"¡Hola de nuevo, {usuario}!")
        perfil = datos[usuario]
        
        # --- CÁLCULO DE NUTRICIÓN REALISTA ---
        # Fórmula de Harris-Benedict
        if perfil["sexo"] == "Hombre":
            tmb = 88.362 + (13.397 * perfil["peso"]) + (4.799 * perfil["altura"]) - (5.677 * perfil["edad"])
        else:
            tmb = 447.593 + (9.247 * perfil["peso"]) + (3.098 * perfil["altura"]) - (4.330 * perfil["edad"])
        
        calorias_mantenimiento = tmb * 1.375 # Multiplicador de actividad ligera
        
        if perfil["objetivo"] == "Perder grasa":
            calorias_meta = calorias_mantenimiento - 400
            proteina = perfil["peso"] * 2.0
        elif perfil["objetivo"] == "Ganar masa muscular":
            calorias_meta = calorias_mantenimiento + 300
            proteina = perfil["peso"] * 1.8
        else:
            calorias_meta = calorias_mantenimiento
            proteina = perfil["peso"] * 1.5
            
        st.header("🍎 Tu Plan de Nutrición")
        st.metric(label="Calorías Diarias Objetivo", value=f"{int(calorias_meta)} kcal")
        st.metric(label="Proteína Diaria (Importante)", value=f"{int(proteina)} g")
        st.info("💡 **Tip realista:** No elimines carbohidratos, solo cumple con tus calorías. Basa el 80% de tu dieta en comida real (huevos, pollo, legumbres, arroz, fruta).")
        
        # --- PLAN DE ENTRENAMIENTO EN CASA ---
        st.header("💪 Tu Rutina en Casa (Sin Equipo)")
        
        if perfil["nivel"] == "Principiante":
            st.write("🟢 **Circuito (3 Rondas) - 30 seg trabajo / 30 seg descanso:**")
            st.markdown("- Flexiones apoyando las rodillas\n- Sentadillas libres\n- Puente de glúteo en el suelo\n- Plancha isométrica apoyando codos\n- Jumping Jacks")
        elif perfil["nivel"] == "Intermedio":
            st.write("🟡 **Circuito (4 Rondas) - 40 seg trabajo / 20 seg descanso:**")
            st.markdown("- Flexiones normales\n- Zancadas (Lunges) alternas\n- Fondos de tríceps apoyado en una silla\n- Plancha tocando hombros\n- Burpees (sin salto)")
        else:
            st.write("🔴 **Circuito (5 Rondas) - 45 seg trabajo / 15 seg descanso:**")
            st.markdown("- Flexiones declinadas (pies encima de una silla)\n- Sentadillas con salto\n- Flexiones diamante (manos juntas)\n- Plancha dinámica (subir y bajar de codos a manos)\n- Burpees completos con salto")
            
        st.write("---")
        # --- SEGUIMIENTO REALISTA ---
        st.subheader("📈 Tu Seguimiento")
        nuevo_peso = st.number_input("Registrar mi peso actual (kg)", value=float(perfil["peso"]))
        if st.button("Actualizar Peso"):
            datos[usuario]["peso"] = nuevo_peso
            datos[usuario]["historial_peso"].append(nuevo_peso)
            guardar_datos(datos)
            st.success("¡Peso actualizado! Tus calorías y rutinas se han recalculado automáticamente.")