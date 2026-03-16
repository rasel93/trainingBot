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

# --- NUEVO MOTOR DE BÚSQUEDA DINÁMICA DE VÍDEOS ---
# Usamos @st.cache_data para que la app sea súper rápida y solo busque el vídeo 1 vez
@st.cache_data
def obtener_video_youtube(ejercicio):
    # La app hace una búsqueda oculta para encontrar el tutorial exacto
    query = urllib.parse.quote_plus(f"como hacer tecnica {ejercicio} gym")
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        # Nos hacemos pasar por un navegador para que YouTube no nos bloquee
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # Buscamos el ID del primer vídeo real que aparezca en los resultados
        video_ids = re.findall(r'"videoId":"(.{11})"', html)
        if video_ids:
            # Devolvemos el enlace del primer vídeo encontrado
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        return None
    return None

def mostrar_ejercicio(nombre, series_reps):
    with st.expander(f"▶️ {nombre} | ⏱️ {series_reps}"):
        url_video = obtener_video_youtube(nombre)
        if url_video:
            # Se reproduce dentro de tu App sin sacarte a YouTube
            st.video(url_video)
        else:
            st.warning("Vídeo cargando. Si no aparece, prueba a refrescar la app.")

# --- LÓGICA DEL CHATBOT FITNESS ---
def responder_chat(mensaje):
    msg = mensaje.lower()
    if any(word in msg for word in["agujetas", "dolor", "cansado", "cansancio"]):
        return "Las agujetas son microrroturas musculares normales por el esfuerzo. Descansa, mantente hidratado y si el dolor es muy fuerte, camina o haz estiramientos suaves. ¡Es tu cuerpo haciéndose más fuerte! 💪"
    elif any(word in msg for word in ["proteína", "proteina", "batido", "comida"]):
        return "La proteína es la 'pintura y ladrillos' de tus músculos. Intenta consumir entre 1.6g y 2g por kilo de tu peso corporal. Huevos, pechuga de pollo, atún, queso batido o proteína whey son excelentes opciones."
    elif any(word in msg for word in["creatina", "suplementos", "tomar"]):
        return "La creatina es el suplemento más estudiado y seguro del mundo. Toma de 3 a 5 gramos al día (incluso los días que no entrenas) para mejorar tu fuerza y recuperación muscular."
    elif any(word in msg for word in["grasa", "barriga", "abdomen", "adelgazar", "peso"]):
        return "⚠️ NO se puede perder grasa localizada. Hacer cientos de abdominales no te quitará la barriga. Para definir el abdomen, necesitas cumplir con las calorías diarias de déficit que te marco en tu pestaña de Nutrición."
    elif any(word in msg for word in["no tengo tiempo", "rápido", "pereza"]):
        return "¡No hay excusas! Es mejor hacer 20 minutos intensos que no hacer nada. La disciplina empieza cuando la motivación se acaba. Haz un circuito rápido de flexiones y sentadillas si vas con prisa. 🔥"
    else:
        return "¡Buena pregunta! Recuerda que lo principal es cumplir tus macros (proteína y calorías) y progresar subiendo pesos en tus entrenamientos. ¿Hay algo más de tu rutina en lo que pueda ayudarte hoy?"

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Mi Entrenador IA", page_icon="💪", layout="wide")
st.title("💪 Tu Entrenador Personal IA")

usuario_input = st.text_input("👤 Ingresa tu usuario para acceder:", placeholder="Ejemplo: Cristian MA")

