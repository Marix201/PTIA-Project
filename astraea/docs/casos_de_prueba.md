# Casos de prueba del MVP

Dos casos de punta a punta con pacientes simuladas (semilla 7) y un caso de validación. Se corrieron con `scripts/demo_evaluar.py` y con la API (`POST /evaluar`) sobre el commit `83ec986` de `develop`, con las 21 pruebas automáticas en verde.

Reproducir (desde `astraea/`):

```bash
python scripts/demo_evaluar.py endo 7
python scripts/demo_evaluar.py otra 7
```

## Caso 1: paciente simulada del grupo endometriosis

**Secuencia de entradas**

1. `GET /salud`: comprobar que el modelo está disponible.
2. `POST /evaluar` con el perfil (34 años, menarquia a los 13, sin familiares afectados, antecedente de infertilidad, medicación hormonal, sin CA-125) y 28 días de registro. En el registro, el dolor va de 0 a 5 (media 0,6), hay 5 días de dolor en el periodo y la fatiga media es de 2,9.

**Salida esperada:** alerta alta, compatibilidad alta con endometriosis y estudios sugeridos.

**Salida lograda**

| Campo | Valor |
|---|---|
| Alerta | alta (puntaje 0,605) |
| Compatibilidad con endometriosis | 0,906 |
| Compatibilidad con adenomiosis | 0,138 |
| Patrones explicativos | antecedente de infertilidad (0,371), síntomas digestivos frecuentes (0,135), medicación hormonal (0,124) |
| Estudios sugeridos | ecografía de mapeo pélvico, resonancia magnética, valoración ginecológica |
| Consistencia | la respuesta de la API es idéntica a la de `servicio.evaluar` |

Observación: en este caso la alerta no la dispara el dolor (media de 0,6), sino el antecedente de infertilidad y la medicación hormonal, como muestran los patrones explicativos.

## Caso 2: paciente simulada sin la enfermedad (grupo `otra`)

**Secuencia de entradas**

1. `GET /salud`.
2. `POST /evaluar` con el perfil (32 años, menarquia a los 13, sin familiares afectados, medicación hormonal, sin CA-125) y 28 días de registro. En el registro, el dolor va de 0 a 5 (media 0,7), hay 4 días de dolor en el periodo y la fatiga media es de 1,4.

**Salida esperada:** alerta baja y ningún estudio sugerido.

**Salida lograda**

| Campo | Valor |
|---|---|
| Alerta | baja (puntaje 0,061) |
| Compatibilidad con endometriosis | 0,181 |
| Compatibilidad con adenomiosis | 0,019 |
| Estudios sugeridos | ninguno |
| Consistencia | la respuesta de la API es idéntica a la de `servicio.evaluar` |

## Caso de validación: registro insuficiente

**Entrada:** `POST /evaluar` con solo 3 registros diarios (menos del mínimo exigido).

**Salida esperada:** la API rechaza la solicitud.

**Salida lograda:** respuesta 422.

## Alcance y limitaciones

- Los casos son pacientes simuladas con el mismo generador con el que se entrenó el modelo. Demuestran que el flujo funciona de punta a punta (entrada, modelo, explicación, reglas y respuesta de la API), no validan el desempeño del modelo en pacientes reales.
- Las métricas de desempeño se reportan aparte, en la sección 7.
- Todas las respuestas incluyen el aviso de que el resultado no es un diagnóstico.
