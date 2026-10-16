# Diccionario de datos de Astraea

Aquí dejamos qué datos se piden en la app, cómo se llaman en la API y en qué se convierten antes de entrar al modelo. Lo que manda es `src/astraea/schema.py`; este archivo es solo una guía para leerlo más fácil. Si se cambia un valor allá, también hay que cambiarlo en el prototipo.

## Perfil de la usuaria (se llena una sola vez)

| Pantalla | Campo en la API | Valores posibles | Variables que usa el modelo |
| --- | --- | --- | --- |
| Antecedentes familiares | `fam` | `no`, `si` (mamá, hermana o hija), `otro`, `nose` | `fam_primer_grado` (1 si es `si`, 0 si es `no` u `otro`, queda vacío si es `nose`) y `fam_otro` |
| Diagnósticos previos | `dx` (lista) | SOP, Miomas, Infertilidad, Enfermedad inflamatoria intestinal, Otro | una variable `dx_*` por cada diagnóstico |
| Laboratorios (opcional) | `ca125` | número mayor o igual a 0, en U/mL | `ca125` (vacío si no lo tiene) y `ca125_faltante` |
| Edad | `edad` | entero de 18 a 55 | `edad` |
| Primera menstruación | `menarquia_edad` | entero de 8 a 18 | `menarquia_edad` |
| Medicación actual | `med` (lista) | Hormonal, Antiinflamatorio, Analgésico | `med_hormonal`, `med_antiinflamatorio`, `med_analgesico` |

## Registro diario (un registro por día)

Se necesitan mínimo 7 días para evaluar; lo ideal es llegar a 28 o más.

| Pantalla | Campo en la API | Valores posibles |
| --- | --- | --- |
| Intensidad del dolor | `dolor` | entero de 0 a 10 |
| Dónde duele | `ubic` (lista) | Pélvico, Lumbar, Durante relaciones, Al evacuar |
| Cómo es el dolor | `tipo` (lista) | Cólico, Punzante, Quemante, Sordo |
| ¿Fue durante el periodo? | `en_periodo` | verdadero o falso |
| Sangrado | `sangrado` | 0 ninguno, 1 manchado, 2 leve, 3 moderado, 4 abundante |
| Fatiga | `fatiga` | entero de 0 a 10 |
| Síntomas digestivos o urinarios | `gi` (lista) | Hinchazón, Diarrea o estreñimiento, Dolor al evacuar, Dolor al orinar, Urgencia urinaria |

Usamos las mismas escalas de dolor (0 a 10) y sangrado (0 a 4) del conjunto KI EndoLIST, para que después se puedan comparar.

## Variables que se calculan a partir del registro (`features.py`)

El modelo no ve los días sueltos, sino un resumen de todos los días registrados:

| Variable | Qué representa |
| --- | --- |
| `dolor_medio`, `dolor_max` | Promedio y valor más alto del dolor en los días registrados |
| `pct_dias_dolor_alto` | Porcentaje de días con dolor de 7 o más |
| `pct_dolor_en_periodo` | Entre los días con dolor, cuántos fueron durante el periodo |
| `pct_dias_fuera_periodo_con_dolor` | Entre los días fuera del periodo, cuántos tuvieron dolor de 3 o más |
| `pct_dias_sangrado_abundante` | Porcentaje de días con sangrado abundante |
| `dias_con_sangrado` | Días con sangrado, ajustados a un mes de 28 días |
| `fatiga_media` | Promedio de la fatiga |
| `pct_dias_gi`, `pct_dias_urinario` | Porcentaje de días con síntomas digestivos o urinarios |
| `loc_*`, `tipo_*` | Entre los días con dolor, qué parte tuvo cada ubicación y cada tipo de dolor |

## Etiquetas (solo para entrenar)

| Etiqueta | Cuándo vale 1 |
| --- | --- |
| `y_endo` | Si la paciente es del grupo endometriosis o ambas |
| `y_adeno` | Si es del grupo adenomiosis o ambas |
| `y_alerta` | Si tiene `y_endo` o `y_adeno` (el 0 es otra causa o ninguna) |

Las tres etiquetas son independientes entre sí, así que una misma paciente puede tener `y_endo` y `y_adeno` en 1 a la vez.
