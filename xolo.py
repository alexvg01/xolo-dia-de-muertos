# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=1.11,<2", "python-docx>=1.2,<2"]
# ///
"""Xolo en la terminal: chatbot de Día de Muertos con la API de Claude.

Uso:
    export ANTHROPIC_API_KEY="tu-clave"
    uv run xolo.py

Las instrucciones viven en instrucciones.txt y los documentos de referencia en
la carpeta conocimiento/. Cambia esos archivos y cambia el chatbot; el código no se toca.
"""

from __future__ import annotations

import os
import sys

import anthropic

from xolo_base import MAX_TOKENS, MODELO, ErrorDeConfiguracion, armar_sistema, detalle, recientes

try:
    import readline  # noqa: F401  (da flechas e historial a input() en macOS y Linux)
except ImportError:
    pass


def responder(cliente: anthropic.Anthropic, sistema: list[dict], historial: list[dict]):
    """Pide la respuesta, la imprime conforme llega y devuelve (texto, uso de tokens).

    Ctrl+C detiene la respuesta; se devuelve lo que alcanzó a llegar.
    """
    partes: list[str] = []
    uso = None
    try:
        with cliente.messages.stream(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=sistema,                  # instrucciones + documentos
            messages=recientes(historial),   # la API no guarda memoria: va el historial cada vez
        ) as stream:
            for fragmento in stream.text_stream:
                print(fragmento, end="", flush=True)
                partes.append(fragmento)
            final = stream.get_final_message()
        uso = final.usage
        print()
        if not "".join(partes).strip():
            print("[No llegó respuesta. Escribe la pregunta de otra forma.]")
        elif final.stop_reason == "max_tokens":
            print("[La respuesta se cortó por longitud. Pide la parte que falta.]")
    except KeyboardInterrupt:
        print("\n[Respuesta detenida]")
    return "".join(partes), uso


def resumen_de_uso(uso) -> str:
    if uso is None:
        return "Todavía no hay una respuesta completa que medir."
    leidos = getattr(uso, "cache_read_input_tokens", None) or 0
    escritos = getattr(uso, "cache_creation_input_tokens", None) or 0
    return (
        f"Entrada: {uso.input_tokens} tokens nuevos, {leidos} leídos de caché, {escritos} escritos en caché. "
        f"Salida: {uso.output_tokens} tokens."
    )


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit('Falta la variable ANTHROPIC_API_KEY. Defínela con: export ANTHROPIC_API_KEY="tu-clave"')
    try:
        sistema, documentos = armar_sistema()
    except ErrorDeConfiguracion as error:
        sys.exit(str(error))
    cliente = anthropic.Anthropic()   # toma la clave de ANTHROPIC_API_KEY
    historial: list[dict] = []        # [{"role": "user" | "assistant", "content": "..."}]
    ultimo_uso = None

    print("Xolo, guía de Día de Muertos. Escribe tu pregunta.")
    print("Documentos cargados: " + (", ".join(documentos) if documentos else "ninguno (carpeta conocimiento/ vacía)"))
    print("Comandos: /nueva, /tokens, /salir. Ctrl+C detiene una respuesta.")

    while True:
        try:
            pregunta = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not pregunta:
            continue
        if pregunta == "/salir":
            break
        if pregunta == "/nueva":
            historial.clear()
            print("Conversación nueva.")
            continue
        if pregunta == "/tokens":
            print(resumen_de_uso(ultimo_uso))
            continue

        historial.append({"role": "user", "content": pregunta})
        print("\nXolo: ", end="", flush=True)
        try:
            respuesta, uso = responder(cliente, sistema, historial)
            ultimo_uso = uso or ultimo_uso
        except anthropic.AuthenticationError:
            sys.exit("\nLa API rechazó la clave. Revisa el valor de ANTHROPIC_API_KEY.")
        except anthropic.RateLimitError:
            respuesta = ""
            print("\n[Se alcanzó el límite de uso. Espera un momento y vuelve a preguntar.]")
        except anthropic.APIConnectionError:
            respuesta = ""
            print("\n[No hubo conexión con la API. Revisa tu red y vuelve a preguntar.]")
        except anthropic.APIStatusError as error:
            respuesta = ""
            print(f"\n[La API respondió con un error {error.status_code}: {detalle(error)}]")

        if respuesta.strip():
            historial.append({"role": "assistant", "content": respuesta.rstrip()})
        else:
            historial.pop()   # sin respuesta, la pregunta no se queda en el historial


if __name__ == "__main__":
    main()
