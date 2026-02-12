import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import gspread
from google.oauth2.service_account import Credentials


# --- Configuración de la Página ---
st.set_page_config(
    page_title="Orientación Vocacional",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 ISTE ")
st.header("Sistema de Orientación Vocacional")

# --- Estilos CSS Personalizados ---
# Ya eliminado por solicitud del usuario, pero se mantiene la estructura limpia

st.markdown("""Completa los datos y los 3 tests para obtener tu orientación.\n\nAquí no vas a encontrar profesiones sino actividades. """)

# --- Inicialización del Estado ---
if 'student_data' not in st.session_state:
    st.session_state.student_data = {}
if 'test1_scores' not in st.session_state:
    st.session_state.test1_scores = {}
if 'test2_scores' not in st.session_state:
    st.session_state.test2_scores = {}
if 'test3_scores' not in st.session_state:
    st.session_state.test3_scores = {}
if 'results_sent' not in st.session_state:
    st.session_state.results_sent = False

# --- Función Generar PDF ---


# --- Definición de Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 Datos del Estudiante 🔜", 
    "🧠 Test 1 (Intereses) 🔜", 
    "❤️ Test 2 (Canihuante) 🔜", 
    "📊 Test 3 (Hereford) 🔜", 
    "✅ Finalizar"
])

# ... (El código de los tabs 1, 2, 3 y 4 permanece igual, solo cambiamos el imports y definition arriba) ...
# Para aplicar el cambio correctamente sin borrar todo, usaré multi-replace o aplicaré tab por tab si es necesario,
# pero como estoy usando replace_file_content en un bloque grande, asumiré que el contexto intermedio no cambia.
# ERROR POTENCIAL: Estoy reemplazando todo desde imports hasta tab 1.

# --- Tab 5: Finalizar (Actualizado) ---
# ...


# --- Tab 1: Datos del Estudiante ---
with tab1:
    st.header("Datos Personales")
    # Eliminamos st.form para permitir interactividad dinámica
    st.write("Por favor ingresa tus datos:")
    
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", min_value=10, max_value=100, step=1)
    celular = st.text_input("Número de Celular")
    
    COLEGIOS = [
        "UE Ambato", "UE Luis A. Martínez", "UE Rumiñahui", "UE González Suarez", 
        "UE San Alfonso", "UE Sagrada Familia", "Centro Escolar Andino", "UE Suizo", 
        "UE Adventista", "UE Ricardo Descalzzi", "UE Rodríguez Albornoz", "UE Génesis", 
        "UE Las Américas", "UE Juan B. Vela", "UE Bautista", "UE Teresa Flor", 
        "UE Juan Montalvo", "UE Pedro Fermín Cevallos", "Grupos de Interés - ESE", "Otro"
    ]
    
    colegio_seleccion = st.selectbox("Selecciona tu Unidad Educativa", COLEGIOS)
    
    unidad_educativa = colegio_seleccion
    otro_colegio = None
    
    # Lógica condicional: Solo mostrar input si selecciona "Otro"
    if colegio_seleccion == "Otro":
        otro_colegio = st.text_input("Si seleccionaste 'Otro', escribe el nombre aquí:")
        if otro_colegio:
            unidad_educativa = otro_colegio
        else:
            unidad_educativa = None # Para validación posterior

    if st.button("Guardar Datos"):
        # Validación
        if colegio_seleccion == "Otro" and not otro_colegio:
            st.error("⚠️ Por favor especifica el nombre de tu Unidad Educativa.")
        elif nombre and edad and celular and unidad_educativa:
            st.session_state.student_data = {
                "Nombre": nombre,
                "Edad": edad,
                "Celular": celular,
                "Unidad Educativa": unidad_educativa
            }
            st.success("✅ Datos guardados correctamente. Pasa al siguiente test.")
        else:
            st.error("⚠️ Por favor completa todos los campos.")
    
    st.caption("Esta encuesta cumple con el requerimiento de protección de datos personales.")



