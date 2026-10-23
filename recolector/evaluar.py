"""Mide cuánto acierta la IA comparando con textos revisados a mano (datos/evaluacion.csv)."""
from pathlib import Path

import pandas as pd

from recolector.ia import extraer
from recolector.validar import normalizar, nombre_depto, ALIAS_PATOGENO

ARCHIVO = Path(__file__).resolve().parents[1] / "datos" / "evaluacion.csv"


def pat(valor):
    """Normaliza un patógeno ("Chikunguña", "tos ferina", vacío -> "")."""
    p = normalizar(valor) if pd.notna(valor) else ""
    return ALIAS_PATOGENO.get(p, p) if p not in ("none", "null", "nan") else ""


def depto(valor):
    """Normaliza un departamento ("VALLE", "76", vacío -> "")."""
    return (nombre_depto(valor) or "") if pd.notna(valor) else ""


def main():
    df = pd.read_csv(ARCHIVO)
    bien_pat = bien_dep = 0
    for i, fila in enumerate(df.to_dict("records"), start=1):
        r = extraer(fila["texto"]) or {}
        ok_pat = pat(r.get("patogeno")) == pat(fila["patogeno"])
        ok_dep = depto(r.get("departamento")) == depto(fila["departamento"])
        bien_pat += ok_pat
        bien_dep += ok_dep
        if not (ok_pat and ok_dep):
            print(f"Fallo en el texto {i}: {str(fila['texto'])[:90]}...")
            print(f"   esperado: {fila['patogeno']} / {fila['departamento']}")
            print(f"   la IA dijo: {r.get('patogeno')} / {r.get('departamento')}")
    print(f"\nTextos evaluados: {len(df)}")
    print(f"Patógeno correcto: {bien_pat / len(df):.0%}")
    print(f"Departamento correcto: {bien_dep / len(df):.0%}")


if __name__ == "__main__":
    main()