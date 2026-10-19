"""Visita la app de Xolo para que Streamlit no la duerma; si ya está dormida, la despierta.

Lo corre GitHub Actions cada pocas horas (ver .github/workflows/mantener-despierta.yml).
Solo abre la página, como lo haría una persona: no le pregunta nada a Xolo,
así que no gasta créditos de la API.
"""

from __future__ import annotations

import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = os.environ.get("XOLO_URL", "https://xolo-dia-de-muertos.streamlit.app/")

# Texto del botón que Streamlit muestra en la pantalla de "app dormida".
BOTON_DESPERTAR = re.compile("get this app back up", re.IGNORECASE)
# La caja de escribir de Xolo: solo existe cuando la app ya terminó de cargar.
APP_CARGADA = '[data-testid="stChatInput"]'

ESPERA_INICIAL = 60       # segundos para saber si está despierta o dormida
ESPERA_AL_DESPERTAR = 300 # segundos que puede tardar en arrancar después del clic
RECARGA_CADA = 60         # mientras arranca, cada cuánto se recarga la página
ESTANCIA = 15             # segundos que se queda en la app ya cargada


def app_cargada(pagina) -> bool:
    """La app vive dentro de un marco (iframe) de la página de Streamlit: se busca en todos."""
    for marco in pagina.frames:
        try:
            if marco.locator(APP_CARGADA).count() > 0:
                return True
        except Exception:
            pass  # el marco cambió mientras se revisaba; se vuelve a intentar en la siguiente vuelta
    return False


def boton_despertar(pagina):
    for marco in pagina.frames:
        try:
            boton = marco.get_by_role("button", name=BOTON_DESPERTAR).first
            if boton.count() > 0 and boton.is_visible():
                return boton
        except Exception:
            pass
    return None


def texto_visible(pagina) -> str:
    """Lo que se alcanza a leer en la página; sirve para entender una falla desde el registro."""
    partes = []
    for marco in pagina.frames:
        try:
            texto = " ".join(marco.locator("body").inner_text(timeout=2000).split())
        except Exception:
            continue
        if texto:
            partes.append(texto[:300])
    return " | ".join(partes) or "(página en blanco)"


def main() -> int:
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        print(f"Visitando {URL}")
        pagina.goto(URL, wait_until="domcontentloaded", timeout=60_000)

        # 1. ¿Despierta o dormida?
        boton = None
        limite = time.monotonic() + ESPERA_INICIAL
        while time.monotonic() < limite and not app_cargada(pagina):
            boton = boton_despertar(pagina)
            if boton:
                break
            pagina.wait_for_timeout(1000)

        if boton is None and not app_cargada(pagina):
            print(f"FALLA: en {ESPERA_INICIAL} segundos la app no cargó ni apareció el botón para despertarla.")
            print("En la página se lee:", texto_visible(pagina))
            return 1

        # 2. Si estaba dormida, se despierta y se espera a que arranque.
        if boton is None:
            print("La app ya estaba despierta.")
        else:
            print("La app estaba dormida: se le da clic al botón para despertarla.")
            boton.click()
            limite = time.monotonic() + ESPERA_AL_DESPERTAR
            recarga = time.monotonic() + RECARGA_CADA
            while time.monotonic() < limite and not app_cargada(pagina):
                pagina.wait_for_timeout(2000)
                if time.monotonic() >= recarga:
                    # Por si la página no avanza sola al terminar de arrancar.
                    pagina.reload(wait_until="domcontentloaded", timeout=60_000)
                    pagina.wait_for_timeout(5000)
                    otro = boton_despertar(pagina)
                    if otro and not app_cargada(pagina):
                        otro.click()
                    recarga = time.monotonic() + RECARGA_CADA
            if not app_cargada(pagina):
                print(f"FALLA: se pidió despertarla, pero no terminó de arrancar en {ESPERA_AL_DESPERTAR} segundos.")
                print("En la página se lee:", texto_visible(pagina))
                return 1
            print("La app despertó y ya cargó.")

        # 3. Se queda un momento, como una visita normal.
        pagina.wait_for_timeout(ESTANCIA * 1000)
        navegador.close()
    print("Listo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
