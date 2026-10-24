"""Carga A MANO un Boletín Epidemiológico Semanal (BES) del INS en epibot.db.

El recolector (python -m recolector.main) ya busca y carga solo el BES más reciente. Este script
sirve para revisar un boletín antes de guardarlo, o para cargar uno que descargaste tú.

    python cargar_bes.py --semana 41                 # baja el BES 41 del INS y muestra las cifras
    python cargar_bes.py --semana 41 --guardar       # ...y las guarda
    python cargar_bes.py datos/crudos/bes/mi.pdf     # usa un PDF que ya descargaste
"""
import argparse
from datetime import date
from pathlib import Path

from recolector import base
from recolector.fuentes import bes
from recolector.oficial import registros_desde_bes, guardar_oficiales


def main():
    ap = argparse.ArgumentParser(description="Carga un BES del INS en epibot.db")
    ap.add_argument("pdf", nargs="?", help="ruta a un PDF del BES ya descargado")
    ap.add_argument("--semana", type=int, help="semana del BES para bajarlo del INS")
    ap.add_argument("--ano", type=int, default=date.today().year)
    ap.add_argument("--guardar", action="store_true", help="guardar en la base (sin esto, solo muestra)")
    a = ap.parse_args()

    if a.pdf:
        ruta = Path(a.pdf)
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo {ruta}")
    elif a.semana:
        print(f"Descargando el BES semana {a.semana} de {a.ano} del INS...")
        try:
            ruta = bes.descargar(a.ano, a.semana)
        except bes.NoPublicado as e:
            raise SystemExit(str(e))
    else:
        raise SystemExit("Indica un PDF o --semana N (por ejemplo: python cargar_bes.py --semana 41)")

    hoy = date.today()
    try:
        corte, semana, url, registros = registros_desde_bes(ruta, hoy)
    except bes.FormatoCambiado as e:
        raise SystemExit(f"No se carga, para no leer mal: {e}. Copia las cifras con cargar_oficial.py.")
    print(f"BES semana {semana}, corte {corte}: {len(registros)} departamentos con casos.\n")
    guardar_oficiales(registros, hoy, simular=not a.guardar)
    if a.guardar:
        base.marcar_procesadas([url])       # así el recolector automático no lo vuelve a cargar
    else:
        print("Compara 2 o 3 cifras con el PDF. Si están bien, repite con --guardar.")


if __name__ == "__main__":
    main()