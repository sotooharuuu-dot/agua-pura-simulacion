
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import streamlit.components.v1 as components
import time

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Agua Pura S.A.C. | Simulador Industrial",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. DISEÑO VISUAL
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f3f7fc;
    }

    [data-testid="stSidebar"] {
        background: #102b46;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-header {
        background: linear-gradient(120deg, #0b2942, #087eaa);
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 25px rgba(10, 50, 80, 0.16);
    }

    .main-header h1 {
        color: white;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }

    .main-header p {
        color: #d8f2ff;
        margin: 8px 0 0 0;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e4edf5;
        box-shadow: 0 4px 14px rgba(20, 55, 80, 0.05);
        min-height: 115px;
    }

    .metric-label {
        color: #718096;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #12344d;
        font-size: 27px;
        font-weight: 800;
        margin-top: 7px;
    }

    .metric-note {
        color: #159b83;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-title {
        color: #12344d;
        font-size: 21px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .station-card {
        background: white;
        border: 1px solid #e3edf5;
        border-radius: 12px;
        padding: 13px 8px;
        text-align: center;
        min-height: 115px;
        box-shadow: 0 3px 10px rgba(20, 55, 80, 0.04);
    }

    .station-icon {
        font-size: 27px;
    }

    .station-name {
        color: #173c57;
        font-size: 12px;
        font-weight: 700;
        margin-top: 7px;
    }

    .station-time {
        color: #718096;
        font-size: 11px;
        margin-top: 4px;
    }

    .info-box {
        background: #e8f5fc;
        border-left: 4px solid #0786b7;
        padding: 14px;
        border-radius: 8px;
        color: #24445d;
        margin: 10px 0;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e4edf5;
    }

    .stButton button {
        border-radius: 9px;
        font-weight: 700;
    }
    /* Texto de los campos de entrada de la barra lateral */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Número escrito en los campos */
[data-testid="stSidebar"] input[type="number"] {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background-color: #ffffff !important;
}

/* Presentación del producto y otros selectores */
[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #000000 !important;
}

/* Fondo blanco de los controles */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] input {
    background-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. DATOS DEL PROCESO PRODUCTIVO
# =========================================================

operaciones = [
    "Recepción",
    "Inspección",
    "Lavado",
    "Llenado",
    "Tapado",
    "Etiquetado",
    "Empaquetado"
]

iconos = ["📥", "🔍", "🚿", "💧", "🧢", "🏷️", "📦"]

tiempos_observados = [8, 12, 15, 18, 10, 14, 20]

factores_valoracion = [1.00, 1.05, 1.00, 1.10, 1.00, 1.05, 0.95]

mejoras = [15, 30, 20, 25, 20, 25, 30]

# =========================================================
# 4. PARÁMETROS DEL SIMULADOR
# =========================================================

st.sidebar.markdown("## 💧 AGUA PURA S.A.C.")
st.sidebar.caption("Sistema de simulación industrial")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Parámetros de producción")

lote = st.sidebar.number_input(
    "Cantidad de botellas por lote",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100
)

presentacion = st.sidebar.selectbox(
    "Presentación del producto",
    ["500 ml", "625 ml", "1 litro"]
)

horas_turno = st.sidebar.slider(
    "Horas de trabajo por turno",
    min_value=1,
    max_value=12,
    value=8
)

eficiencia = st.sidebar.slider(
    "Eficiencia de operación (%)",
    min_value=50,
    max_value=100,
    value=85
)

suplemento = st.sidebar.slider(
    "Suplementos personales y por fatiga (%)",
    min_value=5,
    max_value=20,
    value=10
)

defectos_porcentaje = st.sidebar.slider(
    "Porcentaje de productos defectuosos (%)",
    min_value=0.0,
    max_value=15.0,
    value=2.0,
    step=0.5
)

# =========================================================
# 5. CÁLCULOS DEL ESTUDIO DE TIEMPOS
# =========================================================

datos = pd.DataFrame({
    "Operación": operaciones,
    "Tiempo observado (s)": tiempos_observados,
    "Valoración (%)": [x * 100 for x in factores_valoracion],
    "Mejora propuesta (%)": mejoras
})

datos["Tiempo normal (s)"] = (
    datos["Tiempo observado (s)"] *
    datos["Valoración (%)"] / 100
)

datos["Tiempo estándar (s)"] = (
    datos["Tiempo normal (s)"] *
    (1 + suplemento / 100)
)

datos["Tiempo mejorado (s)"] = (
    datos["Tiempo estándar (s)"] *
    (1 - datos["Mejora propuesta (%)"] / 100)
)

cuello = datos.loc[datos["Tiempo estándar (s)"].idxmax()]

tiempo_ciclo = datos["Tiempo estándar (s)"].max()

capacidad_hora = 3600 / tiempo_ciclo

capacidad_turno = (
    capacidad_hora *
    horas_turno *
    eficiencia / 100
)

produccion_real = min(lote, int(capacidad_turno))

productos_defectuosos = int(
    produccion_real * defectos_porcentaje / 100
)

productos_buenos = produccion_real - productos_defectuosos

tiempo_total_lote = (
    datos["Tiempo estándar (s)"].sum() * produccion_real
)

tiempo_promedio_mejorado = datos["Tiempo mejorado (s)"].max()

capacidad_mejorada_hora = 3600 / tiempo_promedio_mejorado

aumento_capacidad = (
    (capacidad_mejorada_hora - capacidad_hora) /
    capacidad_hora * 100
)

# =========================================================
# 6. ENCABEZADO
# =========================================================

st.markdown("""
<div class="main-header">
    <h1>💧 AGUA PURA S.A.C.</h1>
    <p>Sistema de simulación y mejora del proceso de producción de agua embotellada</p>
    <p>INGENIERÍA DE MÉTODOS | ESTUDIO DE TIEMPOS</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 7. MENÚ PRINCIPAL
# =========================================================

secciones = [
    "Dashboard",
    "Planta virtual",
    "Llenado animado",
    "Estudio de tiempos",
    "Análisis de problemas",
    "Propuesta de mejora",
    "Reportes"
]

seccion = st.sidebar.radio(
    "NAVEGACIÓN",
    secciones
)

st.sidebar.markdown("---")
st.sidebar.caption("Proyecto académico | Datos simulados")

# =========================================================
# 8. DASHBOARD
# =========================================================

if seccion == "Dashboard":

    st.markdown('<div class="section-title">📊 Panel de control de producción</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PRODUCCIÓN DEL TURNO</div>
            <div class="metric-value">{produccion_real:,}</div>
            <div class="metric-note">Botellas procesadas</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PRODUCTOS BUENOS</div>
            <div class="metric-value">{productos_buenos:,}</div>
            <div class="metric-note">Productos aceptados</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">DEFECTUOSOS</div>
            <div class="metric-value">{productos_defectuosos:,}</div>
            <div class="metric-note">Productos rechazados</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CAPACIDAD POR HORA</div>
            <div class="metric-value">{capacidad_hora:,.1f}</div>
            <div class="metric-note">Botellas teóricas/hora</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="section-title">🏭 Etapas del proceso productivo</div>', unsafe_allow_html=True)

    columnas = st.columns(7)

    for i, col in enumerate(columnas):
        with col:
            st.markdown(f"""
            <div class="station-card">
                <div class="station-icon">{iconos[i]}</div>
                <div class="station-name">{operaciones[i]}</div>
                <div class="station-time">{tiempos_observados[i]} segundos</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    izquierda, derecha = st.columns(2)

    with izquierda:
        st.markdown("#### Tiempo estándar por operación")

        grafico = px.bar(
            datos,
            x="Operación",
            y="Tiempo estándar (s)",
            color="Tiempo estándar (s)",
            color_continuous_scale="Blues",
            text_auto=".1f"
        )

        grafico.update_layout(
            template="plotly_white",
            height=370,
            transition_duration=1000,
            coloraxis_showscale=False,
            xaxis_title="Etapa",
            yaxis_title="Segundos"
        )

        st.plotly_chart(grafico, use_container_width=True)

    with derecha:
        st.markdown("#### Distribución de productos")

        grafico_pastel = go.Figure(
            data=[go.Pie(
                labels=["Productos buenos", "Defectuosos"],
                values=[productos_buenos, productos_defectuosos],
                hole=0.60,
                marker=dict(colors=["#087eaa", "#f59e0b"])
            )]
        )

        grafico_pastel.update_layout(
            template="plotly_white",
            height=370,
            transition_duration=1000
        )

        st.plotly_chart(grafico_pastel, use_container_width=True)

    st.markdown('<div class="info-box">📌 <b>Cuello de botella identificado:</b> ' + cuello["Operación"] + ' con un tiempo estándar de ' + f'{cuello["Tiempo estándar (s)"]:.2f} segundos.</div>', unsafe_allow_html=True)

# =========================================================
# 9. PLANTA VIRTUAL
# =========================================================

elif seccion == "Planta virtual":

    st.markdown('<div class="section-title">🏭 Simulación de la línea de producción</div>', unsafe_allow_html=True)

    st.write(
        "Observa cómo avanza el lote de botellas por las diferentes estaciones de la planta."
    )

    st.markdown("#### Línea de producción")

    columnas = st.columns(7)

    for i, col in enumerate(columnas):
        with col:
            st.markdown(f"""
            <div class="station-card">
                <div class="station-icon">{iconos[i]}</div>
                <div class="station-name">{operaciones[i]}</div>
                <div class="station-time">{tiempos_observados[i]} s/unidad</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### Control de simulación")

    cantidad_simular = st.number_input(
        "Botellas que se procesarán en esta demostración",
        min_value=1,
        max_value=100,
        value=10
    )

    if st.button("▶ Iniciar simulación de producción", type="primary", use_container_width=True):

        barra = st.progress(0)
        estado = st.empty()
        estacion_actual = st.empty()

        for i, operacion in enumerate(operaciones):

            estado.info(f"Proceso en ejecución: {operacion}")

            estacion_actual.markdown(
                f"### {iconos[i]} {operacion}"
            )

            for avance in range(1, 101, 10):
                barra.progress(
                    int((i * 100 + avance) / len(operaciones))
                )
                time.sleep(0.025)

        barra.progress(100)
        estado.success(
            f"Simulación finalizada. Se procesaron {cantidad_simular} botellas de demostración."
        )
        estacion_actual.markdown("### ✅ Lote terminado")

        st.balloons()

    st.markdown("---")

    st.markdown("#### Distribución de tiempos por estación")

    fig = px.bar(
        datos,
        x="Operación",
        y="Tiempo estándar (s)",
        color="Operación",
        text_auto=".1f"
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        transition_duration=1000,
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "La simulación representa las etapas del proceso. Los tiempos son datos académicos simulados."
    )


# =========================================================
# 10. LLENADO ANIMADO - BOTELLA EN UNA SOLA POSICIÓN
# =========================================================

elif seccion == "Llenado animado":

    st.markdown(
        '<div class="section-title">💧 Estación de llenado automático</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Observa cómo una botella recibe agua progresivamente "
        "hasta alcanzar su capacidad de 500 ml."
    )

    col1, col2 = st.columns([1.3, 1])

    with col1:

        velocidad = st.slider(
            "Velocidad de llenado",
            min_value=1,
            max_value=10,
            value=5,
            help="A mayor valor, más rápido se llena la botella."
        )

        iniciar = st.button(
            "▶ Iniciar llenado",
            type="primary",
            use_container_width=True
        )

        reiniciar = st.button(
            "↺ Reiniciar botella",
            use_container_width=True
        )

        if iniciar or reiniciar:

            if reiniciar:
                duracion = 0.01
            else:
                duracion = 6 / velocidad * 5

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    padding: 10px;
                    background: #f3f8fc;
                    font-family: Arial, sans-serif;
                    text-align: center;
                }}

                .contenedor {{
                    background: white;
                    border-radius: 18px;
                    padding: 18px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
                }}

                .botella {{
                    position: relative;
                    width: 150px;
                    height: 330px;
                    margin: 15px auto;
                }}

                .cuello {{
                    position: absolute;
                    width: 48px;
                    height: 43px;
                    top: 0;
                    left: 51px;
                    border: 4px solid #8bbbd5;
                    border-bottom: none;
                    border-radius: 8px 8px 0 0;
                    background: #f7fcff;
                    z-index: 3;
                }}

                .tapa {{
                    position: absolute;
                    width: 55px;
                    height: 16px;
                    top: -7px;
                    left: 47px;
                    border-radius: 5px;
                    background: #087eaa;
                    z-index: 4;
                }}

                .cuerpo {{
                    position: absolute;
                    top: 37px;
                    left: 5px;
                    width: 140px;
                    height: 280px;
                    border: 5px solid #8bbbd5;
                    border-radius: 28px 28px 30px 30px;
                    overflow: hidden;
                    background: linear-gradient(
                        90deg,
                        #edfaff,
                        #ffffff,
                        #e9f7ff
                    );
                    box-shadow: inset 0 0 15px rgba(0,100,160,0.08);
                }}

                .agua {{
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 0%;
                    background: linear-gradient(
                        90deg,
                        #0784c2,
                        #42c3ec,
                        #0784c2
                    );
                    transition: height 0.08s linear;
                }}

                .superficie {{
                    position: absolute;
                    top: -5px;
                    left: 0;
                    width: 100%;
                    height: 10px;
                    background: rgba(210,248,255,0.7);
                    border-radius: 50%;
                }}

                .etiqueta {{
                    position: absolute;
                    top: 105px;
                    left: 9px;
                    width: 112px;
                    height: 70px;
                    border-radius: 8px;
                    background: white;
                    border: 2px solid #087eaa;
                    z-index: 2;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    color: #07547b;
                    font-weight: bold;
                }}

                .etiqueta small {{
                    font-size: 10px;
                    margin-top: 5px;
                }}

                .brillo {{
                    position: absolute;
                    top: 25px;
                    left: 15px;
                    width: 9px;
                    height: 210px;
                    border-radius: 10px;
                    background: rgba(255,255,255,0.65);
                    z-index: 3;
                }}

                .nivel {{
                    color: #087eaa;
                    font-size: 29px;
                    font-weight: bold;
                    margin: 12px;
                }}

                .barra {{
                    width: 100%;
                    height: 13px;
                    background: #e5edf4;
                    border-radius: 20px;
                    overflow: hidden;
                }}

                .progreso {{
                    height: 100%;
                    width: 0%;
                    background: linear-gradient(90deg,#087eaa,#39c1e9);
                    border-radius: 20px;
                }}

                .estado {{
                    color: #547087;
                    font-size: 14px;
                    margin-top: 12px;
                    min-height: 20px;
                }}
            </style>
            </head>

            <body>

            <div class="contenedor">

                <h3 style="color:#153b55;margin:5px;">
                    ESTACIÓN DE LLENADO
                </h3>

                <div class="botella">

                    <div class="tapa"></div>

                    <div class="cuello"></div>

                    <div class="cuerpo">

                        <div class="agua" id="agua">
                            <div class="superficie"></div>
                        </div>

                        <div class="etiqueta">
                            AGUA PURA
                            <small>AGUA NATURAL</small>
                            <small>500 ml</small>
                        </div>

                        <div class="brillo"></div>

                    </div>

                </div>

                <div class="nivel" id="nivel">0 ml</div>

                <div class="barra">
                    <div class="progreso" id="progreso"></div>
                </div>

                <div class="estado" id="estado">
                    Esperando inicio del llenado...
                </div>

            </div>

            <script>
                const agua = document.getElementById("agua");
                const nivel = document.getElementById("nivel");
                const progreso = document.getElementById("progreso");
                const estado = document.getElementById("estado");

                const duracion = {duracion};

                function animarLlenado() {{

                    if (duracion <= 0.01) {{
                        agua.style.height = "0%";
                        nivel.textContent = "0 ml";
                        progreso.style.width = "0%";
                        estado.textContent = "Botella vacía";
                        return;
                    }}

                    const inicio = performance.now();

                    estado.textContent = "Válvula abierta: ingresando agua...";

                    function actualizar(tiempo) {{

                        const transcurrido = (tiempo - inicio) / 1000;

                        const porcentaje = Math.min(
                            transcurrido / duracion,
                            1
                        ) * 100;

                        const mililitros = Math.round(
                            porcentaje * 5
                        );

                        agua.style.height = porcentaje + "%";
                        nivel.textContent = mililitros + " ml";
                        progreso.style.width = porcentaje + "%";

                        if (porcentaje < 100) {{
                            requestAnimationFrame(actualizar);
                        }} else {{
                            nivel.textContent = "500 ml";
                            estado.textContent =
                                "✓ Llenado completado. Válvula cerrada.";
                        }}
                    }}

                    requestAnimationFrame(actualizar);
                }}

                animarLlenado();
            </script>

            </body>
            </html>
            """

            components.html(
                html,
                height=450,
                scrolling=False
            )

        else:

            components.html("""
            <div style="
                background:#f3f8fc;
                padding:20px;
                border-radius:15px;
                text-align:center;
                font-family:Arial;
                color:#547087;
            ">
                <h3>💧 Botella lista para llenar</h3>
                <p>Presiona «Iniciar llenado» para comenzar.</p>
                <div style="
                    width:130px;
                    height:220px;
                    margin:20px auto;
                    border:5px solid #8bbbd5;
                    border-radius:25px;
                    background:linear-gradient(90deg,#edfaff,#fff);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#087eaa;
                    font-weight:bold;
                ">
                    AGUA PURA
                </div>
                <p>Capacidad: 500 ml</p>
            </div>
            """, height=390)

    with col2:

        st.markdown("### 📋 Parámetros de llenado")

        st.metric("Capacidad de botella", "500 ml")
        st.metric("Presentación", "500 ml")
        st.metric("Estación", "Llenado automático")

        st.markdown("---")

        st.markdown("### ⚙️ Secuencia de operación")

        st.markdown("""
        1. La botella llega a la estación.
        2. Se posiciona debajo de la boquilla.
        3. Se abre la válvula de agua.
        4. El nivel del líquido aumenta.
        5. Se alcanzan los 500 ml.
        6. Se cierra la válvula.
        7. La botella continúa al tapado.
        """)

        st.info(
            "La animación representa visualmente el llenado de una botella. "
            "Los valores son simulados."
        )

# =========================================================
# 11. ESTUDIO DE TIEMPOS
# =========================================================

elif seccion == "Estudio de tiempos":

    st.markdown('<div class="section-title">⏱️ Estudio de tiempos del proceso</div>', unsafe_allow_html=True)

    st.write(
        "Se utilizan tiempos observados simulados para calcular el tiempo normal y el tiempo estándar."
    )

    st.markdown("#### Tabla de estudio de tiempos")

    tabla = datos.copy()

    st.dataframe(
        tabla.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Fórmulas utilizadas")

    col1, col2 = st.columns(2)

    with col1:
        st.latex(r"T_N = T_O \times F_V")
        st.caption("Tiempo normal = Tiempo observado × Factor de valoración")

    with col2:
        st.latex(r"T_E = T_N \times (1+S)")
        st.caption("Tiempo estándar = Tiempo normal × (1 + suplementos)")

    st.markdown("#### Comparación de tiempos")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Tiempo observado",
        x=datos["Operación"],
        y=datos["Tiempo observado (s)"]
    ))

    fig.add_trace(go.Bar(
        name="Tiempo estándar",
        x=datos["Operación"],
        y=datos["Tiempo estándar (s)"]
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        height=420,
        transition_duration=1000,
        yaxis_title="Tiempo en segundos"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Resultado del estudio")

    a, b, c = st.columns(3)

    a.metric("Cuello de botella", cuello["Operación"])
    b.metric("Tiempo estándar crítico", f'{tiempo_ciclo:.2f} s')
    c.metric("Capacidad teórica", f"{capacidad_hora:.1f} botellas/h")

# =========================================================
# 12. ANÁLISIS DE PROBLEMAS
# =========================================================

elif seccion == "Análisis de problemas":

    st.markdown('<div class="section-title">🔍 Identificación de problemas productivos</div>', unsafe_allow_html=True)

    st.write(
        "El análisis permite identificar las operaciones que requieren mayor atención."
    )

    st.markdown("#### Cuello de botella")

    st.warning(
        f"La operación crítica es {cuello['Operación']}, con {cuello['Tiempo estándar (s)']:.2f} segundos por botella."
    )

    st.markdown("#### Problemas identificados")

    problemas = pd.DataFrame({
        "Problema": [
            "Tiempo elevado de empaquetado",
            "Inspección manual",
            "Demoras en el lavado",
            "Llenado prolongado",
            "Productos defectuosos"
        ],
        "Causa posible": [
            "Organización del puesto de trabajo",
            "Falta de estandarización",
            "Preparación insuficiente de materiales",
            "Ajuste de la operación de llenado",
            "Falta de control de calidad"
        ],
        "Acción propuesta": [
            "Organizar materiales y herramientas",
            "Estandarizar criterios de inspección",
            "Preparar materiales antes del turno",
            "Revisar parámetros de llenado",
            "Implementar inspecciones periódicas"
        ]
    })

    st.dataframe(
        problemas,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Distribución de los tiempos")

    fig = px.pie(
        datos,
        names="Operación",
        values="Tiempo estándar (s)",
        hole=0.45
    )

    fig.update_layout(
        template="plotly_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 13. PROPUESTA DE MEJORA
# =========================================================

elif seccion == "Propuesta de mejora":

    st.markdown('<div class="section-title">📈 Evaluación de las mejoras propuestas</div>', unsafe_allow_html=True)

    st.write(
        "Se comparan los tiempos estándar actuales con los tiempos estimados después de aplicar mejoras."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Capacidad actual",
        f"{capacidad_hora:.1f} botellas/h"
    )

    col2.metric(
        "Capacidad mejorada",
        f"{capacidad_mejorada_hora:.1f} botellas/h",
        f"{aumento_capacidad:.1f}%"
    )

    col3.metric(
        "Reducción del cuello crítico",
        f"{(tiempo_ciclo-tiempo_promedio_mejorado):.2f} s"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Antes de la mejora",
        x=datos["Operación"],
        y=datos["Tiempo estándar (s)"]
    ))

    fig.add_trace(go.Bar(
        name="Después de la mejora",
        x=datos["Operación"],
        y=datos["Tiempo mejorado (s)"]
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_white",
        height=430,
        transition_duration=1200,
        yaxis_title="Tiempo en segundos"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Acciones de mejora")

    for _, fila in datos.iterrows():
        st.markdown(
            f"**{fila['Operación']}:** reducción estimada del {fila['Mejora propuesta (%)']:.0f}% del tiempo estándar."
        )

    st.info(
        "Los porcentajes de mejora son supuestos académicos para la simulación. Deben validarse mediante nuevas mediciones."
    )

# =========================================================
# 14. REPORTES
# =========================================================

elif seccion == "Reportes":

    st.markdown('<div class="section-title">📑 Reportes de producción</div>', unsafe_allow_html=True)

    st.markdown("#### Resumen de resultados")

    resumen = pd.DataFrame({
        "Indicador": [
            "Lote solicitado",
            "Producción procesada",
            "Productos buenos",
            "Productos defectuosos",
            "Capacidad por hora",
            "Tiempo estándar crítico",
            "Cuello de botella",
            "Capacidad mejorada por hora"
        ],
        "Resultado": [
            lote,
            produccion_real,
            productos_buenos,
            productos_defectuosos,
            round(capacidad_hora, 2),
            round(tiempo_ciclo, 2),
            cuello["Operación"],
            round(capacidad_mejorada_hora, 2)
        ]
    })

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )

    csv = datos.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Descargar estudio de tiempos en CSV",
        data=csv,
        file_name="estudio_tiempos_agua_pura.csv",
        mime="text/csv",
        use_container_width=True
    )

    csv_resumen = resumen.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Descargar resumen de producción en CSV",
        data=csv_resumen,
        file_name="reporte_produccion_agua_pura.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.success(
        "Los reportes se encuentran preparados para descargarse y utilizarse en el análisis del proyecto."
    )

# =========================================================
# 15. PIE DE PÁGINA
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#718096; padding:10px;">
        <b>AGUA PURA S.A.C.</b><br>
        Simulación de procesos productivos | Ingeniería de Métodos<br>
        <small>Proyecto académico con datos simulados</small>
    </div>
    """,
    unsafe_allow_html=True
)
