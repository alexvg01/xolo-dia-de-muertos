"""El aspecto de la versión web, copiado del prototipo publicado (su tema oscuro).

Streamlit trae su propio diseño. Aquí se sobrescribe con CSS, apuntando a los
nombres internos de sus elementos (data-testid). Esos nombres pueden cambiar entre
versiones, por eso requirements.txt fija la versión de Streamlit.
"""

from __future__ import annotations

import base64

import streamlit as st

# Paleta del prototipo (tema oscuro)
PAPEL = "#1C0D29"               # fondo
SUPERFICIE = "#2A1440"          # caja de escritura
TINTA = "#F5ECFA"               # texto
TINTA_SUAVE = "#BBA6CC"         # texto secundario
LINEA = "#4A2C63"               # bordes y separadores
MORADO = "#6A2F96"              # burbuja de la persona
SOBRE_MORADO = "#FBF4FF"
ENLACE = "#D9B4F5"
CEMPASUCHIL = "#F8A62B"         # botón Enviar y flor de Xolo
SOBRE_CEMPASUCHIL = "#22102E"
CORDEL = "#7A6190"
COLORES_PAPEL_PICADO = ["#FF2E97", "#FF9F1C", "#A36BDB", "#FFD23F"]   # rosa, naranja, morado, amarillo

FUENTE_TITULO = '"Rozha One", "Abril Fatface", Georgia, "Times New Roman", serif'


def _uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def _banderas() -> dict[str, str]:
    """Las tres banderitas (flor, calavera, rombos) como siluetas con sus recortes.

    Cada una se usa como máscara de un cuadro de color, así el fondo se ve por los agujeros.
    """
    silueta = "M2 6H86V60" + "a7 7 0 0 1-14 0" * 6 + "Z"
    ondas = "".join(f'<circle cx="{x}" cy="60" r="2"/>' for x in (9, 23, 37, 51, 65, 79))
    esquinas = (
        '<path d="M11 10.5l3.6 4.5-3.6 4.5-3.6-4.5zM77 10.5l3.6 4.5-3.6 4.5-3.6-4.5z'
        'M11 44.5l3.6 4.5-3.6 4.5-3.6-4.5zM77 44.5l3.6 4.5-3.6 4.5-3.6-4.5z"/>'
    )
    petalos = "".join(
        f'<ellipse cx="44" cy="18.5" rx="3.3" ry="6.6" transform="rotate({giro} 44 32)"/>'
        for giro in range(0, 360, 45)
    )
    rombos = "".join(
        f"M{x} {y}l5 6-5 6-5-6z"
        for y, xs in ((12, (16, 30, 44, 58, 72)), (26, (23, 37, 51, 65)), (40, (16, 30, 44, 58, 72)))
        for x in xs
    )
    recortes = {
        "flor": ondas + esquinas + '<circle cx="44" cy="32" r="3.2"/>' + petalos,
        "calavera": (
            ondas + esquinas
            + '<circle cx="38.4" cy="31" r="3.7"/><circle cx="49.6" cy="31" r="3.7"/>'
            + '<path d="M44 35.6l2.3 4.2h-4.6z"/>'
            + '<path d="M38.2 44.4h1.7v4h-1.7zM41.5 44.4h1.7v4h-1.7zM44.8 44.4h1.7v4h-1.7zM48.1 44.4h1.7v4h-1.7z"/>'
            + '<ellipse cx="19" cy="32" rx="2.6" ry="7"/><ellipse cx="69" cy="32" rx="2.6" ry="7"/>'
        ),
        "rombos": ondas + f'<path d="{rombos}"/>',
    }
    contorno_calavera = (
        '<path d="M29 31a15 15 0 0 1 30 0v5q0 5.5-6 6.5v8.5h-18v-8.5q-6-1-6-6.5z" '
        'fill="none" stroke="#000" stroke-width="1.9" stroke-dasharray="5.2 2.4"/>'
    )
    return {
        nombre: _uri(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 76" width="88" height="76">'
            '<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="88" height="76">'
            f'<rect width="88" height="76" fill="#fff"/><g fill="#000">{figuras}</g>'
            f'{contorno_calavera if nombre == "calavera" else ""}</mask>'
            f'<path d="{silueta}" mask="url(#m)"/></svg>'
        )
        for nombre, figuras in recortes.items()
    }


def _flor() -> str:
    """La flor de cempasúchil que marca las respuestas de Xolo."""
    petalos = "".join(
        f'<ellipse cx="12" cy="5.4" rx="2.5" ry="4.4" transform="rotate({giro} 12 12)"/>'
        for giro in range(0, 360, 45)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="{CEMPASUCHIL}">'
        f'<circle cx="12" cy="12" r="3.4"/>{petalos}</svg>'
    )


