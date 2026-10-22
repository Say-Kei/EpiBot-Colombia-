"""Noticias de Google News (RSS) sobre los patógenos del proyecto en Colombia."""
import json
from datetime import date
from pathlib import Path

import feedparser

CRUDOS = Path(__file__).resolve().parents[2] / "datos" / "crudos"

# Una búsqueda por patógeno
BUSQUEDAS = ["brote dengue Colombia", "malaria Colombia casos", "tosferina Colombia",
             "fiebre amarilla Colombia", "oropouche Colombia", "chikungunya Colombia"]


def recolectar():
    filas = []
    for q in BUSQUEDAS:
        url = ("https://news.google.com/rss/search?q=" + q.replace(" ", "+")
               + "&hl=es-419&gl=CO&ceid=CO:es-419")
        for n in feedparser.parse(url).entries:
            filas.append({"fuente": "Prensa", "tipo": "temprana", "titulo": n.title,
                          "texto": n.get("summary", ""), "url": n.link,
                          "fecha": n.get("published", "")})
    CRUDOS.mkdir(parents=True, exist_ok=True)
    archivo = CRUDOS / f"noticias_{date.today()}.json"
    archivo.write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    return filas