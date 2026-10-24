"""Carga en epibot.db datos de boletines OFICIALES (INS, secretarías de salud) escritos a mano.

Los boletines oficiales de 2026 vienen en PDF, así que una persona los lee y copia las cifras
en datos/oficiales.csv. Este script las valida y las une a la alerta de esta semana como fuente
"oficial": así la página muestra "Confirmado por el INS" y el nivel puede llegar a Crítico.

    python cargar_oficial.py --simular     # muestra qué haría, sin guardar nada
    python cargar_oficial.py               # guarda en la base y actualiza alertas.json

Columnas de datos/oficiales.csv (una fila por patógeno y departamento):
    patogeno       dengue, chikungunya o malaria
    departamento   como sea: "Santander", "SANTANDER", "Valle"...
    casos          casos de la semana del boletín (vacío si el boletín no lo dice)
    esperado       casos esperados según el boletín (vacío = se calcula con el histórico del INS)
    fecha          fecha de corte del boletín, AAAA-MM-DD
    fuente         nombre corto, por ejemplo: INS · BES semana 40
    url            enlace al PDF del boletín (debe empezar por https://)
    municipios     opcional, separados por ;  (ej. Bucaramanga;Floridablanca)
"""
import argparse
import csv
import re
from datetime import date, timedelta
from pathlib import Path

from recolector.oficial import guardar_oficiales, MAX_DIAS
from recolector.validar import (PATOGENOS, ALIAS_PATOGENO, normalizar, nombre_depto,
                                limpiar_municipios)

ARCHIVO = Path(__file__).resolve().parent / "datos" / "oficiales.csv"
COLUMNAS = ["patogeno", "departamento", "casos", "esperado", "fecha", "fuente", "url", "municipios"]
PATOGENOS_WEB = {"dengue", "chikungunya", "malaria"}


def numero(texto, campo):
    """'1.234' o '1234' -> 1234; vacío -> None."""
    t = (texto or "").replace(".", "").replace(",", "").strip()
    if not t:
        return None
    if not t.isdigit():
        raise ValueError(f"{campo} debe ser un número entero (llegó '{texto}')")
    return int(t)


def leer_fila(fila, hoy):
    """Valida una fila del CSV. Devuelve un diccionario limpio o lanza ValueError con el motivo."""
    pat = normalizar(fila.get("patogeno"))
    pat = ALIAS_PATOGENO.get(pat, pat)
    if pat not in PATOGENOS_WEB:
        raise ValueError(f"patógeno '{fila.get('patogeno')}' no es dengue, chikungunya ni malaria")
    depto = nombre_depto(fila.get("departamento"))
    if not depto:
        raise ValueError(f"departamento '{fila.get('departamento')}' no se reconoce")
    try:
        fecha = date.fromisoformat((fila.get("fecha") or "").strip())
    except ValueError:
        raise ValueError(f"fecha '{fila.get('fecha')}' debe ser AAAA-MM-DD")
    if fecha > hoy:
        raise ValueError(f"fecha {fecha} está en el futuro")
    if fecha < hoy - timedelta(days=MAX_DIAS):
        raise ValueError(f"el boletín es del {fecha}: tiene más de {MAX_DIAS} días y ya no "
                         "confirma la situación actual")
    url = (fila.get("url") or "").strip()
    if not re.fullmatch(r"https://[^\s\"'<>]+", url):
        raise ValueError("url debe ser un enlace que empiece por https://")
    fuente = " ".join((fila.get("fuente") or "").split())[:80]
    if not fuente or re.search(r"[<>]", fuente):
        raise ValueError("fuente vacía o con caracteres no permitidos")
    return {"patogeno": pat.capitalize(), "tipo": PATOGENOS[pat], "departamento": depto,
            "casos": numero(fila.get("casos"), "casos"),
            "esperado": numero(fila.get("esperado"), "esperado"),
            "municipios": limpiar_municipios((fila.get("municipios") or "").split(";")),
            "fuente": {"nombre": fuente, "tipo": "oficial", "url": url, "fecha": str(fecha)}}


def main():
    ap = argparse.ArgumentParser(description="Carga datos de boletines oficiales en epibot.db")
    ap.add_argument("--simular", action="store_true", help="mostrar qué haría, sin guardar")
    simular = ap.parse_args().simular

    if not ARCHIVO.exists():
        ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
        ARCHIVO.write_text(",".join(COLUMNAS) + "\n", encoding="utf-8")
        print(f"Creé {ARCHIVO} vacío: llénalo con los datos del boletín y vuelve a correr.")
        return

    hoy = date.today()
    with open(ARCHIVO, encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        print("oficiales.csv no tiene filas.")
        return

    registros, errores = [], 0
    for n, fila in enumerate(filas, start=2):         # la fila 1 es el encabezado
        try:
            registros.append(leer_fila(fila, hoy))
        except ValueError as e:
            errores += 1
            print(f"  Fila {n}: se salta -> {e}")
    print(f"{len(registros)} filas válidas, {errores} con errores.\n")
    guardar_oficiales(registros, hoy, simular)


if __name__ == "__main__":
    main()