"""Noticias de Google News (RSS) sobre dengue, chikungunya y malaria en Colombia.

Hace búsquedas nacionales y búsquedas por ciudad o departamento: las noticias locales son las
que permiten ubicar una alerta en un departamento concreto.
No gasta tokens: aquí solo se descargan titulares. La IA lee después solo las nuevas
(main.py salta las que ya leyó y toma máximo MAX_TEXTOS).
"""
import json
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

import feedparser

CRUDOS = Path(__file__).resolve().parents[2] / "datos" / "crudos"
DIAS = 30            # Google News: solo noticias de los últimos 30 días (when:30d)
PAUSA = 0.5          # segundos entre búsquedas, para no saturar a Google News

# Búsquedas nacionales
NACIONALES = [
    "brote dengue Colombia",
    "casos de dengue secretaría de salud Colombia",
    "dengue aumento de casos departamento Colombia",
    "chikungunya casos Colombia",
    "malaria casos Colombia",
]
# Dengue: capitales y ciudades donde más se concentra
CIUDADES_DENGUE = ["Barranquilla", "Cartagena", "Santa Marta", "Valledupar", "Montería",
                   "Sincelejo", "Riohacha", "Cúcuta", "Bucaramanga", "Villavicencio", "Yopal",
                   "Neiva", "Ibagué", "Cali", "Medellín", "Leticia"]
# Malaria: departamentos donde más se concentra (Pacífico, Orinoquía, Amazonía)
DEPTOS_MALARIA = ["Chocó", "Nariño", "Antioquia", "Córdoba", "Cauca", "Guainía", "Amazonas", "Vichada"]

BUSQUEDAS = (NACIONALES
             + [f"dengue {c}" for c in CIUDADES_DENGUE]
             + [f"malaria {d}" for d in DEPTOS_MALARIA])


def url_busqueda(q):
    return ("https://news.google.com/rss/search?q=" + quote_plus(f"{q} when:{DIAS}d")
            + "&hl=es-419&gl=CO&ceid=CO:es-419")


def recolectar():
    filas, vistas = [], set()
    for i, q in enumerate(BUSQUEDAS):
        if i:
            time.sleep(PAUSA)
        try:
            entradas = feedparser.parse(url_busqueda(q)).entries
        except Exception as e:          # una búsqueda que falla no detiene las demás
            print(f"  No se pudo buscar '{q}':", e)
            continue
        nuevas = 0
        for n in entradas:
            enlace = n.get("link", "")
            if not enlace or enlace in vistas:   # la misma noticia sale en varias búsquedas
                continue
            vistas.add(enlace)
            filas.append({"fuente": "Prensa", "tipo": "temprana", "titulo": n.get("title", ""),
                          "texto": n.get("summary", ""), "url": enlace,
                          "fecha": n.get("published", ""), "busqueda": q})
            nuevas += 1
        print(f"  '{q}': {nuevas} noticias")
    CRUDOS.mkdir(parents=True, exist_ok=True)
    archivo = CRUDOS / f"noticias_{date.today()}.json"
    archivo.write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(BUSQUEDAS), "búsquedas en Google News,", len(filas), "noticias distintas")
    return filas