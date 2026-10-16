# Astraea

Tamizaje temprano de endometriosis y adenomiosis a partir de síntomas reportados por una usuaria. Dada una paciente con un perfil y un registro diario de síntomas, se estima si presenta alguna de las enfermedades y explica los factores principales, además
sugiere estudios para llevar a consulta.

Estado: **Hito 2, avance de la solución.** Funciona de extremo a extremo con datos sintéticos.
Las secciones 5 y 6 del documento (alcance y diseño metodológico) describen este código.

## estado del proyecto

| Parte | Estado |
| --- | --- |
| Diccionario de variables (`data/DICCIONARIO.md`, `schema.py`) | Hecho |
| Generador de datos sintéticos (`synthetic.py`) | Hecho |
| Extracción de variables desde el registro diario (`features.py`) | Hecho, con pruebas |
| Línea base: 4 familias de modelos, validación cruzada, calibración, umbral por sensibilidad | Hecho |
| Explicación por oclusión y reglas de recomendación (`explain.py`, `rules.py`) | Hecho (reglas pendientes de revisión clínica) |
| API `POST /evaluar` con el contrato JSON de la sección 6e | Hecho |
| Prototipo de interfaz navegable | Hecho (ver `docs/fuentes_diseño.md`) |
| Datos reales (KI EndoLIST) | Pendiente: acceso restringido, requiere solicitud en PhysioNet |
| SHAP, interfaz conectada a la API, reporte PDF real | Hito 3 |

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python scripts/generar_datos.py 2000 42   # crea data/sintetico.csv
python scripts/entrenar.py                # entrena, guarda models/modelo.joblib y docs/RESULTADOS_PRELIMINARES.md
python scripts/demo_evaluar.py endo 7     # evalúa una paciente simulada (otra | endo | adeno | ambas)
uvicorn api.main:app --reload             # API en http://127.0.0.1:8000/docs
pytest                                    # 21 pruebas
```

`entrenar.py` tarda aproximadamente un minuto.

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

## Estructura

```
src/astraea/   schema, features, synthetic, model, explain, rules, servicio
api/main.py    API FastAPI
scripts/       generar_datos, entrenar, demo_evaluar
tests/         features, modelo, reglas, api
data/          diccionario de variables y conjunto sintético
docs/          fuentes de diseño y de código, resultados preliminares, prototipo
models/        modelo entrenado y métricas
```

## Decisiones y límites que hay que tener presentes

- **Los datos son sintéticos.** Los parámetros de `synthetic.py` son supuestos del equipo. Las métricas
  (AUC cercano a 0,95) miden si el pipeline recupera esos supuestos, no la capacidad clínica. Hay que
  decirlo así en el documento y en el video.
- **Metas de la sección 5c.** Con la semilla 42, el AUC de la señal de alerta es 0,946 y la sensibilidad
  en el conjunto de prueba es 0,843, un poco por debajo de la meta de 0,85; para adenomiosis la sensibilidad
  es 0,738. Está pendiente mejorarlas o ajustar las metas cuando haya datos reales.
- **Nivel de alerta.** Es "alta" si el puntaje general supera el umbral elegido por validación cruzada
  o si alguna compatibilidad supera 50 %; así no aparecen mensajes contradictorios.
- **Reglas de recomendación.** Son un borrador del equipo; deben revisarse con una profesional de salud
  y con guías clínicas citadas antes del Hito 3.
- **Explicación.** Por oclusión (reemplazar cada variable por la mediana y medir cuánto baja la alerta).
  SHAP queda para el Hito 3.
- **Privacidad.** No se usan datos reales de personas. Si más adelante se usa KI EndoLIST, hay que firmar
  su acuerdo de uso y no intentar reidentificar a nadie.