# --- Tab 2: Test 1 (Intereses) ---
with tab2:
    st.header("Test de Identificación de Intereses y Profesionales")
    st.write("""
    **Instrucciones:**
    *   Lee atentamente cada una de las actividades.
    *   Puedes señalar una o varias opciones.
    *   Marca la opción únicamente si la actividad te llama la atención. Si no te interesa, déjala vacía.
    *   En general no existen respuestas correctas o incorrectas; lo importante es que contestes con sinceridad y confianza para que puedas conocer mejor tus intereses vocacionales.
    """)
    
    # Definición de Áreas y sus Preguntas (IDs)
    AREAS_TEST1 = {
        "AREA_I": {
            "nombre": "Arte y Creatividad",
            "ids": [4, 9, 12, 20, 28, 31, 35, 39, 43, 46, 50, 65, 67, 68, 75, 77]
        },
        "AREA_II": {
            "nombre": "Ciencias Sociales",
            "ids": [6, 13, 23, 25, 34, 37, 38, 42, 49, 52, 55, 63, 66, 70, 72, 78]
        },
        "AREA_III": {
            "nombre": "Económica, Administrativa y Financiera",
            "ids": [5, 10, 15, 19, 21, 26, 29, 33, 36, 44, 53, 56, 59, 62, 71, 80]
        },
        "AREA_IV": {
            "nombre": "Ciencia y Tecnología",
            "ids": [1, 7, 11, 17, 18, 24, 30, 41, 48, 51, 58, 60, 61, 64, 73, 79]
        },
        "AREA_V": {
            "nombre": "Ciencias Ecológicas, Biológicas y de Salud",
            "ids": [2, 3, 8, 14, 16, 22, 27, 32, 40, 45, 47, 54, 57, 69, 74, 76]
        }
    }

    # Texto de las 80 Preguntas
    QUESTIONS_TEXT = {
        1: "Diseñar programas de computación y explorar nuevas aplicaciones tecnológicas para uso del internet.",
        2: "Criar, cuidar y tratar animales domésticos y de campo.",
        3: "Investigar sobre áreas verdes, medio ambiente y cambios climáticos.",
        4: "Ilustrar, dibujar y animar digitalmente.",
        5: "Seleccionar, capacitar y motivar al personal de una organización/empresa.",
        6: "Realizar excavaciones para descubrir restos del pasado.",
        7: "Resolver problemas de cálculo para construir un puente.",
        8: "Diseñar cursos para enseñar a la gente sobre temas de salud e higiene.",
        9: "Tocar un instrumento y componer música.",
        10: "Planificar cuáles son las metas de una organización pública o privada a mediano y largo plazo.",
        11: "Diseñar y planificar la producción masiva de artículos como muebles, autos, equipos de oficina, empaques y envases para alimentos y otros.",
        12: "Diseñar logotipos y portadas de una revista.",
        13: "Organizar eventos y atender a sus asistentes.",
        14: "Atender la salud de personas enfermas.",
        15: "Controlar ingresos y egresos de fondos y presentar el balance final de una institución.",
        16: "Hacer experimentos con plantas (frutas, árboles, flores).",
        17: "Concebir planos para viviendas, edificios y ciudadelas.",
        18: "Investigar y probar nuevos productos farmacéuticos.",
        19: "Hacer propuestas y formular estrategias para aprovechar las relaciones económicas entre dos partes.",
        20: "Pintar, hacer esculturas, ilustrar libros de arte, etcétera.",
        21: "Elaborar campañas para introducir un nuevo producto al mercado.",
        22: "Examinar y tratar los problemas visuales.",
        23: "Defender a clientes individuales o empresas en juicios de diferente naturaleza.",
        24: "Diseñar máquinas que puedan simular actividades humanas.",
        25: "Investigar las causas y efectos de los trastornos emocionales.",
        26: "Supervisar las ventas de un centro comercial.",
        27: "Atender y realizar ejercicios a personas que tienen limitaciones físicas, problemas de lenguaje, etcétera.",
        28: "Prepararse para ser modelo profesional.",
        29: "Aconsejar a las personas sobre planes de ahorro e inversiones.",
        30: "Elaborar mapas, planos e imágenes para el estudio y análisis de datos geográficos.",
        31: "Diseñar juegos interactivos electrónicos para computadora.",
        32: "Realizar el control de calidad de los alimentos.",
        33: "Tener un negocio propio de tipo comercial.",
        34: "Escribir artículos periodísticos, cuentos, novelas y otros.",
        35: "Redactar guiones y libretos para un programa de televisión.",
        36: "Organizar un plan de distribución y venta de un gran almacén.",
        37: "Estudiar la diversidad cultural en el ámbito rural y urbano.",
        38: "Gestionar y evaluar convenios internacionales de cooperación para el desarrollo social.",
        39: "Crear campañas publicitarias.",
        40: "Trabajar investigando la reproducción de peces, camarones y otros animales marinos.",
        41: "Dedicarse a fabricar productos alimenticios de consumo masivo.",
        42: "Gestionar y evaluar proyectos de desarrollo en una institución educativa y/o fundación.",
        43: "Rediseñar y decorar espacios físicos en viviendas, oficinas y locales comerciales.",
        44: "Administrar una empresa de turismo y/o agencias de viaje.",
        45: "Aplicar métodos alternativos a la medicina tradicional para atender personas con dolencias de diversa índole.",
        46: "Diseñar ropa para niños, jóvenes y adultos.",
        47: "Investigar organismos vivos para elaborar vacunas.",
        48: "Manejar y/o dar mantenimiento a dispositivos/aparatos tecnológicos en aviones, barcos, radares, etcétera.",
        49: "Estudiar idiomas extranjeros actuales y antiguos para hacer traducción.",
        50: "Restaurar piezas y obras de arte.",
        51: "Revisar y dar mantenimiento a artefactos eléctricos, electrónicos y computadoras.",
        52: "Enseñar a niños de 0 a 5 años.",
        53: "Investigar y/o sondear nuevos mercados.",
        54: "Atender la salud dental de las personas.",
        55: "Tratar a niños, jóvenes y adultos con problemas psicológicos.",
        56: "Crear estrategias de promoción y venta de nuevos productos ecuatorianos en el mercado internacional.",
        57: "Planificar y recomendar dietas para personas diabéticas y/o con sobrepeso.",
        58: "Trabajar en una empresa petrolera en un cargo técnico como control de la producción.",
        59: "Administrar una empresa (familiar, privada o pública).",
        60: "Tener un taller de reparación y mantenimiento de carros, tractores, etcétera.",
        61: "Ejecutar proyectos de extracción minera y metalúrgica.",
        62: "Asistir a directivos de multinacionales con manejo de varios idiomas.",
        63: "Diseñar programas educativos para niños con discapacidad.",
        64: "Aplicar conocimientos de estadística en investigaciones en diversas áreas (social, administrativa, salud, etcétera).",
        65: "Fotografiar hechos históricos, lugares significativos, rostros, paisajes para el área publicitaria, artística, periodística y social.",
        66: "Trabajar en museos y bibliotecas nacionales e internacionales.",
        67: "Ser parte de un grupo de teatro.",
        68: "Producir cortometrajes, spots publicitarios, programas educativos, de ficción, etcétera.",
        69: "Estudiar la influencia entre las corrientes marinas y el clima y sus consecuencias ecológicas.",
        70: "Conocer las distintas religiones, su filosofía y transmitirlas a la comunidad en general.",
        71: "Asesorar a inversionistas en la compra de bienes/acciones en mercados nacionales e internacionales.",
        72: "Estudiar grupos étnicos, sus costumbres, tradiciones, cultura y compartir sus vivencias.",
        73: "Explorar el espacio sideral, los planetas, características y componentes.",
        74: "Mejorar la imagen facial y corporal de las personas aplicando diferentes técnicas.",
        75: "Decorar jardines de casas y parques públicos.",
        76: "Administrar y renovar menús de comidas en un hotel o restaurante.",
        77: "Trabajar como presentador de televisión, locutor de radio y televisión, animador de programas culturales y concursos.",
        78: "Diseñar y ejecutar programas de turismo.",
        79: "Administrar y ordenar (planificar) adecuadamente la ocupación del espacio físico de ciudades, países etc., utilizando imágenes de satélite, mapas.",
        80: "Organizar, planificar y administrar centros educativos."
    }
    
    scores_t1 = {area_data['nombre']: 0 for area_data in AREAS_TEST1.values()}
    
    # Mostrar preguntas en orden secuencial (1 al 80) para no revelar el área
    # Usamos una lista vertical simple para evitar problemas en móviles
    st.write("Selecciona las actividades que te llamen la atención:")
    
    # Contenedor Vertical
    for q_id in range(1, 81):
        q_text = QUESTIONS_TEXT.get(q_id, f"Pregunta {q_id}")
        
        # Checkbox directo
        if st.checkbox(f"**{q_id}.** {q_text}", key=f"t1_q{q_id}"):
            # Si se marca, buscamos a qué área pertenece y sumamos 1
            for area_key, area_data in AREAS_TEST1.items():
                if q_id in area_data['ids']:
                    scores_t1[area_data['nombre']] += 1
                    break

    st.session_state.test1_scores = scores_t1
    
    # Mostrar progreso (opcional, sin revelar áreas específicas todavía)
    total_marcadas = sum(scores_t1.values())
    st.progress(min(total_marcadas / 80.0, 1.0), text=f"Has seleccionado {total_marcadas} actividades.")