FLOR = _uri(_flor())   # se usa como avatar de Xolo
_B = _banderas()
_ROSA, _NARANJA, _MORADO_PP, _AMARILLO = COLORES_PAPEL_PICADO

# Las medidas en px son las del prototipo (ahí 1rem = 16px; aquí la base es 17px).
CSS = f"""
:root {{ --flag-w: clamp(68px, 48px + 4.5vw, 112px); --flag-h: calc(var(--flag-w) * 76 / 88); }}

/* Lienzo */
.stApp {{ background: {PAPEL}; }}
[data-testid="stHeader"] {{ background: transparent; }}
.stMain {{ position: relative; }}
.stMainBlockContainer {{ max-width: 688px; padding: calc(var(--flag-h) + 30px) 20px 28px; }}
.stMainBlockContainer > [data-testid="stVerticalBlock"] {{ gap: 21.6px; }}

/* Papel picado: una tira de banderitas que se mecen una vez al cargar */
.stElementContainer:has(.xolo-papel) {{ position: static; height: 0; margin-bottom: -21.6px; }}
.xolo-papel {{
  position: absolute; top: 0; left: 0; right: 0;
  display: flex; justify-content: center; overflow: hidden;
  padding: 5.6px 0 8.8px;
  pointer-events: none;
}}
.xolo-papel::after {{
  content: ""; position: absolute; left: 0; right: 0;
  top: calc(5.6px + var(--flag-w) * 6 / 88); height: 1.5px; background: {CORDEL};
}}
.xolo-papel span {{
  flex: 0 0 var(--flag-w); width: var(--flag-w); height: var(--flag-h);
  -webkit-mask: center / contain no-repeat; mask: center / contain no-repeat;
  transform-origin: 50% 7.9%;
  animation: xolo-asentar 2.8s cubic-bezier(.3, .6, .3, 1) both;
}}
.xolo-papel span:nth-child(4n+1) {{ background: {_ROSA}; }}
.xolo-papel span:nth-child(4n+2) {{ background: {_NARANJA}; }}
.xolo-papel span:nth-child(4n+3) {{ background: {_MORADO_PP}; }}
.xolo-papel span:nth-child(4n)   {{ background: {_AMARILLO}; }}
.xolo-papel span:nth-child(3n+1) {{ -webkit-mask-image: url("{_B['flor']}"); mask-image: url("{_B['flor']}"); --giro: 4deg; }}
.xolo-papel span:nth-child(3n+2) {{ -webkit-mask-image: url("{_B['calavera']}"); mask-image: url("{_B['calavera']}"); --giro: -3deg; animation-delay: .15s; }}
.xolo-papel span:nth-child(3n)   {{ -webkit-mask-image: url("{_B['rombos']}"); mask-image: url("{_B['rombos']}"); --giro: 5deg; animation-delay: .3s; }}
@keyframes xolo-asentar {{
  0%   {{ transform: rotate(var(--giro, 4deg)); }}
  28%  {{ transform: rotate(calc(var(--giro, 4deg) * -.55)); }}
  52%  {{ transform: rotate(calc(var(--giro, 4deg) * .3)); }}
  74%  {{ transform: rotate(calc(var(--giro, 4deg) * -.12)); }}
  100% {{ transform: rotate(0deg); }}
}}
@media (prefers-reduced-motion: reduce) {{ .xolo-papel span {{ animation: none; }} }}

/* Título y bajada */
.xolo-titulo {{
  margin: 0 0 8.8px; padding: 0;
  font-family: {FUENTE_TITULO}; font-weight: 400;
  font-size: clamp(36.8px, 25.6px + 3.4vw, 56px); line-height: 1.02; letter-spacing: -.005em;
  color: {TINTA}; text-wrap: balance;
}}
.xolo-bajada {{ margin: 0 0 4px; max-width: 576px; font-size: 18px; line-height: 1.5; color: {TINTA}; }}

/* Mensajes: Xolo sin caja y con su flor; la persona en burbuja morada a la derecha */
[data-testid="stChatMessage"] {{ background: transparent; padding: 0; gap: 11.2px; }}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {{ font-size: 17px; line-height: 1.55; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
  width: fit-content; max-width: min(85%, 480px); margin-left: auto;
  padding: 9.6px 16px 10.4px;
  background: {MORADO};
  border-radius: 18.4px 18.4px 4.8px 18.4px;
}}
[data-testid="stChatMessageAvatarUser"] {{ display: none; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {{ color: {SOBRE_MORADO}; }}
[data-testid="stChatMessage"] img {{ width: 24px; height: 24px; margin-top: 2px; border: 0; border-radius: 0; background: none; }}

/* Preguntas sugeridas: una lista con líneas, no botones */
.st-key-sugerencias {{ gap: 0; border-bottom: 1px solid {LINEA}; }}
.st-key-sugerencias [data-testid="stCaptionContainer"] {{ margin: -4px 0 -14px; opacity: 1; }}
.st-key-sugerencias [data-testid="stCaptionContainer"] p {{ font-size: 15.2px; font-style: italic; color: {TINTA_SUAVE}; }}
.st-key-sugerencias button {{
  width: 100%; min-height: 0; justify-content: flex-start;
  padding: 9.9px 0; border: 0; border-top: 1px solid {LINEA}; border-radius: 0;
  background: none; color: {ENLACE}; text-align: left;
}}
.st-key-sugerencias button > div {{ justify-content: flex-start; }}
.st-key-sugerencias button p {{ font-size: 17px; font-weight: 500; line-height: 1.55; }}
.st-key-sugerencias button:hover, .st-key-sugerencias button:focus {{ color: {TINTA}; background: none; }}

/* Pie fijo: caja de escritura, botón Enviar y la fila de abajo */
[data-testid="stBottom"] > div {{ background: {PAPEL}; border-top: 1px solid {LINEA}; }}
[data-testid="stBottomBlockContainer"] {{ max-width: 688px; padding: 12.8px 20px 8.8px; }}
[data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"] {{ gap: 4.8px; }}
[data-testid="stChatInput"] > div {{ background: transparent; border: 0; border-radius: 0; padding: 0; box-shadow: none; }}
[data-testid="stChatInput"] > div > div {{ gap: 0; align-items: flex-end; }}
[data-testid="stChatInput"] > div > div > div:first-child {{
  flex: 1 1 auto; min-width: 0;
  padding: 7.5px 14.4px;
  background: {SUPERFICIE}; border: 1.5px solid {LINEA}; border-radius: 14.4px;
}}
[data-testid="stChatInput"] > div > div > div:first-child:focus-within {{ border-color: {ENLACE}; outline: 2px solid {ENLACE}; outline-offset: 0; }}
[data-testid="stChatInputTextArea"] {{ font-size: 17px; line-height: 1.4; color: {TINTA}; caret-color: {TINTA}; }}
[data-testid="stChatInputTextArea"]::placeholder {{ color: {TINTA_SUAVE}; opacity: 1; }}
[data-testid="stChatInput"] > div > div > div:has(> [data-testid="stChatInputSubmitButton"]) {{ width: auto; height: auto; margin-left: 9.6px; }}
[data-testid="stChatInputSubmitButton"] {{
  width: auto; min-width: 97.6px; height: auto; min-height: 47.2px; padding: 0 18.4px;
  background: {CEMPASUCHIL}; color: {SOBRE_CEMPASUCHIL};
  border: 1.5px solid transparent; border-radius: 14.4px;
}}
[data-testid="stChatInputSubmitButton"] svg {{ display: none; }}
[data-testid="stChatInputSubmitButton"]::after {{ content: "Enviar"; font-size: 17px; font-weight: 700; line-height: 1; }}
[data-testid="stChatInputSubmitButton"]:disabled {{ background: {CEMPASUCHIL}; color: {SOBRE_CEMPASUCHIL}; opacity: .5; }}
[data-testid="stChatInputSubmitButton"]:hover:not(:disabled) {{ background: {CEMPASUCHIL}; color: {SOBRE_CEMPASUCHIL}; filter: brightness(1.07); }}
#stChatInputInstructions, [data-testid="InputInstructions"] {{ display: none; }}

.st-key-pie {{ gap: 0 22px; }}
.st-key-pie [data-testid="stCaptionContainer"] {{ opacity: 1; text-align: right; }}
.st-key-pie [data-testid="stCaptionContainer"] p {{ font-size: 15.2px; color: {TINTA_SUAVE}; }}
.st-key-nueva button {{
  min-height: 0; padding: 5.6px 0; border: 0; background: none;
  color: {ENLACE}; text-decoration: underline; text-decoration-thickness: 1.5px; text-underline-offset: .18em;
}}
.st-key-nueva button p {{ font-size: 15.2px; font-weight: 700; }}
.st-key-nueva button:hover, .st-key-nueva button:focus {{ color: {ENLACE}; text-decoration-color: {CEMPASUCHIL}; background: none; }}
"""


def aplicar() -> None:
    """Inyecta el CSS y la tira de papel picado. Se llama una vez, al inicio de app.py."""
    st.html(f"<style>{CSS}</style>")
    st.html('<div class="xolo-papel" aria-hidden="true">' + "<span></span>" * 32 + "</div>")


def encabezado(titulo: str, bajada: str) -> None:
    st.html(f'<h1 class="xolo-titulo">{titulo}</h1><p class="xolo-bajada">{bajada}</p>')
