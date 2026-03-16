import streamlit as st
import json
import os
import urllib.request
import urllib.parse
import re
from datetime import datetime

DATA_FILE = "usuarios_data.json"

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f)

# --- MOTOR DE BÚSQUEDA DINÁMICA DE VÍDEOS EN YOUTUBE ---
@st.cache_data
def obtener_video_youtube(ejercicio):
    query = urllib.parse.quote_plus(f"como hacer {ejercicio} tecnica correcta")
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        video_ids = re.findall(r'"videoId":"(.{11})"', html)
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        return None
    return None

def mostrar_ejercicio(nombre, series_reps):
    with st.expander(f"▶️ {nombre} | ⏱️ {series_reps}"):
        url_video = obtener_video_youtube(nombre)
        if url_video:
            st.video(url_video)
        else:
            st.warning("Vídeo cargando. Si no aparece, prueba a refrescar la app.")

# --- NUEVO GENERADOR DE RUTINAS DIVIDIDAS (SPLITS) ---
def generar_ejercicios_dia(dia, dias_totales, equipamiento):
    tiene_manc = "Mancuernas" in equipamiento
    tiene_banco = "Banco de musculación" in equipamiento
    tiene_est = "Estación Multifunción" in equipamiento
    
    # --- DICCIONARIO INTELIGENTE DE EJERCICIOS ---
    # Pecho
    press_plano = "Press de pecho con mancuernas en banco" if (tiene_manc and tiene_banco) else "Press de pecho en máquina" if tiene_est else "Flexiones de pecho normales"
    press_incl = "Press inclinado con mancuernas" if (tiene_manc and tiene_banco) else "Flexiones declinadas (pies encima de una silla)"
    aperturas = "Aperturas con mancuernas" if (tiene_manc and tiene_banco) else "Aperturas en máquina Peck Deck" if tiene_est else "Flexiones abiertas anchas"
    
    # Espalda
    remo_horiz = "Remo con mancuernas apoyado en banco" if (tiene_manc and tiene_banco) else "Remo a dos manos con mancuernas" if tiene_manc else "Remo invertido debajo de una mesa"
    jalon = "Jalón al pecho en máquina" if tiene_est else "Pullover con mancuerna" if tiene_manc else "Superman isométrico lumbar"
    
    # Hombro
    press_hombro = "Press militar con mancuernas" if tiene_manc else "Flexiones en pica"
    elev_lat = "Elevaciones laterales con mancuernas" if tiene_manc else "Elevaciones laterales con botellas"
    pajaros = "Pájaros para hombro posterior con mancuernas" if tiene_manc else "Plancha tocando hombros alternos"
    
    # Tríceps
    triceps_ext = "Press francés con mancuernas" if tiene_manc else "Flexiones diamante cerradas"
    triceps_aisl = "Extensión de tríceps en polea" if tiene_est else "Extensión copa con mancuerna tras nuca" if tiene_manc else "Fondos de tríceps en silla"
    
    # Bíceps
    biceps_curl = "Curl de bíceps alterno con mancuernas" if tiene_manc else "Curl de bíceps en polea" if tiene_est else "Curl de bíceps casero con mochila"
    biceps_mart = "Curl martillo con mancuernas" if tiene_manc else "Curl de bíceps isométrico con toalla"
    
    # Piernas
    sentadilla = "Sentadilla copa con mancuerna (Goblet Squat)" if tiene_manc else "Sentadilla libre profunda"
    bulgara = "Sentadilla búlgara con mancuernas" if tiene_manc else "Zancadas alternas"
    ext_cuad = "Extensiones de cuádriceps en máquina" if tiene_est else "Sissy squat casera sin peso"
    
    pmr = "Peso muerto rumano con mancuernas" if tiene_manc else "Puente de glúteo a una pierna"
    curl_fem = "Curl femoral en máquina" if tiene_est else "Hip thrust con mancuernas" if tiene_manc else "Curl femoral deslizante en suelo"
    gemelo1 = "Elevación de gemelos de pie con mancuernas" if tiene_manc else "Elevación de gemelos a una pierna"
    
    # Core
    core1 = "Plancha Abdominal isométrica"
    core2 = "Crunch abdominal en suelo"

    # --- ASIGNACIÓN DE GRUPOS MUSCULARES SEGÚN DÍAS ---
    if dias_totales == 3:
        # PUSH / PULL / LEGS (3 Días)
        if dia == 1:
            return "Empuje (Pecho, Hombros y Tríceps)",[("Pecho", press_plano), ("Pecho", press_incl), ("Hombro", press_hombro), ("Hombro", elev_lat), ("Tríceps", triceps_ext)]
        elif dia == 2:
            return "Tirón (Espalda y Bíceps)",[("Espalda", jalon), ("Espalda", remo_horiz), ("Hombro", pajaros), ("Bíceps", biceps_curl), ("Bíceps", biceps_mart)]
        else:
            return "Piernas y Core",[("Cuádriceps", sentadilla), ("Femorales", pmr), ("Cuádriceps", bulgara), ("Gemelos", gemelo1), ("Core", core1)]
            
    elif dias_totales in [4, 5]:
        # TORSO / PIERNA (4-5 Días)
        if dia == 1 or dia == 4:
            return "Torso A (Enfoque Pecho/Espalda)",[("Pecho", press_plano), ("Espalda", jalon), ("Hombro", elev_lat), ("Tríceps", triceps_aisl), ("Bíceps", biceps_curl)]
        elif dia == 2 or dia == 5:
            return "Pierna A (Enfoque Cuádriceps)",[("Cuádriceps", sentadilla), ("Cuádriceps", bulgara), ("Femorales", pmr), ("Gemelos", gemelo1), ("Core", core1)]
        elif dia == 3:
            return "Torso B (Enfoque Hombros/Brazos)",[("Hombro", press_hombro), ("Espalda", remo_horiz), ("Pecho", press_incl), ("Tríceps", triceps_ext), ("Bíceps", biceps_mart)]
        else:
            return "Pierna B (Enfoque Femorales)",[("Femorales", curl_fem), ("Cuádriceps", ext_cuad), ("Gemelos", gemelo1), ("Core", core2)]
            
    else:
        # PPL REPETIDO (6 Días)
        if dia in [1, 4]:
            return "Empuje (Pecho, Hombro, Tríceps)",[("Pecho", press_plano if dia==1 else press_incl), ("Pecho", aperturas), ("Hombro", press_hombro), ("Tríceps", triceps_ext)]
        elif dia in[2, 5]:
            return "Tirón (Espalda, Bíceps)",[("Espalda", jalon if dia==2 else remo_horiz), ("Espalda", remo_horiz if dia==2 else jalon), ("Hombro", pajaros), ("Bíceps", biceps_curl)]
        else:
            return "Piernas y Core",[("Cuádriceps", sentadilla), ("Femorales", pmr if dia==3 else curl_fem), ("Cuádriceps", bulgara), ("Gemelos", gemelo1), ("Core", core1)]

