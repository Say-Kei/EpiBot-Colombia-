"""Carga en la base el histórico oficial del INS desde 2020.

Se ejecuta a mano, una vez (y luego cuando se agreguen XLSX nuevos):
    python -m recolector.importar_historico
"""
from recolector import base
from recolector.fuentes import ins


def main():
    hist = ins.historico(usar_cache=False)
    if hist.empty:
        print("No hay datos del INS: revisa los XLSX en datos/crudos/ins o la conexión a datos.gov.co")
        return
    n = base.guardar_historico(hist)
    anos = sorted(hist[hist["ano"] >= base.ANO_INICIO]["ano"].astype(int).unique())
    print(f"{n} filas guardadas en {base.RUTA}")
    print("Años:", anos)
    tam = base.RUTA.stat().st_size / 1_000_000
    print(f"Tamaño de la base: {tam:.1f} MB")


if __name__ == "__main__":
    main()