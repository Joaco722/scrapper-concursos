"""Interfaz visual local para el scraper de concursos CGE."""

import pandas as pd
import streamlit as st

from servicio_concursos import ESCUELAS_CLAVE, buscar_concursos


st.set_page_config(page_title="Concursos CGE", page_icon="📚", layout="wide")
st.title("Concursos docentes CGE")
st.caption("Seguimiento de publicaciones recientes para las escuelas configuradas.")

with st.sidebar:
    st.header("Escuelas seguidas")
    for escuela in ESCUELAS_CLAVE:
        st.write(f"• {escuela}")
    st.divider()
    st.caption("La búsqueda revisa publicaciones de los últimos tres días.")

if st.button("Buscar concursos", type="primary", use_container_width=True):
    with st.spinner("Consultando publicaciones del CGE..."):
        try:
            resultados = buscar_concursos()
        except Exception as error:
            st.error(f"No se pudo completar la búsqueda: {error}")
            resultados = None

    if resultados is not None:
        if not resultados:
            st.info("No hubo publicaciones para las escuelas seguidas en los últimos tres días.")
        else:
            datos = [
                {
                    "Escuela": resultado["escuela"] or "Sin identificar",
                    "Fecha publicación": resultado["fecha_texto"],
                    "Fecha sorteo": resultado["fecha_sorteo"] or "No especificada",
                    "Materias": ", ".join(resultado["materias"]) or "No informadas",
                    "Publicación": resultado["url"],
                }
                for resultado in resultados
            ]
            tabla = pd.DataFrame(datos)

            primera, segunda = st.columns(2)
            primera.metric("Publicaciones encontradas", len(tabla))
            segunda.metric("Escuelas con novedades", tabla["Escuela"].nunique())

            st.dataframe(
                tabla,
                column_config={
                    "Publicación": st.column_config.LinkColumn(
                        "Publicación", display_text="Abrir aviso"
                    )
                },
                hide_index=True,
                use_container_width=True,
            )
else:
    st.info("Selecciona “Buscar concursos” para consultar las novedades.")