if usuario_input:
    usuario = usuario_input.strip().lower()
    nombre_mostrar = usuario_input.strip().title()
    datos = cargar_datos()
    
    # --- CREACIÓN / CONFIGURACIÓN DE PERFIL ---
    if usuario not in datos or st.sidebar.checkbox("⚙️ Configurar / Editar mi Plan"):
        if usuario not in datos:
            st.success(f"¡Bienvenido, {nombre_mostrar}! Vamos a configurar tu plan por primera vez.")
            datos[usuario] = {
                "nombre_real": nombre_mostrar, 
                "historial_peso":[],
                "fecha_inicio": str(datetime.now().date()), 
                "fase": 1 
            } 
            
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
        try: 
            default_val = datos.get(usuario, {}).get("equipamiento", equipamiento_default)
        except: 
            default_val = equipamiento_default

        st.write("**Material disponible en casa:**")
        equipamiento = st.multiselect("Selecciona tu equipamiento:",["Ninguno (Peso corporal)", "Mancuernas", "Banco de musculación", "Estación Multifunción", "Gomas elásticas", "Barra de dominadas"], default=default_val)
        
        if st.button("💾 Guardar y Generar Plan", use_container_width=True):
            datos[usuario].update({
                "nombre_real": nombre_mostrar, "edad": edad, "peso": peso, 
                "altura": altura, "sexo": sexo, "objetivo": objetivo, 
                "dias_entreno": dias_entreno, "tiempo": tiempo, "equipamiento": equipamiento
            })
            if not datos[usuario].get("historial_peso"):
                datos[usuario]["historial_peso"] = [peso]
            if "fecha_inicio" not in datos[usuario]:
                datos[usuario]["fecha_inicio"] = str(datetime.now().date())
                datos[usuario]["fase"] = 1
            guardar_datos(datos)
            st.success("¡Guardado! Desmarca la casilla 'Configurar / Editar mi Plan' a la izquierda para ver tu App.")
            
        if usuario in datos:
            st.divider()
            if st.button("🛠️ MODO PRUEBA: Avanzar Fase Automáticamente"):
                datos[usuario]["fase"] = datos[usuario].get("fase", 1) + 1
                datos[usuario]["fecha_inicio"] = str(datetime.now().date())
                guardar_datos(datos)
                st.success(f"¡Has avanzado a la Fase {datos[usuario]['fase']}! Desmarca la edición para verlo.")

    # --- VISTA PRINCIPAL (MODO APP) ---
    if usuario in datos and "objetivo" in datos[usuario]:
        perfil = datos[usuario]
        
        fecha_inicio = datetime.strptime(perfil.get("fecha_inicio", str(datetime.now().date())), "%Y-%m-%d").date()
        dias_pasados = (datetime.now().date() - fecha_inicio).days
        fase_actual = perfil.get("fase", 1)
        dias_restantes = 28 - dias_pasados
        
        if dias_pasados >= 28:
            st.balloons()
            st.success("🎉 ¡ENHORABUENA! Has completado 4 semanas de este ciclo. Tu cuerpo necesita un nuevo estímulo.")
            if st.button("🔄 Evolucionar a la Siguiente Fase", use_container_width=True):
                datos[usuario]["fase"] = fase_actual + 1
                datos[usuario]["fecha_inicio"] = str(datetime.now().date())
                guardar_datos(datos)
                st.rerun()

        st.markdown(f"### 👋 Hola, {perfil['nombre_real']} | 🔥 **Fase de Entrenamiento {fase_actual}**")
        st.caption(f"Día {dias_pasados} de 28 en esta fase (Faltan {max(0, dias_restantes)} días para el cambio automático).")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🏋️‍♂️ Entrenamiento", "🥗 Nutrición", "📈 Mi Progreso", "💬 Entrenador IA"])
        
        with tab1:
            st.markdown(f"**Tu material:** {', '.join(perfil['equipamiento'])}")
            st.divider()
            
            estilo = fase_actual % 3
            if estilo == 1:
                enfoque, reps_base, reps_grandes = "Hipertrofia Clásica (Volumen)", "3 series x 10-12 reps", "4 series x 8-12 reps"
            elif estilo == 2:
                enfoque, reps_base, reps_grandes = "Fuerza y Tensión (Más peso en tus máquinas)", "4 series x 8 reps", "5 series x 6-8 reps"
            else:
                enfoque, reps_base, reps_grandes = "Estrés Metabólico (Quema grasa)", "3 series x 15-20 reps", "4 series x 15 reps"

            st.info(f"🧠 **Enfoque de este mesociclo:** {enfoque}")
            
            tiene_mancuernas = "Mancuernas" in perfil["equipamiento"]
            tiene_banco = "Banco de musculación" in perfil["equipamiento"]
            tiene_estacion = "Estación Multifunción" in perfil["equipamiento"]
            
            pecho = "Press de pecho con mancuernas en banco" if (tiene_mancuernas and tiene_banco) else "Aperturas en máquina Peck Deck" if tiene_estacion else "Flexiones de pecho en el suelo"
            espalda = "Jalón al pecho en máquina" if tiene_estacion else "Remo con mancuernas apoyado en banco" if (tiene_mancuernas and tiene_banco) else "Remo invertido en casa"
            pierna1 = "Sentadilla búlgara con mancuernas" if tiene_mancuernas else "Sentadilla libre"
            pierna2 = "Extensiones de cuádriceps en máquina" if tiene_estacion else "Zancadas alternas"
            hombro = "Press militar con mancuernas sentado" if (tiene_mancuernas and tiene_banco) else "Elevaciones laterales con mancuernas" if tiene_mancuernas else "Flexiones en pica"
            brazo = "Curl de bíceps y Tríceps en polea" if tiene_estacion else "Curl con mancuernas y Press francés" if (tiene_mancuernas and tiene_banco) else "Fondos en silla y flexiones diamante"
            peso_muerto, gemelo, plancha = "Peso Muerto Rumano con mancuernas", "Elevación de gemelos de pie", "Plancha Abdominal isométrica"

            if perfil["dias_entreno"] <= 3:
                for dia in range(1, perfil["dias_entreno"] + 1):
                    st.subheader(f"📅 Día {dia} - Cuerpo Completo")
                    mostrar_ejercicio(pecho, reps_base)
                    mostrar_ejercicio(espalda, reps_base)
                    mostrar_ejercicio(pierna1, reps_grandes)
                    mostrar_ejercicio(hombro, reps_base)
                    mostrar_ejercicio(brazo, reps_base)
            else:
                for dia in range(1, perfil["dias_entreno"] + 1):
                    es_torso = (dia % 2 != 0)
                    st.subheader(f"📅 Día {dia} - {'Torso' if es_torso else 'Pierna y Core'}")
                    if es_torso:
                        mostrar_ejercicio(pecho, reps_grandes)
                        mostrar_ejercicio(espalda, reps_grandes)
                        mostrar_ejercicio(hombro, reps_base)
                        mostrar_ejercicio(brazo, reps_base)
                    else:
                        mostrar_ejercicio(pierna1, reps_grandes)
                        mostrar_ejercicio(pierna2, reps_base)
                        mostrar_ejercicio(peso_muerto, reps_base)
                        mostrar_ejercicio(gemelo, "4 series al fallo")
                        mostrar_ejercicio(plancha, "3 series de 45 seg")

        with tab2:
            st.markdown(f"### 🍎 Tu Plan Nutricional Mensual")
            peso_actual = perfil["historial_peso"][-1] if perfil["historial_peso"] else perfil["peso"]
            
            if perfil["sexo"] == "Hombre": 
                tmb = 88.362 + (13.397 * peso_actual) + (4.799 * perfil["altura"]) - (5.677 * perfil["edad"])
            else: 
                tmb = 447.593 + (9.247 * peso_actual) + (3.098 * perfil["altura"]) - (4.330 * perfil["edad"])
                
            multiplicador = 1.2 if perfil["dias_entreno"] < 3 else 1.375 if perfil["dias_entreno"] <= 4 else 1.55
            calorias_mantenimiento = tmb * multiplicador
            
            if perfil["objetivo"] == "Perder grasa": 
                calorias_meta, proteina = calorias_mantenimiento - 400, peso_actual * 2.0
            elif perfil["objetivo"] == "Ganar masa muscular": 
                calorias_meta, proteina = calorias_mantenimiento + 300, peso_actual * 1.8
            else: 
                calorias_meta, proteina = calorias_mantenimiento, peso_actual * 1.5
                
            col1, col2 = st.columns(2)
            col1.metric("🎯 Calorías Diarias", f"{int(calorias_meta)} kcal")
            col2.metric("🍗 Proteína Mínima", f"{int(proteina)} g")
            
            st.divider()
            
            estilo_comida = fase_actual % 2
            st.write("**Opciones de Menú Diario:** (Combina una de cada columna)")
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.info("🍳 **Desayunos**")
                if estilo_comida == 1: 
                    st.write("• Tostadas con 2 huevos y pavo.\n• Avena con leche y plátano.\n• Café y tortilla.")
                else: 
                    st.write("• Yogur griego con nueces y miel.\n• Revuelto de claras con espinacas.\n• Batido de proteínas.")
            with c2: 
                st.success("🥗 **Comidas**")
                if estilo_comida == 1: 
                    st.write("• 150g pollo + 80g arroz + ensalada.\n• Lentejas con verduras y pavo.\n• Pasta integral con carne magra.")
                else: 
                    st.write("• Ternera magra con patata asada.\n• Garbanzos con pollo desmenuzado.\n• Ensalada de quinoa y atún.")
            with c3: 
                st.warning("🍽️ **Cenas**")
                if estilo_comida == 1: 
                    st.write("• Salmón al horno con patata cocida.\n• Ensalada de atún y aguacate.\n• Pechuga a la plancha con brócoli.")
                else: 
                    st.write("• Merluza a la plancha con espárragos.\n• Revuelto de setas y gambas.\n• Ensalada de tomate y queso fresco.")

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
                if len(perfil["historial_peso"]) > 1: 
                    st.line_chart(perfil["historial_peso"])
                else: 
                    st.info("Registra tu peso en distintos días para visualizar tu progreso.")

        with tab4:
            st.markdown("### 💬 Chat con tu Entrenador IA")
            if "mensajes_chat" not in st.session_state:
                st.session_state.mensajes_chat = [{"rol": "entrenador", "texto": f"¡Hola {perfil['nombre_real']}! Soy tu entrenador. ¿En qué te ayudo hoy?"}]

            for msg in st.session_state.mensajes_chat:
                if msg["rol"] == "usuario": 
                    st.chat_message("user", avatar="👤").write(msg["texto"])
                else: 
                    st.chat_message("assistant", avatar="🤖").write(msg["texto"])

            prompt = st.chat_input("Escribe tu pregunta aquí...")
            if prompt:
                st.session_state.mensajes_chat.append({"rol": "usuario", "texto": prompt})
                st.chat_message("user", avatar="👤").write(prompt)
                respuesta_bot = responder_chat(prompt)
                st.session_state.mensajes_chat.append({"rol": "entrenador", "texto": respuesta_bot})
                st.chat_message("assistant", avatar="🤖").write(respuesta_bot)
