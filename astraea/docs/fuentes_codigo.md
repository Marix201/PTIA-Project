# Fuentes del código

## Código

| Módulo | Qué hace | Sección del documento |
| --- | --- | --- |
| `src/astraea/schema.py` | Diccionario de variables y rangos permitidos | 6e, variables de entrada |
| `src/astraea/features.py` | Resume el registro diario en variables clínicas | 6b capa 1, 6e |
| `src/astraea/synthetic.py` | Genera datos sintéticos con parámetros supuestos | 6e, datos |
| `src/astraea/model.py` | Compara 4 modelos, calibra, elige umbrales por sensibilidad, evalúa, ablación | 6e, pipeline y evaluación |
| `src/astraea/explain.py` | Explicación por oclusión | 6b capa 3 |
| `src/astraea/rules.py` | Reglas de recomendación y nivel de alerta | 6b capa 3 |
| `src/astraea/servicio.py`, `api/main.py` | Flujo completo y API FastAPI (`/evaluar`, `/reporte`, `/salud`) | 6d |
| `src/astraea/reporte.py` | Genera el reporte en PDF con ReportLab | 6d, reporte |
| `web/index.html` | Interfaz web conectada a la API | 6d, interfaz |
| `scripts/entrenar.py`, `scripts/figuras_metricas.py` | Entrenan el modelo y generan métricas, matrices de confusión y curvas de calibración | 7, evaluación |
| `scripts/comparar_datos_reales.py` | Compara el grupo sintético con endometriosis con datos publicados | 7, validación externa descriptiva |
| `tests/` | 36 pruebas con pytest (features 5, modelo 7, reglas 7, API 6, reporte 11) | Hito 3, casos de prueba |

## Librerías (versiones instaladas con las que se probó)

Versiones verificadas el 21 de noviembre de 2026 en un entorno nuevo creado con `pip install -r requirements.txt`, que las deja fijadas. Con ellas pasan las 36 pruebas (`pytest`).

| Librería | Versión | Uso |
| --- | --- | --- |
| Python | 3.12.3 | Lenguaje |
| NumPy | 2.5.4 | Cálculo numérico y simulación |
| pandas | 3.0.6 | Tablas de datos |
| scikit-learn | 1.9.1 | Modelos, validación cruzada, calibración, métricas |
| joblib | 1.6.0 | Guardar el modelo |
| FastAPI | 0.143.3 | API |
| pydantic | 2.14.1 | Validación de entradas |
| uvicorn | 0.54.0 | Servidor |
| ReportLab | 5.1.0 | Reporte en PDF |
| pytest, httpx | 9.1.1, 0.28.1 | Pruebas |
| tabulate | 0.10.0 | Tablas Markdown en el reporte de resultados |
| matplotlib | 3.11.2 | Figuras de métricas y de la comparación con datos publicados |

Para volver a comprobarlas: `pip list` dentro del entorno virtual.

## Datos

| Fuente | Estado |
| --- | --- |
| Datos sintéticos de `synthetic.py` (semilla 42, 2000 filas) | En uso. Parámetros supuestos por el equipo que no son pacientes reales |
| Kupec et al. (2025), J Clin Med, 175 mujeres con endometriosis (acceso abierto, CC BY 4.0) | Solo estadísticos descriptivos publicados (`data/real/publicados.csv`), para la comparación descriptiva. No se usó para entrenar ni para medir el desempeño |
| [KI EndoLIST, PhysioNet](https://www.physionet.org/content/ki-endolist/) (v1.0.0, abril de 2026) | Sin usar. 34 pacientes con endometriosis, registro diario; acceso restringido con acuerdo de uso, con tiempos incompatibles con el cronograma |

## Literatura que sustenta las variables y las metas

Goldstein y Cohen (2023); de Kok et al. (2025); De Corte et al. (2025); Mittal et al. (2025); Wang et al. (2025), todos citados en el Hito 1. Para la comparación descriptiva: Kupec et al. (2025).

## Uso de asistencia de IA

Este código se hizo con ayuda de Claude pero también hicimos código nosotras mismas, lo que se hizo con ayuda de IA lo comprendimos y revisamos antes de añadirlo al trabajo.
