import streamlit as st
import json
import os
import urllib.parse

DATA_FILE = "usuarios_data.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f)

# Función para añadir enlaces de YouTube automáticamente a los ejercicios
def ej(nombre):
    # Crea una búsqueda directa en YouTube con la técnica del ejercicio
    busqueda = urllib.parse.quote_plus(f"como hacer técnica correcta {nombre}")
    url = f"https://www.youtube.com/results?search_query={busqueda}"
    return f"**{nombre}** [🎥 Video]({url})"

st.set_page_config(page_title="Mi Entrenador IA", page_icon="🏋️‍♂️", layout="wide")
st.title("🏋️‍♂️ Tu Entrenador Personal IA")
st.write("Seguimiento, nutrición y entrenamientos con tutoriales adaptados a TU casa.")

# --- OPTIMIZACIÓN DEL USUARIO ---
usuario_input = st.text_input("👤 Ingresa tu nombre de usuario para acceder:")

if usuario_input:
    # Limpiamos el texto: quitamos espacios sobrantes y pasamos a minúsculas
    usuario = usuario_input.strip().lower()
    # Guardamos una versión bonita para saludarle
    nombre_mostrar = usuario_input.strip().title()
    
    datos = cargar_datos()
    
    # --- CREACIÓN O EDICIÓN DE PERFIL ---
    if usuario not in datos or st.sidebar.checkbox("⚙️ Editar mi configuración"):
        if usuario not in datos:
            st.warning(f"Nuevo usuario detectado: {nombre_mostrar}. Vamos a crear tu perfil.")
            datos[usuario] = {"nombre_real": nombre_mostrar, "historial_peso":[]} 
            
        st.subheader("1. Tus Datos Físicos")
        col1, col2, col3 = st.columns(3)
        edad = col1.number_input("Edad", min_value=12, max_value=100, value=datos.get(usuario, {}).get("edad", 30))
        peso = col2.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=datos.get(usuario, {}).get("peso", 75.0))
        altura = col3.number_input("Altura (cm)", min_value=100, max_value=250, value=datos.get(usuario, {}).get("altura", 175))
        sexo = st.selectbox("Sexo",["Hombre", "Mujer"], index=0 if datos.get(usuario, {}).get("sexo", "Hombre") == "Hombre" else 1)
        
        st.subheader("2. Configuración del Entrenamiento")
        objetivo = st.selectbox("Objetivo principal",["Perder grasa", "Ganar masa muscular", "Mantenerse en forma"])
        dias_entreno = st.slider("¿Cuántos días a la semana quieres entrenar?", 2, 6, 4)
        tiempo = st.selectbox("¿Cuánto tiempo tienes por sesión?",["30-40 min", "45-60 min", "Más de 1 hora"])
        
        # Equipamiento en casa (Preseleccionado con tu material)
        st.write("¿Qué material tienes en casa?")
        equipamiento_default =["Mancuernas", "Banco de musculación", "Estación Multifunción"]
        
        # Evitar error de selección si hay datos previos guardados
        try:
            default_val = datos.get(usuario, {}).get("equipamiento", equipamiento_default)
        except:
            default_val = equipamiento_default

        equipamiento = st.multiselect(
            "Selecciona tu equipamiento:",["Ninguno (Peso corporal)", "Mancuernas", "Banco de musculación", "Estación Multifunción", "Gomas elásticas", "Barra de dominadas"],
            default=default_val
        )
        
        if st.button("Guardar Perfil y Generar Plan"):
            datos[usuario].update({
                "nombre_real": nombre_mostrar, "edad": edad, "peso": peso, 
                "altura": altura, "sexo": sexo, "objetivo": objetivo, 
                "dias_entreno": dias_entreno, "tiempo": tiempo, "equipamiento": equipamiento
            })
            if not datos[usuario].get("historial_peso"):
                datos[usuario]["historial_peso"] = [peso]
            guardar_datos(datos)
            st.success("¡Plan generado! Desmarca 'Editar mi configuración' para ver tu plan.")
            
    # --- VISTA DEL PERFIL ---
    if usuario in datos and "objetivo" in datos[usuario]:
        perfil = datos[usuario]
        st.success(f"¡Hola de nuevo, {perfil.get('nombre_real', nombre_mostrar)}!")
        
        tab1, tab2, tab3 = st.tabs(["💪 Entrenamientos y Vídeos", "🍎 Plan Semanal de Nutrición", "📈 Seguimiento"])
        
        with tab1:
            st.header("💪 Tu Rutina Semanal")
            st.write(f"**Frecuencia:** {perfil['dias_entreno']} días/semana | **Duración:** {perfil['tiempo']}")
            st.write(f"**Material:** {', '.join(perfil['equipamiento'])}")
            
            tiene_mancuernas = "Mancuernas" in perfil["equipamiento"]
            tiene_banco = "Banco de musculación" in perfil["equipamiento"]
            tiene_estacion = "Estación Multifunción" in perfil["equipamiento"]
            
            # --- SELECCIÓN INTELIGENTE DE EJERCICIOS (AHORA CON VÍDEOS) ---
            pecho = ej("Press de pecho con mancuernas en banco") if (tiene_mancuernas and tiene_banco) else ej("Aperturas en máquina Peck Deck") if tiene_estacion else ej("Flexiones de pecho en el suelo")
            espalda = ej("Jalón al pecho en máquina") if tiene_estacion else ej("Remo con mancuernas apoyado en banco") if (tiene_mancuernas and tiene_banco) else ej("Remo invertido en casa")
            pierna1 = ej("Sentadilla búlgara con mancuernas") if tiene_mancuernas else ej("Sentadilla libre")
            pierna2 = ej("Extensiones de cuádriceps en máquina") if tiene_estacion else ej("Zancadas alternas")
            hombro = ej("Press militar con mancuernas sentado") if (tiene_mancuernas and tiene_banco) else ej("Elevaciones laterales con mancuernas") if tiene_mancuernas else ej("Flexiones en pica")
            brazo = ej("Curl de bíceps y Extensiones de Tríceps en polea") if tiene_estacion else ej("Curl con mancuernas y Press francés") if (tiene_mancuernas and tiene_banco) else ej("Fondos en silla y flexiones diamante")
            peso_muerto = ej("Peso Muerto Rumano con mancuernas o polea")
            gemelo = ej("Elevación de gemelos de pie")
            plancha = ej("Plancha Abdominal isométrica")

            # Generar los días
            if perfil["dias_entreno"] <= 3:
                st.info("💡 **Distribución:** Rutina Full Body (Cuerpo Completo).")
                for dia in range(1, perfil["dias_entreno"] + 1):
                    with st.expander(f"Día {dia} - Full Body (Clic para ver ejercicios)"):
                        st.markdown(f"""
                        - {pecho} ➔ 3 series de 10-12 reps
                        - {espalda} ➔ 3 series de 10-12 reps
                        - {pierna1} ➔ 3 series de 12-15 reps
                        - {hombro} ➔ 3 series de 12 reps
                        - {brazo} ➔ 3 series de 12-15 reps
                        """)
            else:
                st.info("💡 **Distribución:** Rutina Torso / Pierna para máxima ganancia muscular.")
                for dia in range(1, perfil["dias_entreno"] + 1):
                    tipo = "Torso (Pecho, Espalda, Brazos)" if dia % 2 != 0 else "Pierna y Core"
                    with st.expander(f"Día {dia} - {tipo} (Clic para ver)"):
                        if tipo.startswith("Torso"):
                            st.markdown(f"""
                            - {pecho} ➔ 4 series de 8-12 reps
                            - {espalda} ➔ 4 series de 8-12 reps
                            - {hombro} ➔ 3 series de 10-15 reps
                            - {brazo} ➔ 4 series de 12-15 reps (Super-serie)
                            """)
                        else:
                            st.markdown(f"""
                            - {pierna1} ➔ 4 series de 10-12 reps por pierna
                            - {pierna2} ➔ 4 series de 12-15 reps
                            - {peso_muerto} ➔ 3 series de 10 reps
                            - {gemelo} ➔ 4 series al fallo
                            - {plancha} ➔ 3 series de 45 segundos
                            """)

        with tab2:
            st.header("🍎 Tu Plan Semanal de Nutrición")
            
            # Cálculo de calorías
            if perfil["sexo"] == "Hombre":
                tmb = 88.362 + (13.397 * perfil["peso"]) + (4.799 * perfil["altura"]) - (5.677 * perfil["edad"])
            else:
                tmb = 447.593 + (9.247 * perfil["peso"]) + (3.098 * perfil["altura"]) - (4.330 * perfil["edad"])
            
            multiplicador = 1.2 if perfil["dias_entreno"] < 3 else 1.375 if perfil["dias_entreno"] <= 4 else 1.55
            calorias_mantenimiento = tmb * multiplicador
            
            if perfil["objetivo"] == "Perder grasa":
                calorias_meta = calorias_mantenimiento - 400
                proteina = perfil["peso"] * 2.0
            elif perfil["objetivo"] == "Ganar masa muscular":
                calorias_meta = calorias_mantenimiento + 300
                proteina = perfil["peso"] * 1.8
            else:
                calorias_meta = calorias_mantenimiento
                proteina = perfil["peso"] * 1.5
                
            st.metric(label="🎯 Tus Calorías Diarias Objetivo", value=f"{int(calorias_meta)} kcal")
            st.metric(label="🍗 Proteína Diaria Mínima", value=f"{int(proteina)} g")
            
            st.subheader("🗓️ Menú Semanal Modular")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("🍳 **Desayunos**")
                st.markdown("- Tostadas integrales con 2 huevos revueltos y pavo.\n- Porridge de avena con leche, proteína (o yogur griego) y plátano.\n- Café/Té y tortilla francesa con queso fresco.")
            with c2:
                st.markdown("🥗 **Comidas**")
                st.markdown("- 150g pollo + 80g arroz (en seco) + ensalada.\n- Lentejas con verduras y trozos de pavo/pollo.\n- Pasta integral con carne picada magra y tomate natural.")
            with c3:
                st.markdown("🍽️ **Cenas**")
                st.markdown("- Filete de salmón o merluza al horno con patata cocida.\n- Ensalada completa con atún, huevo cocido y aguacate.\n- Pechuga a la plancha con brócoli al vapor.")

        with tab3:
            st.header("📈 Seguimiento Realista")
            nuevo_peso = st.number_input("Registrar peso actual (kg)", value=float(perfil["peso"]))
            if st.button("Actualizar Peso"):
                datos[usuario]["peso"] = nuevo_peso
                datos[usuario]["historial_peso"].append(nuevo_peso)
                guardar_datos(datos)
                st.success("¡Peso guardado! La app ajustará las calorías la próxima vez.")
                
            if len(perfil["historial_peso"]) > 1:
                st.line_chart(perfil["historial_peso"])
            else:
                st.info("Registra más pesos en semanas diferentes para ver tu gráfica de evolución.")