# --- LÓGICA DEL CHATBOT ---
def responder_chat(mensaje):
    msg = mensaje.lower()
    if any(word in msg for word in["agujetas", "dolor"]): return "Las agujetas son microrroturas normales. Hemos dividido tu rutina para que esos músculos descansen mínimo 48h. ¡Haz estiramientos y recupérate! 💪"
    elif any(word in msg for word in["proteína", "comida"]): return "Intenta consumir entre 1.6g y 2g por kilo de peso. Huevos, pollo, atún o proteína whey."
    elif any(word in msg for word in["creatina", "suplementos"]): return "Toma de 3 a 5 gramos de creatina al día para mejorar tu fuerza y recuperación."
    elif any(word in msg for word in["grasa", "barriga", "abdomen"]): return "⚠️ NO se puede perder grasa localizada. Para definir el abdomen, cumple tu déficit calórico y el cardio."
    else: return "¡Buena pregunta! Recuerda cumplir tus macros y ser constante. ¿En qué más te ayudo?"

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Mi Entrenador IA", page_icon="🏋️", layout="wide")
st.title("🏋️ Tu Entrenador Personal IA")

usuario_input = st.text_input("👤 Ingresa tu usuario para acceder:", placeholder="Ejemplo: Cristian MA")

if usuario_input:
    usuario = usuario_input.strip().lower()
    nombre_mostrar = usuario_input.strip().title()
    datos = cargar_datos()
    
    if usuario not in datos or st.sidebar.checkbox("⚙️ Configurar / Editar mi Plan"):
        if usuario not in datos:
            st.success(f"¡Bienvenido, {nombre_mostrar}! Vamos a configurar tu plan.")
            datos[usuario] = {"nombre_real": nombre_mostrar, "historial_peso":[], "fecha_inicio": str(datetime.now().date()), "fase": 1} 
            
        st.subheader("1. Tus Datos Físicos")
        col1, col2, col3 = st.columns(3)
        edad = col1.number_input("Edad", min_value=12, max_value=100, value=datos.get(usuario, {}).get("edad", 30))
        peso = col2.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=datos.get(usuario, {}).get("peso", 75.0))
        altura = col3.number_input("Altura (cm)", min_value=100, max_value=250, value=datos.get(usuario, {}).get("altura", 175))
        sexo = st.selectbox("Sexo",["Hombre", "Mujer"], index=0 if datos.get(usuario, {}).get("sexo", "Hombre") == "Hombre" else 1)
        
        st.subheader("2. Configuración")
        objetivo = st.selectbox("Objetivo",["Perder grasa", "Ganar masa muscular", "Mantenerse en forma"])
        dias_entreno = st.slider("Días de entrenamiento a la semana", 2, 6, 4)
        tiempo = st.selectbox("Duración de la sesión",["30-40 min", "45-60 min", "Más de 1 hora"])
        
        equipamiento_default =["Mancuernas", "Banco de musculación", "Estación Multifunción"]
        try: default_val = datos.get(usuario, {}).get("equipamiento", equipamiento_default)
        except: default_val = equipamiento_default

        st.write("**Material disponible en casa:**")
        equipamiento = st.multiselect("Selecciona tu equipamiento:",["Ninguno (Peso corporal)", "Mancuernas", "Banco de musculación", "Estación Multifunción", "Gomas elásticas", "Barra de dominadas"], default=default_val)
        
        if st.button("💾 Guardar y Generar Plan Dividido", use_container_width=True):
            datos[usuario].update({"nombre_real": nombre_mostrar, "edad": edad, "peso": peso, "altura": altura, "sexo": sexo, "objetivo": objetivo, "dias_entreno": dias_entreno, "tiempo": tiempo, "equipamiento": equipamiento})
            if not datos[usuario].get("historial_peso"): datos[usuario]["historial_peso"] = [peso]
            if "fecha_inicio" not in datos[usuario]: datos[usuario]["fecha_inicio"] = str(datetime.now().date()); datos[usuario]["fase"] = 1
            guardar_datos(datos)
            st.success("¡Plan Creado! Cierra este menú a la izquierda para verlo.")

    if usuario in datos and "objetivo" in datos[usuario]:
        perfil = datos[usuario]
        fecha_inicio = datetime.strptime(perfil.get("fecha_inicio", str(datetime.now().date())), "%Y-%m-%d").date()
        dias_pasados = (datetime.now().date() - fecha_inicio).days
        fase_actual = perfil.get("fase", 1)
        dias_restantes = 28 - dias_pasados
        
        if dias_pasados >= 28:
            if st.button("🔄 Evolucionar a la Siguiente Fase", use_container_width=True):
                datos[usuario]["fase"] = fase_actual + 1
                datos[usuario]["fecha_inicio"] = str(datetime.now().date())
                guardar_datos(datos)
                st.rerun()

        st.markdown(f"### 👋 Hola, {perfil['nombre_real']} | 🔥 **Fase de Entrenamiento {fase_actual}**")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🏋️‍♂️ Entrenamiento", "🥗 Nutrición", "📈 Mi Progreso", "💬 Entrenador IA"])
        
        with tab1:
            st.markdown(f"**Tu material:** {', '.join(perfil['equipamiento'])}")
            st.divider()
            
            estilo = fase_actual % 3
            if estilo == 1: enfoque, reps_base, reps_grandes = "Hipertrofia Clásica", "3 series x 10-12 reps", "4 series x 8-12 reps"
            elif estilo == 2: enfoque, reps_base, reps_grandes = "Fuerza y Tensión", "4 series x 8 reps", "5 series x 6-8 reps"
            else: enfoque, reps_base, reps_grandes = "Estrés Metabólico", "3 series x 15-20 reps", "4 series x 15 reps"

            st.info(f"🧠 **Foco de este mes:** {enfoque}")
            
            if perfil["objetivo"] == "Perder grasa": tipo_cardio, tiempo_cardio = "rutina cardio HIIT intenso en casa", "15 minutos intensos"
            elif perfil["objetivo"] == "Ganar masa muscular": tipo_cardio, tiempo_cardio = "rutina cardio suave en casa low intensity", "10 minutos (salud cardiovascular)"
            else: tipo_cardio, tiempo_cardio = "rutina cardio moderado en casa de pie", "15 minutos intensidad media"

            # Renderizado de la Rutina Integral y Dinámica
            for dia in range(1, perfil["dias_entreno"] + 1):
                titulo_dia, ejercicios_hoy = generar_ejercicios_dia(dia, perfil["dias_entreno"], perfil["equipamiento"])
                
                with st.expander(f"📅 Día {dia} - {titulo_dia}", expanded=False):
                    st.markdown("### 🔥 FASE 1: Calentamiento")
                    mostrar_ejercicio("rutina calentamiento dinámico movilidad articular", "5 minutos antes de empezar")
                    
                    st.markdown("### 💪 FASE 2: Bloque de Fuerza")
                    for grupo_muscular, nombre_ejercicio in ejercicios_hoy:
                        reps = reps_grandes if grupo_muscular in["Pecho", "Espalda", "Cuádriceps", "Femorales"] else reps_base
                        mostrar_ejercicio(f"[{grupo_muscular}] {nombre_ejercicio}", reps)
                            
                    st.markdown("### 🏃‍♂️ FASE 3: Cardio y Estiramientos")
                    mostrar_ejercicio(tipo_cardio, tiempo_cardio)
                    mostrar_ejercicio("rutina estiramientos completos vuelta a la calma", "5 minutos para finalizar")

        with tab2:
            st.markdown(f"### 🍎 Tu Plan Nutricional Mensual")
            peso_actual = perfil["historial_peso"][-1] if perfil["historial_peso"] else perfil["peso"]
            
            if perfil["sexo"] == "Hombre": tmb = 88.362 + (13.397 * peso_actual) + (4.799 * perfil["altura"]) - (5.677 * perfil["edad"])
            else: tmb = 447.593 + (9.247 * peso_actual) + (3.098 * perfil["altura"]) - (4.330 * perfil["edad"])
                
            multiplicador = 1.2 if perfil["dias_entreno"] < 3 else 1.375 if perfil["dias_entreno"] <= 4 else 1.55
            calorias_mantenimiento = tmb * multiplicador
            
            if perfil["objetivo"] == "Perder grasa": calorias_meta, proteina = calorias_mantenimiento - 400, peso_actual * 2.0
            elif perfil["objetivo"] == "Ganar masa muscular": calorias_meta, proteina = calorias_mantenimiento + 300, peso_actual * 1.8
            else: calorias_meta, proteina = calorias_mantenimiento, peso_actual * 1.5
                
            col1, col2 = st.columns(2)
            col1.metric("🎯 Calorías Diarias", f"{int(calorias_meta)} kcal")
            col2.metric("🍗 Proteína Mínima", f"{int(proteina)} g")
            
            estilo_comida = fase_actual % 2
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.info("🍳 **Desayunos**")
                if estilo_comida == 1: st.write("• Tostadas con huevos y pavo.\n• Avena con leche y plátano.\n• Café y tortilla.")
                else: st.write("• Yogur griego con nueces y miel.\n• Revuelto de claras con espinacas.\n• Batido de proteínas.")
            with c2: 
                st.success("🥗 **Comidas**")
                if estilo_comida == 1: st.write("• 150g pollo + 80g arroz + ensalada.\n• Lentejas con verduras y pavo.\n• Pasta integral.")
                else: st.write("• Ternera magra con patata asada.\n• Garbanzos con pollo desmenuzado.\n• Ensalada de quinoa y atún.")
            with c3: 
                st.warning("🍽️ **Cenas**")
                if estilo_comida == 1: st.write("• Salmón al horno con patata.\n• Ensalada de atún y aguacate.\n• Pechuga plancha.")
                else: st.write("• Merluza a la plancha.\n• Revuelto de setas y gambas.\n• Ensalada de tomate y queso.")

        with tab3:
            st.markdown("### 📈 Registro de Peso Corporal")
            col_peso1, col_peso2 = st.columns([1, 2])
            with col_peso1:
                nuevo_peso = st.number_input("Peso de hoy (kg)", value=float(perfil["historial_peso"][-1] if perfil["historial_peso"] else perfil["peso"]))
                if st.button("Guardar mi peso actual", use_container_width=True):
                    datos[usuario]["historial_peso"].append(nuevo_peso)
                    guardar_datos(datos)
                    st.success("¡Guardado! Tus calorías se han ajustado.")
                    st.rerun()
            with col_peso2:
                if len(perfil["historial_peso"]) > 1: st.line_chart(perfil["historial_peso"])
                else: st.info("Registra tu peso en distintos días para ver tu gráfica.")

        with tab4:
            st.markdown("### 💬 Chat con tu Entrenador IA")
            if "mensajes_chat" not in st.session_state:
                st.session_state.mensajes_chat =[{"rol": "entrenador", "texto": f"¡Hola {perfil['nombre_real']}! Soy tu entrenador. ¿En qué te ayudo hoy?"}]

            for msg in st.session_state.mensajes_chat:
                if msg["rol"] == "usuario": st.chat_message("user", avatar="👤").write(msg["texto"])
                else: st.chat_message("assistant", avatar="🤖").write(msg["texto"])

            prompt = st.chat_input("Escribe tu pregunta aquí...")
            if prompt:
                st.session_state.mensajes_chat.append({"rol": "usuario", "texto": prompt})
                st.chat_message("user", avatar="👤").write(prompt)
                respuesta_bot = responder_chat(prompt)
                st.session_state.mensajes_chat.append({"rol": "entrenador", "texto": respuesta_bot})
                st.chat_message("assistant", avatar="🤖").write(respuesta_bot)
