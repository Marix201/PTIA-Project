# Fuentes del diseño

| Fuente | Qué es | Cómo se usó |
| --- | --- | --- |
| `docs/diseno/Mock-up_original.pdf` | Mock-up realizado en el hito 1 de 5 pantallas estáticas | Punto de partida: mismas pantallas, campos y orden |
| `docs/diseno/prototipo_navegable.html` | Prototipo de interfaz navegable, un solo archivo HTML | Entregable de prototipo de interfaz del Hito 2.|
| `docs/diseno/prototipo_Main.dc.html` y `prototipo_canvas.json` | Archivos fuente con la que se generó el prototipo. No se abren por sí solos; el entregable es `prototipo_navegable.html` | Solo referencia |
| `data/DICCIONARIO.md` | Diccionario de variables | Los campos y valores de las pantallas Perfil y Registro son los mismos que usa la API |
| Documento Astraea PTIA, Hito 1 | Problema, justificación y referencias | Texto de la pantalla "Conoce tu cuerpo" (De Corte et al., 2025; de Kok et al., 2025) |
| Tipografía Figtree (Google Fonts) | Tipo de letra del prototipo | Texto de toda la interfaz |

## Cambios respecto al mock-up

- Pantalla de bienvenida con aviso de que no es un diagnóstico y casilla de consentimiento.
- Barra de navegación inferior entre Perfil, Aprende, Registro y Resultados.
- Escala de dolor completa de 0 a 10 (el mock-up la mostraba cortada en 8).
- Resultados con dos compatibilidades independientes (68 % y 41 % son un ejemplo), en lugar de 68 % y 32 %, que sumaban 100 %.
- Contenido para las tarjetas vacías: "Conoce tu cuerpo", "Patrones detectados" y vista previa del reporte.
- Texto gris con más contraste sobre el fondo oscuro; controles de al menos 44 px.
- Validación de edad (18 a 55) y de primera menstruación (8 a 18), y avisos al guardar.

## Lo real y lo simulado en el prototipo

- Real: navegación, campos que responden y validan, tarjetas que se abren, contador de registros guardados.
- Simulado: el resultado (valores fijos de ejemplo), las sugerencias de estudios y la descarga del reporte.
  La conexión con la API de este repositorio queda para el Hito 3.

