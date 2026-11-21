# Fuentes del código

## Código

| Módulo | Qué hace | Sección del documento |
| --- | --- | --- |
| `src/astraea/schema.py` | Diccionario de variables y rangos permitidos | 6e, variables de entrada |
| `src/astraea/features.py` | Resume el registro diario en variables clínicas | 6b capa 1, 6e |
| `src/astraea/synthetic.py` | Genera datos sintéticos con parámetros supuestos | 6e, datos |
| `src/astraea/model.py` | Compara 4 modelos, calibra, elige umbral, evalúa, ablación | 6e, pipeline y evaluación |
| `src/astraea/explain.py` | Explicación por oclusión | 6b capa 3 |
| `src/astraea/rules.py` | Reglas de recomendación| 6b capa 3 |
| `src/astraea/servicio.py`, `api/main.py` | Flujo completo y API FastAPI | 6d |
| `tests/` | 21 pruebas con pytest | Hito 3, casos de prueba |

## Librerías (versiones instaladas con las que se probó)

Versiones verificadas el 20 de noviembre de 2026 en un entorno nuevo creado con `pip install -r requirements.txt`. Con ellas pasan las 21 pruebas (`pytest`) y se reproducen las métricas de `models/metricas.json` (AUC de alerta 0,946; sensibilidad 0,843).

| Librería | Versión | Uso |
| --- | --- | --- |
| Python | 3.13.18 | Lenguaje |
| NumPy | 2.5.5 | Cálculo numérico y simulación |
| pandas | 3.1.1 | Tablas de datos |
| scikit-learn | 1.9.1 | Modelos, validación cruzada, calibración, métricas |
| joblib | 1.6.0 | Guardar el modelo |
| FastAPI | 0.165.0 | API |
| pydantic | 2.14.4 | Validación de entradas |
| uvicorn | 0.54.0 | Servidor |
| pytest, httpx | 9.2.0, 0.28.1 | Pruebas |
| tabulate | 0.10.0 | Tablas Markdown en el reporte de resultados (opcional) |

Para volver a comprobarlas: `pip list` dentro del entorno virtual.


## Datos

| Fuente | Estado |
| --- | --- |
| Datos sintéticos de `synthetic.py` (semilla 42, 2000 filas) | En uso. Parámetros supuestos por el equipo que no son pacientes reales |
| [KI EndoLIST, PhysioNet](https://www.physionet.org/content/ki-endolist/) (v1.0.0, abril de 2026) | Sin usar todavía. 34 pacientes con endometriosis, registro diario; acceso restringido con acuerdo de uso |

## Literatura que sustenta las variables y las metas

Goldstein y Cohen (2023); de Kok et al. (2025); De Corte et al. (2025); Mittal et al. (2025); Wang et al. (2025), todos citados en el Hito 1.

## Uso de asistencia de IA

Este código se hizo con ayuda de Claude pero también hicimos código nosotras mismas, lo que se hizo con ayuda de IA lo comprendimos y revisamos antes de añadirlo al trabajo.
