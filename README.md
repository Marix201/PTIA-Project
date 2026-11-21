# Astraea

Tamizaje temprano de endometriosis y adenomiosis a partir de síntomas reportados por una usuaria. Dada una paciente con un perfil y un registro diario de síntomas, se estima si presenta alguna de las enfermedades, se explican los factores principales y se sugieren estudios para llevar a consulta.

Estado: **Hito 3, MVP funcional.** Funciona de extremo a extremo con datos sintéticos: interfaz web, API, modelo y reporte en PDF.
Las secciones 5 y 6 del documento (alcance y diseño metodológico) describen este código.

## Estado del proyecto

| Parte | Estado |
| --- | --- |
| Diccionario de variables (`data/DICCIONARIO.md`, `schema.py`) | Hecho |
| Generador de datos sintéticos (`synthetic.py`) | Hecho |
| Extracción de variables desde el registro diario (`features.py`) | Hecho, con pruebas |
| Línea base: 4 familias de modelos, validación cruzada, calibración, umbral por sensibilidad para cada salida | Hecho |
| Regla combinada de alerta (tres umbrales) con matrices de confusión y curvas de calibración | Hecho |
| Explicación por oclusión y reglas de recomendación (`explain.py`, `rules.py`) | Hecho (reglas pendientes de revisión clínica) |
| API: `POST /evaluar`, `POST /reporte` (PDF) y `GET /salud` | Hecho |
| Interfaz web conectada a la API (`web/index.html`, se abre en `/app`) | Hecho |
| Reporte descargable en PDF (`reporte.py`, ReportLab) | Hecho |
| Comparación descriptiva con datos publicados (Kupec et al., 2025) | Hecho (`docs/comparacion_datos_reales.md`) |
| Casos de prueba de punta a punta | Hecho (`docs/casos_de_prueba.md`) |
| Datos reales con registro diario (KI EndoLIST) | No se usó: requiere un acuerdo de uso con tiempos incompatibles con el cronograma. Queda como trabajo futuro |
| SHAP en lugar de la explicación por oclusión | Trabajo futuro |

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

El código vive en la carpeta `astraea/`, así que los comandos se ejecutan desde ahí (con el entorno virtual activado):

```bash
cd astraea
python scripts/generar_datos.py 2000 42   # crea data/sintetico.csv
python scripts/entrenar.py                # entrena, guarda models/modelo.joblib, models/metricas.json y docs/resultados_preliminares.md
python scripts/figuras_metricas.py        # matrices de confusión y calibración en docs/figuras/
python scripts/demo_evaluar.py endo 7     # evalúa una paciente simulada (otra | endo | adeno | ambas)
PYTHONPATH=src uvicorn api.main:app --reload   # API en http://127.0.0.1:8000/docs e interfaz en http://127.0.0.1:8000/
pytest                                    # 36 pruebas
```

En Windows (PowerShell), la línea de la API es:

```powershell
$env:PYTHONPATH = "src"; uvicorn api.main:app --reload
```

`PYTHONPATH=src` hace falta porque el paquete `astraea` no está instalado; los scripts y `pytest` ya agregan `src/` por su cuenta, `uvicorn` no.

`entrenar.py` tarda aproximadamente un minuto. La interfaz carga React y la tipografía desde internet (CDN), así que necesita conexión para verse completa.

Para repetir la comparación con datos publicados (desde `astraea/`):

```bash
python scripts/comparar_datos_reales.py --publicados data/real/publicados.csv --fuente "Kupec et al. 2025 (n=175)"
```

## API

`POST /evaluar` recibe `{"perfil": {...}, "registros": [{...}, ...]}` (mínimo 7 días de registro;
28 o más recomendados) y devuelve:

```json
{
  "alerta": {"nivel": "alta", "puntaje": 0.605},
  "compatibilidad": {"endometriosis": 0.906, "adenomiosis": 0.138},
  "patrones": [{"factor": "dx_infertilidad", "texto": "Antecedente de infertilidad", "peso": 0.371}],
  "estudios_sugeridos": ["ecografia_mapeo_pelvico", "resonancia_magnetica", "valoracion_ginecologica"],
  "aviso": "Este resultado no es un diagnóstico. Un resultado bajo no descarta la enfermedad.",
  "reglas_revisadas_por_profesional": false,
  "entrenado_con_datos_sinteticos": true,
  "version_modelo": "0.1.0"
}
```

Las dos compatibilidades son independientes y no suman 100 %. La API valida rangos y valores
permitidos (responde 422 si no cumplen) y responde 503 si no hay modelo entrenado.

`POST /reporte` recibe la misma solicitud y devuelve el reporte para llevar a consulta como PDF (`reporte_astraea.pdf`).
`GET /salud` indica si el modelo está disponible.

## Estructura

El diagrama de arquitectura y el mapa de componentes con enlaces a cada archivo están en [`astraea/docs/arquitectura.md`](astraea/docs/arquitectura.md).

Las rutas son relativas a `astraea/`. En la raíz del repositorio solo están `README.md`, `requirements.txt`, `pyproject.toml` y `.gitignore`.

```
src/astraea/   schema, features, synthetic, model, explain, rules, servicio, reporte
api/main.py    API FastAPI
web/           interfaz web (index.html)
scripts/       generar_datos, entrenar, figuras_metricas, demo_evaluar, comparar_datos_reales
tests/         features, modelo, reglas, api, reporte
data/          diccionario de variables, conjunto sintético y datos publicados para la comparación
docs/          fuentes de diseño y de código, resultados, casos de prueba, comparación, figuras
models/        modelo entrenado y métricas
```

## Decisiones y límites que hay que tener presentes

- **Los datos son sintéticos.** Los parámetros de `synthetic.py` son supuestos del equipo. Las métricas
  (AUC cercano a 0,95) miden si el pipeline recupera esos supuestos, no la capacidad clínica. Hay que
  decirlo así en el documento y en el video.
- **Umbrales y sensibilidad.** Los umbrales de la señal de alerta, de endometriosis y de adenomiosis se eligen en el entrenamiento
  para una sensibilidad de al menos 0,85. En el conjunto de prueba (n = 400) la sensibilidad es 0,843 para la alerta,
  0,828 para endometriosis y 0,851 para adenomiosis, así que dos de las tres quedan un poco por debajo de la meta. La regla combinada
  llega a 0,926 de sensibilidad y 0,785 de especificidad (`models/metricas.json`).
- **Nivel de alerta.** Es "alta" si el puntaje general o alguna de las dos compatibilidades supera su propio umbral;
  así no aparecen mensajes contradictorios.
- **Reglas de recomendación.** Son un borrador del equipo y siguen sin revisión de una profesional de salud
  ni guías clínicas citadas (`reglas_revisadas_por_profesional` es `false`).
- **Explicación.** Por oclusión (reemplazar cada variable por la mediana y medir cuánto baja la alerta).
  SHAP queda como trabajo futuro.
- **Comparación con datos publicados.** El grupo con endometriosis sintético se comparó con Kupec et al. (2025, 175 mujeres):
  el dolor máximo y la dismenorrea son consistentes, pero la dispareunia sintética (89 %) es mucho mayor que la publicada (38 %).
  Es una validación descriptiva; no se usó para entrenar ni para medir el desempeño.
- **Privacidad.** No se usan datos reales de personas. Si más adelante se usa KI EndoLIST, hay que firmar
  su acuerdo de uso y no intentar reidentificar a nadie.