# --- Tab 3: Test 2 (Canihuante) ---
with tab3:
    st.header("Cuestionario de Intereses Vocacionales (Canihuante)")
    st.write("""
    **Instrucciones:**
    A continuación encontrarás un conjunto de actividades:
    *   Si te agrada realizar la actividad propuesta, marca la casilla correspondiente.
    *   Puedes señalar una o varias opciones.
    *   Si no te agrada o te es indiferente, deja la casilla vacía.
    *   Recuerda contestar con rapidez y sinceridad.
    """)
    
    # 10 categorías (A-J), 100 preguntas
    categories_t2 = list("ABCDEFGHIJ")
    scores_t2 = {cat: 0 for cat in categories_t2}
    
    QUESTIONS_TEXT_T2 = {
        1: "Tener un negocio propio",
        2: "Leer revistas técnicas",
        3: "Dibujar flores y frutas",
        4: "Pintar muebles",
        5: "Cuidar árboles frutales, regándolos y podándolos",
        6: "Escribir cuentos originales",
        7: "Hacer inventos científicos",
        8: "Arreglar peleas entre compañeros para restablecer la amistad",
        9: "Pasar materias a cuadernos en limpio",
        10: "Levantarse siempre temprano",
        11: "Vender objetos en un mostrador",
        12: "Arreglar desperfectos eléctricos en la casa",
        13: "Tocar algún instrumento musical",
        14: "Hacer mesas y bancos",
        15: "Cultivar plantas y flores",
        16: "Escribir artículos en un diario mural",
        17: "Leer revistas sobre adelantados de la ciencia",
        18: "Reclamar por alguna injusticia del profesor",
        19: "Escribir a máquina",
        20: "Andar vestido de uniforme militar",
        21: "Reunir dinero para el curso",
        22: "Trabajar en máquinas",
        23: "Cantar en una fiesta",
        24: "Arreglar puertas y ventanas",
        25: "Trabajar en la tierra con las manos",
        26: "Consultar libros y diccionarios",
        27: "Coleccionar insectos",
        28: "Enseñar algo a los demás compañeros",
        29: "Hacer largas sumas con rapidez",
        30: "Manejar armas de fuego",
        31: "Arrendar revistas a los compañeros",
        32: "Arreglar planchas eléctricas",
        33: "Dibujar casas y muebles",
        34: "Trabajar en algo que requiera fuerza",
        35: "Comprar aves y engordarlas para la venta",
        36: "Aprender poesías de memoria",
        37: "Descubrir cómo funcionan las maquinarias",
        38: "Cuidar el curso cuando no está el profesor",
        39: "Ser empleado de una tienda",
        40: "Manejar tanques",
        41: "Vender sándwiches en la escuela",
        42: "Manejar un taxi, micro o camión",
        43: "Trabajar en comedias",
        44: "Hacer trabajos manuales",
        45: "Dar alimentos a las aves",
        46: "Participar en concursos de poesías y cuentos",
        47: "Conocer bien el funcionamiento del cuerpo humano",
        48: "Ser jefe de curso",
        49: "Ordenar cuadernos y libros",
        50: "Manejar aviones",
        51: "Vender radios a domicilio",
        52: "Desarmar un motor de automóvil",
        53: "Pintar cuadros",
        54: "Afilar cuchillos, hachas y herramientas",
        55: "Manejar tractores, o maquinas de campo",
        56: "Trabajar en diario",
        57: "Conocer bien las enfermedades para poder curarlas",
        58: "Conocer centros deportivos",
        59: "Ser secretario de una empresa",
        60: "Participar en peleas violentas",
        61: "Ser tesorero de un club",
        62: "Tener un taller en casa",
        63: "Ser director de un programa radial",
        64: "Ayudar a un carpintero en su trabajo",
        65: "Administrar un fundo",
        66: "Hacer entrevistas a personajes importantes",
        67: "Hacer experimentos en el laboratorio",
        68: "Ser dirigente en una institución",
        69: "Redactar cartas comerciales",
        70: "Leer relatos sobre las guerras mundiales",
        71: "Tener una alcancía para reunir dinero",
        72: "Armar un radio",
        73: "Dibujar tapas de libros",
        74: "Hacer juguetes de madera",
        75: "Trabajar en un jardín o huerto",
        76: "Escribir un libro",
        77: "Estudiar la vida de los peces",
        78: "Ser presidente de un club",
        79: "Trabajar en una oficina",
        80: "Participar en desfiles militares",
        81: "Hacer volantines para venderlos",
        82: "Recibir y transmitir mensajes por radio",
        83: "Arreglar vitrinas comerciales",
        84: "Pintar y empapelar piezas",
        85: "Trabajar en el campo",
        86: "Defender un acusado ante el juez",
        87: "Estudiar los astros",
        88: "Aconsejar a amigos",
        89: "Atender publico en una oficina",
        90: "Mandar a un grupo de soldados",
        91: "Vender libros viejos para reunir dinero",
        92: "Soldar metales",
        93: "Llegar hacer un cómico radial",
        94: "Limpiar motores en una industria",
        95: "Tener una chacrita en su casa",
        96: "Decir un discurso en público",
        97: "Trabajar con un micrófono",
        98: "Organizar una fiesta en el curso",
        99: "Tener un trabajo con horario fijo",
        100: "Tener un trabajo con mucha disciplina"
    }

    # Layout vertical para móviles
    # Iteramos por las 100 preguntas
    for i in range(1, 101):
        q_text = QUESTIONS_TEXT_T2.get(i, f"Pregunta {i}")
        
        # Determinar Categoría (A-J) usando modulo
        # i=1 -> 0 -> A
        # i=2 -> 1 -> B
        # ...
        # i=10 -> 9 -> J
        cat_idx = (i - 1) % 10
        category = categories_t2[cat_idx]

        if st.checkbox(f"**{i}.** {q_text}", key=f"t2_q{i}"):
             scores_t2[category] += 1
    
    st.session_state.test2_scores = scores_t2
    
    st.divider()
    # st.subheader("Resultados Parciales Canihuante") # Opcional: Ocultar para no sugestionar
    # if any(scores_t2.values()):
    #     df_chart_t2 = pd.DataFrame(list(scores_t2.items()), columns=["Categoría", "Puntaje"])
    #     st.bar_chart(df_chart_t2.set_index("Categoría"))

