"""Noticias de brotes de la OMS (Disease Outbreak News) que mencionan a Colombia."""
import json
from datetime import date
from pathlib import Path

import requests

try:  # usa los certificados de Windows (antivirus o red de la universidad)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

URL = "https://www.who.int/api/news/diseaseoutbreaknews"
BASE = "https://www.who.int/emergencies/disease-outbreak-news/item/"
CRUDOS = Path(__file__).resolve().parents[2] / "datos" / "crudos"


def recolectar():
    filas = []
    try:
        params = {"$orderby": "PublicationDate desc", "$top": 100}
        r = requests.get(URL, params=params, timeout=30)
        r.raise_for_status()
        items = r.json().get("value", [])
    except (requests.RequestException, ValueError) as e:
        print("OMS no disponible:", e)
        return filas

    for item in items:
        titulo = item.get("Title") or ""
        texto = " ".join(item.get(k) or "" for k in ("Summary", "Overview", "Epidemiology"))
        if "colombia" not in (titulo + texto).lower():
            continue  # solo brotes que mencionan a Colombia
        filas.append({"fuente": "OMS", "tipo": "internacional", "titulo": titulo,
                      "texto": texto, "url": BASE + (item.get("UrlName") or ""),
                      "fecha": item.get("PublicationDate", "")})

    CRUDOS.mkdir(parents=True, exist_ok=True)
    (CRUDOS / f"oms_{date.today()}.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(items), "noticias de la OMS revisadas,", len(filas), "mencionan a Colombia")
    return filas