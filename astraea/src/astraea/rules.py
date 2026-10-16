
from __future__ import annotations

UMBRAL_COMPATIBILIDAD = 0.5

AVISO = "Este resultado no es un diagnóstico. Un resultado bajo no descarta la enfermedad."


def nivel_alerta(puntaje: float, umbral: float, p_endo: float = 0.0, p_adeno: float = 0.0) -> str:
    """Alta si la señal general supera su umbral O alguna compatibilidad supera el 50 %.

    La segunda condición evita mensajes contradictorios (alerta baja con 90 % de compatibilidad)
    y favorece la sensibilidad, que es la prioridad del proyecto.
    """
    if puntaje >= umbral or max(p_endo, p_adeno) >= UMBRAL_COMPATIBILIDAD:
        return "alta"
    return "baja"


def estudios_sugeridos(nivel: str, p_endo: float, p_adeno: float) -> list[str]:
    """Identificadores de los tres estudios de la pantalla "¿Qué exigir a tu médico?"."""
    if nivel != "alta":
        return []
    estudios = ["valoracion_ginecologica"]
    if p_endo >= UMBRAL_COMPATIBILIDAD:
        estudios.insert(0, "ecografia_mapeo_pelvico")
    if p_endo >= UMBRAL_COMPATIBILIDAD or p_adeno >= UMBRAL_COMPATIBILIDAD:
        estudios.insert(len(estudios) - 1, "resonancia_magnetica")
    if len(estudios) == 1:  # alerta alta pero ninguna compatibilidad llega al umbral
        estudios.insert(0, "ecografia_mapeo_pelvico")
    return estudios
