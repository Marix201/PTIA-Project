"""Reporte en PDF para llevar a consulta (Hito 3).

Recibe el resultado de `servicio.evaluar` (contrato JSON de la sección 6e) y, si se quiere, los
registros diarios, y devuelve los bytes del PDF. Tiene el mismo contenido que la pantalla
"Reporte para tu consulta" de la interfaz.
"""

from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import Any, Mapping, Sequence
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Textos de la interfaz (web/index.html, constante ESTUDIOS); el último dice "este reporte" en vez de "tu reporte".
ESTUDIOS = {
    "ecografia_mapeo_pelvico": ("Ecografía de mapeo pélvico", "Estudio de imagen que busca signos de endometriosis y adenomiosis en la pelvis."),
    "resonancia_magnetica": ("Resonancia magnética", "Imagen más detallada, útil cuando la ecografía no es suficiente."),
    "valoracion_ginecologica": ("Valoración con ginecólogo", "Lleva este reporte para que el médico revise tus registros en conjunto."),
}
MORADO = colors.HexColor("#4b3fa0")


def _pct(x: float) -> str:
    # Redondea .5 hacia arriba, igual que Math.round de la interfaz (round de Python da 60 para 60,5).
    return f"{int(100 * x + 0.5)} %"


def generar_pdf(resultado: Mapping[str, Any], registros: Sequence[Mapping[str, Any]] | None = None) -> bytes:
    base = getSampleStyleSheet()
    h = ParagraphStyle("h", parent=base["Heading2"], textColor=MORADO, spaceBefore=14, spaceAfter=6)
    n, pie = base["BodyText"], ParagraphStyle("pie", parent=base["BodyText"], fontSize=9, textColor=colors.HexColor("#555555"))
    p = lambda texto, estilo=n: Paragraph(escape(str(texto)), estilo)  # noqa: E731

    r = resultado
    historia = [Paragraph("Reporte Astraea para tu consulta", base["Title"]), p(f"Generado el {date.today():%d/%m/%Y}", pie)]

    dolores = [x["dolor"] for x in (registros or []) if x.get("dolor") is not None]
    if dolores:
        historia += [p("Resumen de tus registros", h), p(f"Días registrados: {len(registros)}. Dolor medio {sum(dolores) / len(dolores):.1f} de 10, máximo {max(dolores)}.")]
    if r.get("advertencia"):
        historia.append(p(r["advertencia"], pie))

    historia += [p("Señal de alerta", h), p(f"Nivel: {r['alerta']['nivel']} (puntaje {_pct(r['alerta']['puntaje'])})")]
    tabla = Table([["Condición", "Compatibilidad"], ["Endometriosis", _pct(r["compatibilidad"]["endometriosis"])], ["Adenomiosis", _pct(r["compatibilidad"]["adenomiosis"])]], colWidths=[8 * cm, 4 * cm])
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), MORADO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("ALIGN", (1, 0), (1, -1), "RIGHT")]))
    historia += [Spacer(1, 6), tabla, Spacer(1, 4), p("Las dos compatibilidades son independientes y no suman 100 %: ambas condiciones pueden presentarse a la vez.", pie)]

    historia.append(p("Patrones detectados", h))
    patrones = [p(x["texto"]) for x in r.get("patrones", [])] or [p("Ninguno destacado")]
    historia.append(ListFlowable(patrones, bulletType="bullet", leftIndent=14))

    historia.append(p("Estudios sugeridos para llevar a consulta", h))
    if r.get("estudios_sugeridos"):
        for clave in r["estudios_sugeridos"]:
            nombre, detalle = ESTUDIOS.get(clave, (clave, ""))
            historia += [Paragraph(f"<b>{escape(nombre)}</b>. {escape(detalle)}", n)]
    else:
        historia.append(p("No se sugieren estudios con esta señal de alerta."))

    notas = [r["aviso"]]
    if not r.get("reglas_revisadas_por_profesional"):
        notas.append("Las reglas de recomendación todavía no han sido revisadas por una profesional de salud.")
    if r.get("entrenado_con_datos_sinteticos"):
        notas.append("Modelo entrenado con datos sintéticos, no con pacientes reales.")
    notas.append(f"Versión del modelo: {r['version_modelo']}")
    historia += [Spacer(1, 14)] + [p(t, pie) for t in notas]

    buf = BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm, title="Reporte Astraea", author="Astraea", pageCompression=0).build(historia)
    return buf.getvalue()
