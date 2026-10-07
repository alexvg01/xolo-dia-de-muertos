"""Xolo en el navegador: el mismo chatbot de xolo.py con interfaz web (Streamlit).

En tu computadora:
    export ANTHROPIC_API_KEY="tu-clave"
    uv run --with-requirements requirements.txt streamlit run app.py

Publicado en Streamlit Community Cloud, la clave va en los Secrets de la app
(ver LEEME.md). Quien abre el enlace no necesita cuenta de nada: las respuestas
se pagan con tu clave, por eso hay un tope de preguntas por sesión.
"""

from __future__ import annotations

import os

import anthropic
import streamlit as st

import estilo
from xolo_base import MAX_TOKENS, MODELO, ErrorDeConfiguracion, armar_sistema, detalle, huella, recientes

MAX_PREGUNTAS = 30       # por sesión del navegador; cuida tu saldo si el enlace circula
MAX_CARACTERES = 1000    # largo máximo de cada pregunta
AVATAR = {"user": None, "assistant": estilo.FLOR}
SUGERENCIAS = [
    "¿Qué lleva una ofrenda y qué significa cada cosa?",
    "¿De dónde viene la Catrina?",
    "¿Cómo se celebra en Oaxaca, Michoacán y Yucatán?",
    "Escríbeme una calaverita para mi amigo Beto, que siempre llega tarde",
]

st.set_page_config(page_title="Xolo, guía de Día de Muertos", page_icon="🏵️")


def con_aviso(fragmentos, aviso):
    """Deja pasar el texto de la respuesta y quita el aviso de "Pensando…" al llegar la primera palabra."""
    try:
        for fragmento in fragmentos:
            aviso.empty()
            yield fragmento
    finally:
        aviso.empty()


def clave_api() -> str | None:
    """En Streamlit Community Cloud la clave está en Secrets; en tu computadora, en la variable de entorno."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


@st.cache_resource
def cliente() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=clave_api())


@st.cache_resource(max_entries=1)
def sistema(archivos: tuple) -> tuple[list[dict], list[str]]:
    """Instrucciones y documentos se leen una vez y se vuelven a leer solo si algún archivo cambia."""
    return armar_sistema()


estilo.aplicar()
estilo.encabezado(
    "Pregúntale a Xolo",
    "Un guía de Día de Muertos: la ofrenda, las flores, la comida, las calaveritas y cómo se celebra en cada región.",
)

if not clave_api():
    st.error("Xolo no está configurado: falta la clave ANTHROPIC_API_KEY.")
    st.stop()
try:
    bloques, _ = sistema(huella())
except ErrorDeConfiguracion as error:
    st.error(str(error))
    st.stop()

historial: list[dict] = st.session_state.setdefault("historial", [])
# Tope por sesión: las respuestas las paga tu clave.
limite = sum(1 for m in historial if m["role"] == "user") >= MAX_PREGUNTAS

# Pie fijo: caja de escritura y, debajo, "Conversación nueva" y el aviso.
with st.bottom:
    escrita = st.chat_input("Escribe tu pregunta…", max_chars=MAX_CARACTERES, disabled=limite)
    with st.container(key="pie", horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        if st.button("Conversación nueva", key="nueva", type="tertiary"):
            st.session_state.historial = []
            st.rerun()
        st.caption("Xolo es una IA y puede equivocarse.")

# Saludo fijo de Xolo; las preguntas sugeridas solo aparecen antes del primer mensaje.
elegida = None
with st.chat_message("assistant", avatar=AVATAR["assistant"]):
    st.markdown("Hola, soy Xolo. ¿Qué quieres saber del Día de Muertos?")
    zona_sugerencias = st.empty()
    if not historial:
        with zona_sugerencias.container(key="sugerencias"):
            st.caption("Puedes empezar con una de estas preguntas:")
            for sugerencia in SUGERENCIAS:
                if st.button(sugerencia, type="tertiary", width="stretch"):
                    elegida = sugerencia

for mensaje in historial:
    with st.chat_message(mensaje["role"], avatar=AVATAR[mensaje["role"]]):
        st.markdown(mensaje["content"])

if limite:
    st.info("Llegaste al límite de preguntas de esta sesión. Empieza una conversación nueva para seguir.")

pregunta = None if limite else (escrita or elegida)

if pregunta:
    zona_sugerencias.empty()   # las sugerencias desaparecen al empezar la conversación
    historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    respuesta = ""
    with st.chat_message("assistant", avatar=AVATAR["assistant"]):
        aviso = st.empty()
        aviso.html('<p class="xolo-pensando">Pensando…</p>')
        try:
            with cliente().messages.stream(
                model=MODELO,
                max_tokens=MAX_TOKENS,
                system=bloques,                  # instrucciones + documentos (con caché)
                messages=recientes(historial),   # la API no guarda memoria: va el historial cada vez
            ) as stream:
                respuesta = st.write_stream(con_aviso(stream.text_stream, aviso))
                final = stream.get_final_message()
            if not (isinstance(respuesta, str) and respuesta.strip()):
                st.caption("No llegó respuesta. Escribe la pregunta de otra forma.")
            elif final.stop_reason == "max_tokens":
                st.caption("La respuesta se cortó por longitud. Pide la parte que falta.")
        except anthropic.RateLimitError:
            aviso.empty()
            st.warning("Xolo está recibiendo muchas preguntas. Espera un momento y vuelve a intentar.")
        except anthropic.APIConnectionError:
            aviso.empty()
            st.warning("No hubo conexión con la API. Vuelve a intentar en un momento.")
        except anthropic.APIStatusError as error:
            # El detalle va al registro del servidor; al visitante solo se le avisa.
            aviso.empty()
            print(f"Error {error.status_code} de la API: {detalle(error)}", flush=True)
            st.error(f"Xolo no pudo responder (error {error.status_code}). Vuelve a intentar más tarde.")

    if isinstance(respuesta, str) and respuesta.strip():
        historial.append({"role": "assistant", "content": respuesta.rstrip()})
    else:
        historial.pop()  # sin respuesta, la pregunta no se queda en el historial
