# Fuentes del diseño

| Fuente | Qué es | Cómo se usó |
| --- | --- | --- |
| `docs/diseno/Mock-up_original.pdf` | Mock-up realizado en el hito 1 de 5 pantallas estáticas | Punto de partida: mismas pantallas, campos y orden |
| `docs/diseno/prototipo_navegable.html` | Prototipo de interfaz navegable, un solo archivo HTML | Entregable de prototipo de interfaz del Hito 2 |
| `docs/diseno/prototipo_Main.dc.html` y `prototipo_canvas.json` | Archivos fuente con la que se generó el prototipo. No se abren por sí solos; el entregable es `prototipo_navegable.html` | Solo referencia |
| `web/index.html` | Interfaz del Hito 3, servida por la API en `/app` | Parte del prototipo navegable, ahora conectada a `POST /evaluar` |
| `data/DICCIONARIO.md` | Diccionario de variables | Los campos y valores de las pantallas Perfil y Registro son los mismos que usa la API |
| Documento Astraea PTIA, Hito 1 | Problema, justificación y referencias | Texto de la pantalla "Conoce tu cuerpo" (De Corte et al., 2025; de Kok et al., 2025) |
| Tipografía Figtree (Google Fonts) | Tipo de letra del prototipo | Texto de toda la interfaz |
| `docs/arquitectura.md` y `docs/figuras/arquitectura.png` | Diagrama de arquitectura y mapa de componentes con enlaces a cada archivo | Figura del documento; resume el flujo de la interfaz a la API, las tres capas del servicio y la respuesta JSON |
| Kupec et al. (2025), J Clin Med, 175 mujeres con endometriosis (acceso abierto, CC BY 4.0) | Estudio con estadísticos descriptivos publicados | Comparación descriptiva con el grupo con endometriosis de los datos sintéticos (`docs/comparacion_datos_reales.md`). No se usó para entrenar ni para medir el desempeño del modelo |
| `docs/casos_de_prueba.md` | Dos casos de punta a punta con pacientes simuladas y un caso de validación | Sección 7: secuencia de entradas, salida esperada y salida lograda |

## Cambios respecto al mock-up

- Pantalla de bienvenida con aviso de que no es un diagnóstico y casilla de consentimiento.
- Barra de navegación inferior entre Perfil, Aprende, Registro y Resultados.
- Escala de dolor completa de 0 a 10 (el mock-up la mostraba cortada en 8).
- Resultados con dos compatibilidades independientes (68 % y 41 % son un ejemplo), en lugar de 68 % y 32 %, que sumaban 100 %.
- Contenido para las tarjetas vacías: "Conoce tu cuerpo", "Patrones detectados" y vista previa del reporte.
- Texto gris con más contraste sobre el fondo oscuro; controles de al menos 44 px.
- Validación de edad (18 a 55) y de primera menstruación (8 a 18), y avisos al guardar.

## Cambios del Hito 3 (MVP)

- La interfaz ya no usa valores fijos: envía el perfil y el registro a `POST /evaluar` y muestra la respuesta del modelo.
- La API sirve la interfaz en `/app`, de modo que se abre desde el mismo servidor.
- Se agregó un botón para cargar días de ejemplo y poder probar el flujo sin registrar cada día a mano.
- Las sugerencias de estudios y los patrones detectados salen de la respuesta de la API.

## Lo real y lo simulado

- Real: navegación, campos que responden y validan, tarjetas que se abren, contador de registros guardados, y el resultado, los patrones y las sugerencias de estudios, calculados por el modelo a través de la API.
- Simulado: los datos. El modelo se entrenó con datos sintéticos, y los días de ejemplo de la interfaz también son simulados; no hay pacientes reales en el sistema.
- Limitación: la comparación con Kupec et al. es descriptiva. Muestra si los supuestos del generador se parecen a lo publicado (dolor máximo y dismenorrea coinciden; la dispareunia sintética, 89 %, supera a la publicada, 38 %), no valida el modelo con pacientes reales.
