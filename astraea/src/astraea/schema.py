"""Diccionario de variables de Astraea (contrato entre la interfaz, la API y el modelo).

Cada campo del mock-up tiene una variable. Los valores permitidos aquí son los mismos
que muestra el prototipo de interfaz; si se cambia uno, hay que cambiarlo en ambos.
"""

from __future__ import annotations

# --- Perfil (se llena una vez) -------------------------------------------------
FAM_VALORES = ("no", "si", "otro", "nose")  # antecedentes familiares
DX_PREVIOS = ("SOP", "Miomas", "Infertilidad", "Enfermedad inflamatoria intestinal", "Otro")
MEDICACION = ("Hormonal", "Antiinflamatorio", "Analgésico")
EDAD_RANGO = (18, 55)
MENARQUIA_RANGO = (8, 18)

# --- Registro diario (se llena cada día) --------------------------------------
UBICACIONES = ("Pélvico", "Lumbar", "Durante relaciones", "Al evacuar")
TIPOS_DOLOR = ("Cólico", "Punzante", "Quemante", "Sordo")
SANGRADO = ("Ninguno", "Manchado", "Leve", "Moderado", "Abundante")  # 0 a 4
SINTOMAS_GI_URIN = (
    "Hinchazón",
    "Diarrea o estreñimiento",
    "Dolor al evacuar",
    "Dolor al orinar",
    "Urgencia urinaria",
)
DOLOR_RANGO = (0, 10)
FATIGA_RANGO = (0, 10)

# Mínimo de días de registro para evaluar y días recomendados (1 ciclo)
MIN_DIAS = 7
DIAS_RECOMENDADOS = 28

# --- Variables que recibe el modelo (salida de features.py) --------------------
FEATURES_PERFIL = [
    "fam_primer_grado",
    "fam_otro",
    "dx_sop",
    "dx_miomas",
    "dx_infertilidad",
    "dx_eii",
    "dx_otro",
    "edad",
    "menarquia_edad",
    "med_hormonal",
    "med_antiinflamatorio",
    "med_analgesico",
    "ca125",
    "ca125_faltante",
]

FEATURES_DIARIO = [
    "dolor_medio",
    "dolor_max",
    "pct_dias_dolor_alto",
    "pct_dolor_en_periodo",
    "pct_dias_fuera_periodo_con_dolor",
    "pct_dias_sangrado_abundante",
    "dias_con_sangrado",
    "fatiga_media",
    "pct_dias_gi",
    "pct_dias_urinario",
    "loc_pelvico",
    "loc_lumbar",
    "loc_relaciones",
    "loc_evacuar",
    "tipo_colico",
    "tipo_punzante",
    "tipo_quemante",
    "tipo_sordo",
]

FEATURES = FEATURES_PERFIL + FEATURES_DIARIO

TARGETS = ("y_alerta", "y_endo", "y_adeno")

# Texto en lenguaje claro para "Patrones detectados" (pantalla de resultados)
TEXTO_FACTOR = {
    "fam_primer_grado": "Antecedente familiar",
    "fam_otro": "Otro familiar con endometriosis",
    "dx_sop": "Diagnóstico previo de SOP",
    "dx_miomas": "Diagnóstico previo de miomas",
    "dx_infertilidad": "Antecedente de infertilidad",
    "dx_eii": "Enfermedad inflamatoria intestinal",
    "dx_otro": "Otro diagnóstico previo",
    "edad": "Edad",
    "menarquia_edad": "Edad de la primera menstruación",
    "med_hormonal": "Uso de medicación hormonal",
    "med_antiinflamatorio": "Uso de antiinflamatorios",
    "med_analgesico": "Uso de analgésicos",
    "ca125": "Valor de CA-125",
    "ca125_faltante": "Sin dato de laboratorio",
    "dolor_medio": "Dolor medio alto",
    "dolor_max": "Dolor máximo alto",
    "pct_dias_dolor_alto": "Muchos días con dolor intenso",
    "pct_dolor_en_periodo": "El dolor coincide con el periodo",
    "pct_dias_fuera_periodo_con_dolor": "Dolor fuera del periodo",
    "pct_dias_sangrado_abundante": "Días de sangrado abundante",
    "dias_con_sangrado": "Duración del sangrado",
    "fatiga_media": "Fatiga frecuente",
    "pct_dias_gi": "Síntomas digestivos frecuentes",
    "pct_dias_urinario": "Síntomas urinarios frecuentes",
    "loc_pelvico": "Dolor pélvico",
    "loc_lumbar": "Dolor lumbar",
    "loc_relaciones": "Dolor durante relaciones",
    "loc_evacuar": "Dolor al evacuar",
    "tipo_colico": "Dolor tipo cólico",
    "tipo_punzante": "Dolor punzante",
    "tipo_quemante": "Dolor quemante",
    "tipo_sordo": "Dolor sordo",
}
