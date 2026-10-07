"""Lo que comparten xolo.py (terminal) y app.py (web): modelo, instrucciones y documentos."""

from __future__ import annotations

from pathlib import Path

import anthropic

# El modelo más rápido y barato. "claude-sonnet-5-5" razona mejor y cuesta el doble por token.
MODELO = "claude-haiku-4-5-20251001"
MAX_TOKENS = 2048    # tope de tokens de cada respuesta
MAX_MENSAJES = 24    # cuántos mensajes recientes se reenvían en cada llamada

RAIZ = Path(__file__).parent
INSTRUCCIONES = RAIZ / "instrucciones.txt"
CONOCIMIENTO = RAIZ / "conocimiento"   # documentos de referencia: .docx, .md o .txt
EXTENSIONES = {".docx", ".md", ".txt"}
LIMITE_CARACTERES = 500_000            # más que esto ya no conviene mandarlo completo en cada mensaje


class ErrorDeConfiguracion(Exception):
    """Falta algo para arrancar: las instrucciones, un documento ilegible, etc."""


def cargar_instrucciones() -> str:
    try:
        texto = INSTRUCCIONES.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise ErrorDeConfiguracion(f"No encuentro {INSTRUCCIONES.name}. Debe estar junto a xolo_base.py.") from None
    if not texto:
        raise ErrorDeConfiguracion(f"{INSTRUCCIONES.name} está vacío: sin instrucciones no hay chatbot de un tema.")
    return texto


def leer_docx(ruta: Path) -> str:
    """Texto de un Word: párrafos y tablas en orden, con los títulos marcados."""
    from docx import Document          # paquete python-docx
    from docx.table import Table

    partes = []
    for elemento in Document(str(ruta)).iter_inner_content():
        if isinstance(elemento, Table):
            for fila in elemento.rows:
                celdas = [celda.text.strip() for celda in fila.cells]
                if any(celdas):
                    partes.append(" | ".join(celdas))
            continue
        texto = elemento.text.strip()
        if not texto:
            continue
        estilo = (elemento.style.name or "").lower() if elemento.style is not None else ""
        es_titulo = estilo.startswith(("heading", "título", "titulo", "title")) and len(texto) <= 120
        partes.append(f"## {texto}" if es_titulo else texto)
    return "\n\n".join(partes)


def cargar_conocimiento() -> list[tuple[str, str]]:
    """(nombre, texto) de cada documento de la carpeta conocimiento/, en orden alfabético."""
    if not CONOCIMIENTO.is_dir():
        return []
    documentos = []
    for ruta in sorted(CONOCIMIENTO.iterdir(), key=lambda r: r.name.lower()):
        # Se saltan archivos ocultos, los temporales que Word crea mientras el documento está abierto
        # y el README de la carpeta, que es la lista de fuentes para quien visita el repositorio.
        if ruta.name.startswith((".", "~$")) or ruta.suffix.lower() not in EXTENSIONES:
            continue
        if ruta.name.lower() == "readme.md":
            continue
        try:
            texto = leer_docx(ruta) if ruta.suffix.lower() == ".docx" else ruta.read_text(encoding="utf-8").strip()
        except Exception as error:
            raise ErrorDeConfiguracion(f"No pude leer conocimiento/{ruta.name}: {error}") from error
        if texto:
            documentos.append((ruta.name, texto))
    return documentos


def armar_sistema() -> tuple[list[dict], list[str]]:
    """Bloques para el parámetro `system` y los nombres de los documentos cargados.

    Primero van las instrucciones y después los documentos completos. El último
    bloque lleva cache_control: la API guarda ese prefijo unos minutos y, mientras
    siga en caché, releerlo cuesta la décima parte que mandarlo como texto nuevo.
    """
    bloques: list[dict] = [{"type": "text", "text": cargar_instrucciones()}]
    documentos = cargar_conocimiento()
    if documentos:
        total = sum(len(texto) for _, texto in documentos)
        if total > LIMITE_CARACTERES:
            raise ErrorDeConfiguracion(
                f"Los documentos de conocimiento/ suman {total:,} caracteres. Es demasiado para mandarlo "
                "completo en cada mensaje: quita documentos o cambia a recuperación por fragmentos (RAG)."
            )
        cuerpo = "\n\n".join(
            f'<documento nombre="{nombre}">\n{texto}\n</documento>' for nombre, texto in documentos
        )
        bloques.append({
            "type": "text",
            "text": "DOCUMENTOS DE REFERENCIA\n\n" + cuerpo,
            "cache_control": {"type": "ephemeral"},
        })
    return bloques, [nombre for nombre, _ in documentos]


def huella() -> tuple:
    """Cambia cuando cambian las instrucciones o los documentos. La versión web la usa para recargarlos."""
    rutas = [INSTRUCCIONES] + (sorted(CONOCIMIENTO.iterdir()) if CONOCIMIENTO.is_dir() else [])
    return tuple((r.name, r.stat().st_mtime_ns, r.stat().st_size) for r in rutas if r.is_file())


def recientes(historial: list[dict]) -> list[dict]:
    """Los últimos mensajes de la conversación, empezando siempre por uno del usuario."""
    ventana = historial[-MAX_MENSAJES:]
    while ventana and ventana[0]["role"] != "user":
        ventana = ventana[1:]
    return ventana


def detalle(error: anthropic.APIStatusError) -> str:
    """El mensaje que envía la API dentro del error, si viene; si no, el del SDK."""
    cuerpo = error.body
    if isinstance(cuerpo, dict) and isinstance(cuerpo.get("error"), dict):
        return str(cuerpo["error"].get("message") or error.message)
    return error.message
