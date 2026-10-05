# Xolo, chatbot de Día de Muertos

Chatbot de un tema hecho con la API de Claude. Responde con base en `instrucciones.txt` y en los documentos de la carpeta `conocimiento/`.

## Qué hay en la carpeta

| Archivo | Para qué sirve |
|---|---|
| `app.py` | Versión web (Streamlit). Es la que usa una persona externa. |
| `xolo.py` | Versión de terminal, para probar rápido. |
| `estilo.py` | El aspecto de la versión web: papel picado, tipografía, colores y burbujas. |
| `xolo_base.py` | Lo que comparten las dos: modelo, instrucciones y documentos. |
| `instrucciones.txt` | Rol, tema, tono y reglas del bot. |
| `conocimiento/` | Documentos de referencia: `.docx`, `.md` o `.txt`. |
| `requirements.txt` | Dependencias. |

## Correrlo en tu computadora

```bash
export ANTHROPIC_API_KEY="tu-clave"

# Versión web: abre http://localhost:8501
uv run --with-requirements requirements.txt streamlit run app.py

# Versión de terminal
uv run xolo.py
```

Para una demo en vivo sin publicar nada: al arrancar la versión web, Streamlit imprime una "Network URL". Quien esté en la misma red wifi puede abrirla desde su celular o laptop, si la red lo permite.

## Cambiar el aspecto

La versión web copia el tema oscuro del prototipo y es fija: no cambia con el modo claro u oscuro de quien la visita. Los colores y estilos están en `estilo.py`; la tipografía y el tema base, en `.streamlit/config.toml`. Los textos (título, saludo, preguntas sugeridas) están al inicio de `app.py`. Si cambias `config.toml`, reinicia la app.

El estilo depende de nombres internos de Streamlit, por eso `requirements.txt` fija su versión. Si la actualizas, revisa que la página se siga viendo bien.

## Agregarle información

1. Copia el archivo a `conocimiento/`. Acepta Word (`.docx`), Markdown (`.md`) y texto (`.txt`). Un PDF hay que pasarlo antes a uno de esos formatos.
2. En la versión web basta recargar la página; la terminal hay que reiniciarla. La terminal muestra al arrancar la lista de documentos cargados.

Todo lo que hay en la carpeta se manda al modelo en cada mensaje. Eso funciona bien hasta unos cientos de páginas; `xolo_base.py` avisa si te pasas. Con más material hay que cambiar a recuperación por fragmentos (RAG).

Si un documento y las notas de `instrucciones.txt` se contradicen, el bot sigue al documento.

## Publicarlo para que cualquiera lo use

Con Streamlit Community Cloud, que es gratis, queda una dirección `https://....streamlit.app` que se abre desde cualquier navegador sin crear cuenta.

1. Sube esta carpeta a un repositorio de GitHub. Puede ser privado; en ese caso Streamlit te pedirá permiso para leerlo. El `.gitignore` ya evita subir claves.
2. Entra a share.streamlit.io con tu cuenta de GitHub y elige "Create app". Indica el repositorio, la rama y el archivo `app.py`.
3. En "Advanced settings", pega esto en "Secrets" con tu clave:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Despliega y comparte la dirección.

Si nadie la abre en 12 horas, la app se duerme. Quien llegue después la despierta con un botón y tarda un momento en arrancar.

Para cambiar documentos o instrucciones en la versión publicada, sube el cambio a GitHub. Si no lo ves reflejado, reinicia la app desde "Manage app".

## Costo y cuidado del saldo

- Las respuestas de la versión web y de la terminal se pagan con tu clave, sin importar quién pregunte.
- La API funciona con créditos prepagados. Si cargas poco y dejas apagada la recarga automática, lo más que puedes gastar es lo que cargaste.
- Con el modelo actual (Haiku 4.5) la entrada cuesta 1 USD por millón de tokens y la salida 5 USD. El documento incluido son unos 25 a 30 mil tokens (estimación), o sea cerca de 3 centavos de dólar por mensaje si se manda como texto nuevo.
- Para bajar ese costo, los documentos van con caché: la primera pregunta los escribe en caché (1.25 USD por millón) y las siguientes los leen (0.10 USD por millón), siempre que no pasen más de 5 minutos entre mensajes.
- En la terminal, el comando `/tokens` muestra cuántos tokens de la última respuesta se leyeron de caché. Úsalo para confirmar que la caché funciona con tu clave.
- `MAX_PREGUNTAS` en `app.py` limita las preguntas por sesión del navegador.

## Si algo falla

- "Falta la clave": no está definida `ANTHROPIC_API_KEY` (o el Secret en la versión publicada).
- Error 400 con saldo insuficiente: hay que cargar créditos en platform.claude.com.
- Error 404 de modelo: el modelo se retiró. Cambia `MODELO` en `xolo_base.py` por uno vigente.
