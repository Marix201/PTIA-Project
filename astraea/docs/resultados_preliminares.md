# Resultados preliminares (datos SINTÉTICOS)

Estas métricas miden si el pipeline recupera las asociaciones que el equipo asumió al generar los datos,
no la capacidad clínica del modelo.

Filas: 2000. Semilla: 42. Conjunto de prueba: 20 %, estratificado por grupo.

## Comparación de modelos, validación cruzada de 5 particiones: y_alerta

| familia             |   auc_cv_media |   auc_cv_sd |
|:--------------------|---------------:|------------:|
| regresion_logistica |          0.942 |       0.017 |
| boosting            |          0.94  |       0.017 |
| bosque              |          0.927 |       0.013 |
| arbol               |          0.89  |       0.017 |

## Comparación de modelos, validación cruzada de 5 particiones: y_endo

| familia             |   auc_cv_media |   auc_cv_sd |
|:--------------------|---------------:|------------:|
| regresion_logistica |          0.944 |       0.01  |
| boosting            |          0.936 |       0.009 |
| bosque              |          0.929 |       0.015 |
| arbol               |          0.889 |       0.011 |

## Comparación de modelos, validación cruzada de 5 particiones: y_adeno

| familia             |   auc_cv_media |   auc_cv_sd |
|:--------------------|---------------:|------------:|
| boosting            |          0.909 |       0.013 |
| bosque              |          0.905 |       0.014 |
| regresion_logistica |          0.894 |       0.018 |
| arbol               |          0.858 |       0.018 |

## Métricas en el conjunto de prueba (modelo elegido y calibrado)

| etiqueta   | familia             |   umbral |      auc |   sensibilidad |   especificidad |       f1 |     brier |       ece |   n_prueba |
|:-----------|:--------------------|---------:|---------:|---------------:|----------------:|---------:|----------:|----------:|-----------:|
| y_alerta   | regresion_logistica |   0.6515 | 0.945889 |       0.842975 |        0.917722 | 0.888889 | 0.0871308 | 0.0327614 |        400 |
| y_endo     | regresion_logistica |   0.5    | 0.955269 |       0.822086 |        0.924051 | 0.850794 | 0.0806146 | 0.0410618 |        400 |
| y_adeno    | boosting            |   0.5    | 0.91629  |       0.737589 |        0.915058 | 0.779026 | 0.109154  | 0.0529801 |        400 |

## Ablación sobre la señal de alerta

| configuración                             | familia             |   auc |   sensibilidad |   especificidad |
|:------------------------------------------|:--------------------|------:|---------------:|----------------:|
| solo perfil                               | regresion_logistica | 0.863 |          0.851 |           0.728 |
| perfil y registro diario                  | regresion_logistica | 0.946 |          0.843 |           0.918 |
| perfil y registro diario, sin laboratorio | regresion_logistica | 0.942 |          0.847 |           0.911 |
