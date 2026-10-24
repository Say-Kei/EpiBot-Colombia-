"""Actualiza data/dengue.json. La web lo detecta sola, sin reiniciar Flask.

  python actualizar_datos.py --manual
      Te pregunta cada cifra del ultimo boletin del INS (Enter = dejar la actual).

  python actualizar_datos.py --soda ID_DATASET --col COLUMNA [--dominio www.datos.gov.co]
      Cuenta casos por municipio desde un conjunto de datos abiertos (API Socrata)
      y llena el ranking del panel. Necesitas el ID y el nombre de la columna
      que aparecen en la pagina del conjunto de datos. (Sin probar con datos reales.)
"""
import argparse, datetime, json, os, urllib.parse, urllib.request

RUTA = os.path.join(os.path.dirname(__file__), "data", "dengue.json")


def pedir(etiqueta, actual):
    v = input(f"{etiqueta} [{actual}]: ").strip()
    return v or actual


def manual(d):
    d["casos_total"] = pedir("Casos acumulados (ej. 70.452)", d["casos_total"])
    d["semana"] = int(pedir("Semana epidemiologica", d["semana"]))
    d["anio"] = int(pedir("Anio", d["anio"]))
    d["concentracion"]["porcentaje"] = pedir("% de casos en los territorios con mas casos", d["concentracion"]["porcentaje"])
    for dep in ("Magdalena", "Cesar"):
        d["incrementos"][dep] = pedir(f"Incremento {dep} (ej. +234%)", d["incrementos"][dep])
    for k in ("municipios_sobre_esperado", "municipios_riesgo"):
        d["alerta"][k] = pedir(k, d["alerta"][k])
    d["atlantico_brote"] = pedir("Municipios del Atlantico en brote", d["atlantico_brote"])


def soda(d, dominio, dataset, col):
    q = urllib.parse.urlencode({"$select": f"{col},count(*) as casos", "$group": col,
                                "$order": "casos DESC", "$limit": "15"})
    with urllib.request.urlopen(f"https://{dominio}/resource/{dataset}.json?{q}", timeout=30) as r:
        filas = json.load(r)
    d["ranking"] = [{"nombre": f[col], "casos": int(f["casos"])} for f in filas if f.get(col)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual", action="store_true")
    ap.add_argument("--soda"); ap.add_argument("--col")
    ap.add_argument("--dominio", default="www.datos.gov.co")
    a = ap.parse_args()
    with open(RUTA, encoding="utf-8") as f:
        d = json.load(f)
    if a.manual:
        manual(d)
    if a.soda and a.col:
        soda(d, a.dominio, a.soda, a.col)
    d["fecha_carga"] = datetime.date.today().isoformat()
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print("Listo: data/dengue.json actualizado.")
