"""Comparacion descriptiva del grupo 'endo' sintetico con datos publicados.

Es una validacion externa descriptiva: NO se usa para entrenar el modelo
ni para medir su desempeno. Solo muestra si los supuestos del generador se
parecen a lo que reporta un estudio con pacientes reales.

Uso (desde astraea/):
    python scripts/comparar_datos_reales.py \
        --publicados data/real/publicados.csv \
        --fuente "Kupec et al. 2025 (n=175)"

publicados.csv tiene las columnas: variable,n,media,sd
  - dolor_max    -> media y sd del dolor maximo (0-10)
  - dismenorrea  -> proporcion (0-1) con dolor menstrual
  - dispareunia  -> proporcion (0-1) con dolor en relaciones
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def sintetico_endo(ruta):
    """Resume el grupo endo sintetico en las mismas variables que el estudio."""
    d = pd.read_csv(ruta)
    e = d[d["grupo"] == "endo"]
    return {
        "n": len(e),
        "dolor_max": (e["dolor_max"].mean(), e["dolor_max"].std()),
        "dismenorrea": (e["pct_dolor_en_periodo"] > 0).mean(),
        "dispareunia": (e["loc_relaciones"] > 0).mean(),
    }


def leer_publicados(ruta):
    p = pd.read_csv(ruta).set_index("variable")
    return {
        "n": int(p.loc["dolor_max", "n"]),
        "dolor_max": (p.loc["dolor_max", "media"], p.loc["dolor_max", "sd"]),
        "dismenorrea": p.loc["dismenorrea", "media"],
        "dispareunia": p.loc["dispareunia", "media"],
    }


def pct(x):
    return f"{100 * x:.1f} %".replace(".", ",")


def num(x):
    return f"{x:.2f}".replace(".", ",")


def escribir_md(real, sint, fuente, ruta):
    filas = [
        "| Sintoma | Publicado | Sintetico |",
        "|---|---|---|",
        f"| Dolor maximo (0-10), media (DE) | {num(real['dolor_max'][0])} "
        f"({num(real['dolor_max'][1])}) | {num(sint['dolor_max'][0])} "
        f"({num(sint['dolor_max'][1])}) |",
        f"| Dismenorrea | {pct(real['dismenorrea'])} | {pct(sint['dismenorrea'])} |",
        f"| Dispareunia | {pct(real['dispareunia'])} | {pct(sint['dispareunia'])} |",
    ]
    texto = (
        "# Comparacion descriptiva con datos publicados\n\n"
        f"Fuente: {fuente}. Grupo sintetico: endo (n={sint['n']}).\n\n"
        + "\n".join(filas)
        + "\n\nValidacion externa descriptiva. No se uso para entrenar el "
        "modelo ni para medir su desempeno, y la poblacion publicada es "
        "distinta a la simulada. La dispareunia sintetica cuenta cualquier "
        "dia con dolor en relaciones dentro del registro; el estudio publicado "
        "la mide una sola vez.\n"
    )
    ruta.write_text(texto, encoding="utf-8")


def graficar(real, sint, fuente, ruta):
    fig, ejes = plt.subplots(1, 2, figsize=(9, 4))
    ejes[0].bar(["Publicado", "Sintetico"],
                [real["dolor_max"][0], sint["dolor_max"][0]],
                yerr=[real["dolor_max"][1], sint["dolor_max"][1]], capsize=6,
                color=["#7a7a7a", "#2a6f97"])
    ejes[0].set_ylim(0, 10)
    ejes[0].set_title("Dolor maximo (0-10)")
    ancho = 0.35
    etiquetas = ["Dismenorrea", "Dispareunia"]
    pub = [100 * real["dismenorrea"], 100 * real["dispareunia"]]
    sin = [100 * sint["dismenorrea"], 100 * sint["dispareunia"]]
    x = range(len(etiquetas))
    ejes[1].bar([i - ancho / 2 for i in x], pub, ancho, label="Publicado",
                color="#7a7a7a")
    ejes[1].bar([i + ancho / 2 for i in x], sin, ancho, label="Sintetico",
                color="#2a6f97")
    ejes[1].set_xticks(list(x))
    ejes[1].set_xticklabels(etiquetas)
    ejes[1].set_ylim(0, 125)
    ejes[1].set_ylabel("% de pacientes")
    ejes[1].set_title("Proporcion con el sintoma")
    ejes[1].legend(loc="upper center", ncol=2)
    fig.suptitle(f"Grupo endo sintetico vs {fuente}", fontsize=10)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--publicados", required=True)
    ap.add_argument("--fuente", required=True)
    ap.add_argument("--sintetico", default=str(RAIZ / "data" / "sintetico.csv"))
    ap.add_argument("--salida-md",
                    default=str(RAIZ / "docs" / "comparacion_datos_reales.md"))
    ap.add_argument("--salida-fig", default=str(
        RAIZ / "docs" / "figuras" / "comparacion_datos_reales.png"))
    a = ap.parse_args()

    real = leer_publicados(a.publicados)
    sint = sintetico_endo(a.sintetico)
    Path(a.salida_fig).parent.mkdir(parents=True, exist_ok=True)
    escribir_md(real, sint, a.fuente, Path(a.salida_md))
    graficar(real, sint, a.fuente, a.salida_fig)
    print(f"Tabla:  {a.salida_md}\nFigura: {a.salida_fig}")


if __name__ == "__main__":
    main()
