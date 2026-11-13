import requests
import streamlit as st

from explorar import cargar_partidas

st.title("Análisis de partidas de Chess.com")

usuario = st.text_input("Usuario de Chess.com").strip().lower()

if st.button("Analizar"):
    if not usuario:
        st.warning("Escribe un usuario de Chess.com.")
    else:
        try:
            with st.spinner("Descargando las partidas..."):
                df = cargar_partidas(usuario, ultimos_meses=3)
        except requests.HTTPError as error:
            if error.response is not None and error.response.status_code == 404:
                st.error(f"No encontré al usuario «{usuario}». Revisa cómo está escrito.")
            else:
                st.error("Chess.com no respondió bien. Intenta de nuevo en unos minutos.")
        except requests.RequestException:
            st.error("No pude conectarme a Chess.com. Revisa tu conexión a internet.")
        except ValueError as error:
            st.warning(str(error))
        else:
            st.success(f"Se descargaron {len(df)} partidas")
            st.dataframe(df[["fecha", "time_class", "mi_color", "mi_rating", "resultado"]].head(10))