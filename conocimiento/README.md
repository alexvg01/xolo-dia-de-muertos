# Fuentes de conocimiento de Xolo

Xolo responde a partir de cuatro fuentes, en este orden de prioridad.

| # | Fuente | Dónde está | Qué aporta |
|---|---|---|---|
| 1 | Documento base | [`DIA_DE_MUERTOS.docx`](DIA_DE_MUERTOS.docx) | El contenido principal: historia, ofrenda, calendario de ánimas, la Catrina y el cine. |
| 2 | Notas de referencia | [`notas_de_referencia.md`](notas_de_referencia.md) | Datos breves que el documento base no cubre, cada uno con su fuente. |
| 3 | Tradiciones por región | [`tradiciones_por_region.md`](tradiciones_por_region.md) | Cómo se vive la fiesta en distintos estados, incluido el norte del país, con la fuente de cada dato. |
| 4 | Conocimiento general del modelo | No es un archivo | Lo que el modelo de lenguaje aprendió en su entrenamiento. Solo se usa cuando la respuesta no está en las fuentes 1 a 3. |

## 1. Documento base

- **Archivo:** `DIA_DE_MUERTOS.docx`, 14 páginas y unas 13,500 palabras.
- **Referencia bibliográfica:** pendiente de completar (autor, título, editorial y año de la obra de la que se tomó el texto).
- **Estado del texto:** es un texto digitalizado y conserva erratas de escaneo. Xolo tiene la instrucción de interpretarlas por contexto.

Temas que cubre:

- Las fiestas de los muertos entre los nahuas y los destinos del alma.
- El Día de Muertos después de la Conquista y en el siglo XIX.
- El altar y los objetos de la ofrenda: copal, cempasúchil, agua, sal, pan, bebidas, retrato y calaverita de azúcar.
- El calendario de los muertos: qué ánimas llegan cada día.
- La celebración pública.
- De la Calavera garbancera a la Catrina.
- El Día de Muertos en el cine.
- Cronología.
- Guía para montar un altar.

## 2. Notas de referencia

Son datos breves redactados para este proyecto a partir de las fuentes siguientes, consultadas el 5 de octubre de 2026. En `notas_de_referencia.md` cada nota trae el enlace a su fuente.

| Tema | Fuentes |
|---|---|
| Reconocimiento de la UNESCO | UNESCO, Patrimonio Cultural Inmaterial |
| Elementos de la ofrenda | Instituto Nacional de los Pueblos Indígenas (INPI) |
| Niveles de la ofrenda | IMER Noticias |
| La Catrina | INBAL e INAH |
| Calaveritas literarias | National Geographic en Español; El Informador, que cita a la Casa Universitaria del Libro de la UNAM |
| Desfile de la Ciudad de México | El Financiero y Milenio |
| Alebrijes | UNAM (CEPE, revista Flores de Nieve) e Infobae |

## 3. Tradiciones por región

Reúne lo que se pudo documentar de cada estado o región, con el enlace a la fuente en cada apartado de `tradiciones_por_region.md`. Fuentes consultadas el 5 y el 6 de octubre de 2026. No cubre todos los estados.

| Región | Fuentes |
|---|---|
| Panorama del norte y la frontera | EFE, con un investigador de El Colegio de la Frontera Norte; Monterrey Secreto |
| Nuevo León | Monterrey Secreto, Publimetro, Posta y EFE |
| Tamaulipas | Milenio y Lifeder |
| Chihuahua | Luz Noticias y comunicados del Gobierno del Estado de Chihuahua |
| La Huasteca (Xantolo) | Matador Network, Milenio, Posta y la revista Plasticidad y Restauración Neurológica |
| Oaxaca | El Financiero |
| Puebla (Huaquechula) | EFE |
| Aguascalientes y Estado de México | Chilango |
| Ciudad de México (Mixquic) | El Diario |
| Michoacán, Yucatán y Campeche | Milenio y El Universal |

## 4. Conocimiento general del modelo

Xolo funciona sobre un modelo de lenguaje, Claude Haiku 4.5, de Anthropic. Cuando una pregunta no se responde con las fuentes 1 a 3, el modelo contesta con lo que aprendió en su entrenamiento y aclara que ese dato no viene de sus documentos. Esa parte no tiene una fuente que se pueda citar, y por eso las instrucciones le piden cautela: decir cuando algo varía entre regiones, no inventar fechas ni programas de eventos y reconocer lo que no sabe.

## Lo que Xolo no usa

No busca en internet ni consulta archivos fuera de esta carpeta.

## Cómo se combinan

En cada mensaje se envían al modelo las instrucciones (`instrucciones.txt`), los archivos de esta carpeta y la conversación. Si el documento base y las notas difieren, Xolo sigue al documento base. Si le preguntan de dónde sale un dato, debe decir de cuál de las fuentes viene.

## Cómo agregar una fuente

Copia el archivo a esta carpeta, en formato `.docx`, `.md` o `.txt`, y agrégalo a la tabla de arriba. Este `README.md` es solo para quien visita el repositorio; no se le envía al modelo.