# --- Tab 4: Test 3 (Hereford) ---
with tab4:
    st.header("Inventario de Intereses de Karl Hereford")
    st.write("""
    **Instrucciones:**
    Esta no es una prueba, sino solamente una medida de tu interés en algunos campos profesionales. No hay respuestas correctas, lo único importante es tu franca opinión.
    
    Para cada actividad, indica qué tanto te gusta o desagrada usando la siguiente escala del 1 al 5:
    *   **1:** Me desagrada mucho
    *   **2:** No me gusta
    *   **3:** Me es indiferente
    *   **4:** Me gusta
    *   **5:** Me gusta mucho
    """)
    
    # Categorías Oficiales Hereford (9)
    # Nota: El usuario proporcionó 9 categorías con listas específicas de IDs
    AREAS_TEST3 = {
        "Cálculo": [3, 11, 22, 32, 37, 48, 59, 64, 73, 88],
        "Científico Físico": [8, 14, 30, 39, 45, 53, 57, 68, 81, 84],
        "Científico Biológico": [5, 18, 24, 36, 40, 51, 61, 69, 76, 90],
        "Mecánico": [1, 16, 26, 34, 43, 46, 63, 66, 79, 82],
        "Servicio Social": [6, 13, 19, 21, 29, 49, 56, 71, 77, 86],
        "Literario": [9, 12, 25, 28, 42, 52, 62, 67, 78, 83],
        "Persuasivo": [2, 17, 27, 35, 38, 47, 55, 72, 75, 87],
        "Artístico": [7, 10, 20, 31, 44, 50, 58, 65, 80, 85],
        "Musical": [4, 15, 23, 33, 41, 54, 60, 70, 74, 89]
    }
    
    QUESTIONS_TEXT_T3 = {
        1: "Reparar una licuadora",
        2: "Participar en debates y argumentos",
        3: "Resolver rompecabezas numéricos",
        4: "Aprender a leer música",
        5: "Hacer análisis de sangre",
        6: "Visitar orfelinatos",
        7: "Pintar paisajes",
        8: "Tomar fotografías de las fases de un eclipse",
        9: "Escribir cuentos para una revista",
        10: "Recibir un juego de pinturas de óleo como regalo",
        11: "Ejecutar mecanizaciones aritméticas",
        12: "Ser escritor de novelas",
        13: "Participar en campañas contra la delincuencia juvenil",
        14: "Recibir un telescopio como regalo",
        15: "Saber distinguir y apreciar la buena música",
        16: "Manejar un torno o taladro eléctrico",
        17: "Ayudar a los candidatos políticos",
        18: "Hacer colecciones de plantas",
        19: "Colaborar con otros para bien de ellos y de mí mismo",
        20: "Asistir a exposiciones de pintura",
        21: "Impartir conocimientos a aquellas personas que no los tienen",
        22: "Convertir radios a grados",
        23: "Tener discos de música clásica",
        24: "Aprender a practicar primeros auxilios",
        25: "Leer a los clásicos",
        26: "Hacer dibujos de máquinas",
        27: "Hacer campañas estadísticas",
        28: "Saber distinguir y apreciar la buena literatura",
        29: "Ayudar a encontrar empleo a personas de escasos recursos",
        30: "Informarme sobre la energía atómica",
        31: "Leer libros sobre arte",
        32: "Calcular el área de un cuarto para alfombrarse",
        33: "Escuchar los conciertos en las plazas públicas",
        34: "Instalar un contacto eléctrico",
        35: "Convencer a otros para que hagan lo que yo creo deben hacer",
        36: "Cuidar un pequeño acuario",
        37: "Usar una regla de cálculo",
        38: "Ser protagonista de artículos nuevos",
        39: "Hacer una colección de rocas",
        40: "Observar las costumbres de las abejas",
        41: "Obtener el autógrafo de un músico famoso",
        42: "Asistir a la biblioteca en una tarde libre",
        43: "Observar como el técnico repara la televisión",
        44: "Diseñar escenarios para representaciones teatrales",
        45: "Observar el movimiento aparente de las estrellas",
        46: "Soldar alambres o partes metálicas",
        47: "Defender un punto de vista de alguna persona",
        48: "Calcular porcentajes",
        49: "Servir como consejero en un club de niños",
        50: "Hacer mosaicos artísticos para decoraciones",
        51: "Asistir a una operación médica",
        52: "Participar en concursos literarios",
        53: "Estudiar el espectro luminoso de la luz",
        54: "Asistir a conciertos",
        55: "Ser 'líder' de un grupo",
        56: "Leer cuentos a los ciegos",
        57: "Visitar una exposición científica",
        58: "Hacer diseños para tapices",
        59: "Consultar tablas de logaritmos y raíces",
        60: "Estudiar la música de diferentes países como la India, el Japón, etc.",
        61: "Leer libros sobre el funcionamiento de los organismos vivos",
        62: "Corregir composiciones o artículos periodísticos",
        63: "Observar como los mecánicos hacen reparaciones de coches",
        64: "Ayudar a otras personas con problemas matemáticos",
        65: "Dibujar o delinear personas o cosas",
        66: "Desarmar y armar un reloj",
        67: "Escribir reseñas críticas de libros",
        68: "Estudiar los cambios del tiempo y sus causas",
        69: "Hacer colecciones de insectos",
        70: "Tomar parte en un conjunto coral",
        71: "Escuchar a otros con paciencia y comprender su punto de vista",
        72: "Organizar y dirigir festivales, excursiones o campañas sociales",
        73: "Ilustrar problemas geométricos con ayuda de las escuadras, la regla T y el compás",
        74: "Tocar un instrumento musical",
        75: "Dirigir un grupo o equipo en situaciones difíciles",
        76: "Cultivar plantas exóticas",
        77: "Visitar casas humildes para determinar lo que necesitan",
        78: "Escribir cartas narrativas a mis amigos o parientes",
        79: "Armar o componer muebles comunes",
        80: "Saber distinguir y apreciar las buenas pinturas",
        81: "Visitar un observatorio astronómico",
        82: "Observar las máquinas cuando las montan",
        83: "Escribir artículos en el periódico",
        84: "Experimentar con la necesidad de oxígeno para la combustión",
        85: "Hacer un proyecto de decoración interior",
        86: "Cuidar a mis hermanos menores",
        87: "Mostrar un nuevo producto al público",
        88: "Resolver problemas matemáticos",
        89: "Ser compositor de música",
        90: "Observar a menudo como transportan las hormigas su carga"
    }

    # Inicializar puntajes
    scores_t3 = {cat: 0 for cat in AREAS_TEST3.keys()}
    
    with st.expander("Abrir Cuestionario Hereford", expanded=True):
        # Layout vertical para mejor lectura en móviles
        
        for q_id in range(1, 91):
            q_text = QUESTIONS_TEXT_T3.get(q_id, f"Pregunta {q_id}")
            
            # Encontrar categoría según ID
            category = "Otros"
            for cat, ids in AREAS_TEST3.items():
                if q_id in ids:
                    category = cat
                    break
            
            # Slider de 1 a 5, por defecto 3 (Me desagrada mucho)
            val = st.slider(f"**{q_id}.** {q_text}", 1, 5, 3, key=f"t3_q{q_id}")
            if category in scores_t3:
                scores_t3[category] += val
    
    st.session_state.test3_scores = scores_t3
    
    st.divider()
    if scores_t3:
        dominant_cat = max(scores_t3, key=scores_t3.get)
        st.metric("Área de Mayor Interés (Preliminar)", dominant_cat)

