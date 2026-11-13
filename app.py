import altair as alt
import requests
import streamlit as st

from explorar import cargar_partidas

MODOS = ["blitz", "rapid", "bullet"]


@st.cache_data(ttl=3600, show_spinner=False)
def descargar(usuario, meses):
    """Descarga las partidas. Streamlit recuerda el resultado durante 1 hora."""
    return cargar_partidas(usuario, ultimos_meses=meses)


def grafica_barras(serie, titulo_y, orden=None, colores=None):
    """Gráfica de barras con el eje vertical empezando en 0 y las etiquetas rectas."""
    datos = serie.reset_index()
    datos.columns = ["categoria", "valor"]

    color = alt.value("#4C9AFF")
    if colores:
        color = alt.Color(
            "categoria:N",
            scale=alt.Scale(domain=list(colores), range=list(colores.values())),
            legend=None,
        )

    return (
        alt.Chart(datos)
        .mark_bar()
        .encode(
            x=alt.X("categoria:N", title=None, sort=orden, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("valor:Q", title=titulo_y, scale=alt.Scale(zero=True, nice=True)),
            color=color,
            tooltip=["categoria", "valor"],
        )
    )


def mostrar_resumen(df):
    corte = df["mi_resultado"].isin(["abandoned", "timeout"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Partidas", len(df))
    col2.metric("Victorias", f"{df['gane'].mean():.1%}")
    col3.metric("Abandono o tiempo", f"{corte.mean():.1%}")

    if len(df) < 100:
        st.caption(
            f"Son solo {len(df)} partidas: con tan pocas, los porcentajes cambian mucho "
            "por azar y no son fiables."
        )

    st.subheader("Resultados")
    resultados = df["resultado"].value_counts()
    st.altair_chart(
        grafica_barras(
            resultados,
            "Partidas",
            orden=["victoria", "derrota", "empate"],
            colores={"victoria": "#2EB67D", "derrota": "#E5534B", "empate": "#8A97A8"},
        ),
        use_container_width=True,
    )

    st.subheader("Victorias por color")
    por_color = (df.groupby("mi_color")["gane"].mean() * 100).round(1)
    st.altair_chart(
        grafica_barras(por_color, "% de victorias", orden=["blancas", "negras"]),
        use_container_width=True,
    )


st.title("Análisis de partidas de Chess.com")

usuario = st.text_input("Usuario de Chess.com").strip().lower()
meses = st.slider("Meses a descargar", min_value=1, max_value=12, value=3)

if st.button("Analizar"):
    # Al pulsar el botón se borran los resultados anteriores
    st.session_state.pop("df", None)

    if not usuario:
        st.warning("Escribe un usuario de Chess.com.")
    else:
        try:
            with st.spinner("Descargando las partidas..."):
                df = descargar(usuario, meses)
        except requests.HTTPError as error:
            codigo = error.response.status_code if error.response is not None else None
            if codigo == 404:
                st.error(f"No encontré al usuario «{usuario}». Revisa cómo está escrito.")
            elif codigo == 429:
                st.error("Chess.com recibió demasiadas peticiones. Espera un minuto e intenta de nuevo.")
            else:
                st.error("Chess.com no respondió bien. Intenta de nuevo en unos minutos.")
        except requests.RequestException:
            st.error("No pude conectarme a Chess.com. Revisa tu conexión a internet.")
        except ValueError as error:
            st.warning(str(error))
        else:
            # Mismo filtro que en el análisis: ajedrez normal en blitz, rapid y bullet
            df = df[(df["rules"] == "chess") & (df["time_class"].isin(MODOS))]
            if df.empty:
                st.warning("No hay partidas de blitz, rapid o bullet en ese periodo.")
            else:
                # Guardar en la memoria de la sesión para que no se pierda
                st.session_state["df"] = df
                st.session_state["usuario_analizado"] = usuario
                st.session_state["meses_analizados"] = meses

# Esto va FUERA del botón: se dibuja siempre que haya resultados guardados
if "df" in st.session_state:
    df = st.session_state["df"]
    n_meses = st.session_state["meses_analizados"]
    periodo = f"los últimos {n_meses} meses" if n_meses > 1 else "el último mes"
    st.success(
        f"{st.session_state['usuario_analizado']}: {len(df)} partidas "
        f"de blitz, rapid y bullet en {periodo}"
    )

    modos = st.multiselect("Modos de juego", MODOS, default=MODOS)
    filtrado = df[df["time_class"].isin(modos)]

    if filtrado.empty:
        st.info("Elige al menos un modo de juego que tenga partidas.")
    else:
        mostrar_resumen(filtrado)

st.divider()
st.caption(
    "Herramienta independiente, sin relación con Chess.com. "
    "Usa los datos públicos de su API."
)