# --- Tab 5: Finalizar ---
with tab5:
    st.header("Resultados y Envío")
    
    # Verificar que haya datos
    if not st.session_state.student_data:
        st.warning("⚠️ Primero debes completar tus Datos Personales en la pestaña 1.")
    else:
        # Calcular Resultados (para tenerlos listos)
        
        # --- Cálculo Test 1 ---
        scores_t1 = st.session_state.test1_scores
        if scores_t1:
            sorted_t1 = sorted(scores_t1.items(), key=lambda x: x[1], reverse=True)
            top1_t1 = sorted_t1[0][0] if len(sorted_t1) > 0 else "N/A"
            top2_t1 = sorted_t1[1][0] if len(sorted_t1) > 1 else "N/A"
        else:
            top1_t1, top2_t1 = "Pendiente", "Pendiente"

        # --- Cálculo Test 2 ---
        MAP_T2 = {
            "A": "Comercio", "B": "Mecánica", "C": "Artístico", "D": "Manuales",
            "E": "Agrícola", "F": "Literario", "G": "Científico", "H": "Social",
            "I": "Oficina", "J": "Fuerzas Armadas"
        }
        scores_t2 = st.session_state.test2_scores
        if scores_t2:
            cat_max_t2 = max(scores_t2, key=scores_t2.get)
            nombre_cat_t2 = MAP_T2.get(cat_max_t2, cat_max_t2)
            res_t2 = f"{cat_max_t2} ({nombre_cat_t2})"
        else:
            res_t2 = "Pendiente"

        # --- Cálculo Test 3 ---
        scores_t3 = st.session_state.test3_scores
        if scores_t3:
            sorted_t3 = sorted(scores_t3.items(), key=lambda x: x[1], reverse=True)
            res_t3_list = [f"{k} ({v})" for k, v in sorted_t3]
            res_t3_str = ", ".join(res_t3_list)
        else:
            res_t3_str = "Pendiente"

        # --- Lógica de Visualización ---
        
        if not st.session_state.results_sent:
            st.info("ℹ️ Para ver tu Reporte de Resultados Vocacionales, primero debes enviar tus respuestas.")
            
            if st.button("🚀 Enviar Resultados"):
                if not scores_t1 or not scores_t2 or not scores_t3:
                   st.error("⚠️ Por favor completa los 3 tests antes de enviar.")
                else:
                    # Preparar Datos
                    final_data = {
                        "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        **st.session_state.student_data,
                        "T1_Primera_Opcion": top1_t1,
                        "T1_Segunda_Opcion": top2_t1,
                        "T2_Dominante": res_t2,
                        "T3_Resultados_Ordenados": res_t3_str
                    }
                    
                    # Guardar en Google Sheets (Lógica Segura sin Race Conditions)
                    try:
                        # Usar gspread directamente para operación atómica 'append_row'
                        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                        
                        # Obtener secretos (asumiendo estructura estándar de st-gsheets-connection)
                        secrets = dict(st.secrets["connections"]["gsheets"])
                        
                        # Autenticación
                        creds = Credentials.from_service_account_info(secrets, scopes=scope)
                        client = gspread.authorize(creds)
                        
                        # Abrir Hoja
                        sheet_url = secrets.get("spreadsheet")
                        sh = client.open_by_url(sheet_url)
                        worksheet = sh.worksheet("Hoja 1")
                        
                        # Verificar encabezados (si la hoja está vacía)
                        existing_data = worksheet.get_all_values()
                        
                        if not existing_data:
                            # Si está vacía, escribimos headers primero
                            headers = list(final_data.keys())
                            worksheet.append_row(headers)
                        else:
                            # Si ya tiene datos, usamos la primera fila como headers para alinear
                            headers = existing_data[0]
                        
                        # Alinear datos con los encabezados existentes
                        row_to_append = [str(final_data.get(h, "")) for h in headers]
                        
                        # Append Atómico
                        worksheet.append_row(row_to_append)
                        
                        # Actualizar estado y recargar
                        st.session_state.results_sent = True
                        st.rerun() # Recargar para mostrar resultados
                        
                    except Exception as e:
                        st.error(f"❌ Error al conectar con Google Sheets: {e}")
                        st.write("Verifica tu archivo secrets.toml y los permisos de la hoja.")
        
        else:
            # Si ya se enviaron, mostramos éxito y resultados
            st.success("✅ ¡Datos enviados correctamente! Aquí tienes tu resumen vocacional:")
            st.balloons()
            
            st.write("### Resumen de Resultados")
            if scores_t1:
                st.info(f"**Test 1 (Intereses):**\n- 1ra Opción: {top1_t1}\n- 2da Opción: {top2_t1}")
            if scores_t2:
                st.info(f"**Test 2 (Canihuante):**\n- Interés Dominante: {res_t2}")
            if scores_t3:
                st.info(f"**Test 3 (Hereford):**\nOrden de Preferencia:\n{', '.join(res_t3_list[:3])}...")
            


            st.divider()
            if st.button("🔄 Comenzar Nuevo Estudiante"):
                # Resetear todo
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()
