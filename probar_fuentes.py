"""Revisa que las fuentes de EpiBot respondan, sin gastar tokens de la IA.

    python probar_fuentes.py

Prueba: datos.gov.co (SIVIGILA / INS), la OMS, Google News, la clave de Groq y, si Flask está
corriendo, la API propia. Al final dice qué funciona y qué no.
"""
import os
import time

import requests
from dotenv import load_dotenv

try:  # mismos certificados de Windows que usa el recolector (antivirus o red de la universidad)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

load_dotenv()
resultados = []


def prueba(nombre):
    """Decorador: corre la prueba, mide el tiempo y guarda si pasó o falló."""
    def envolver(funcion):
        print(f"\n== {nombre}")
        inicio = time.time()
        try:
            detalle = funcion()
            resultados.append((nombre, True, detalle))
            print(f"   OK ({time.time() - inicio:.1f} s): {detalle}")
        except Exception as e:  # noqa: BLE001 - queremos ver cualquier falla
            resultados.append((nombre, False, str(e)[:200]))
            print(f"   FALLA ({time.time() - inicio:.1f} s): {e}")
        return funcion
    return envolver


@prueba("SIVIGILA / INS en datos.gov.co")
def sivigila():
    # datos.gov.co es lento con conjuntos grandes: se dan hasta 90 s y se hacen consultas livianas
    url = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
    headers = {"X-App-Token": os.getenv("DATOS_GOV_TOKEN")} if os.getenv("DATOS_GOV_TOKEN") else {}
    espera = 90
    # 1. ¿Responde? Una sola fila, sin filtros (es la consulta más rápida posible)
    r = requests.get(url, params={"$limit": 1}, headers=headers, timeout=espera)
    r.raise_for_status()
    filas = r.json()
    if not filas:
        raise RuntimeError("respondió, pero vacío")
    faltan = {"nombre_evento", "ano", "semana", "departamento_ocurrencia", "conteo"} - set(filas[0])
    if faltan:
        raise RuntimeError(f"cambiaron las columnas; faltan {sorted(faltan)}")
    # 2. ¿Hasta qué año llegan los datos de dengue? Con "=" exacto, que es mucho más rápido que "like"
    r = requests.get(url, params={"$select": "max(ano) as ano", "$where": "nombre_evento = 'DENGUE'"},
                     headers=headers, timeout=espera)
    r.raise_for_status()
    ano = (r.json() or [{}])[0].get("ano")
    if not ano:
        return "responde y tiene las columnas correctas (no se pudo ver el último año de dengue)"
    r = requests.get(url, params={"$select": "max(semana) as semana",
                                  "$where": f"nombre_evento = 'DENGUE' AND ano = '{ano}'"},
                     headers=headers, timeout=espera)
    r.raise_for_status()
    semana = (r.json() or [{}])[0].get("semana")
    return f"responde; dengue llega hasta el año {ano}, semana {semana}"


@prueba("OMS (Disease Outbreak News)")
def oms():
    r = requests.get("https://www.who.int/api/news/diseaseoutbreaknews",
                     params={"$orderby": "PublicationDate desc", "$top": 100}, timeout=30)
    r.raise_for_status()
    items = r.json().get("value", [])
    if not items:
        raise RuntimeError("respondió, pero sin noticias")
    colombia = [i for i in items if "colombia" in str(i).lower()]
    ultima = items[0]
    return (f"{len(items)} noticias; la más reciente es del {str(ultima.get('PublicationDate'))[:10]} "
            f"('{ultima.get('Title')}'); {len(colombia)} mencionan a Colombia")


@prueba("Google News (prensa)")
def google_news():
    import feedparser
    url = ("https://news.google.com/rss/search?q=dengue+Colombia+when%3A30d"
           "&hl=es-419&gl=CO&ceid=CO:es-419")
    feed = feedparser.parse(url)
    if feed.get("bozo") and not feed.entries:
        raise RuntimeError(f"no se pudo leer: {feed.get('bozo_exception')}")
    if not feed.entries:
        raise RuntimeError("respondió, pero sin noticias")
    return f"{len(feed.entries)} noticias de dengue de los últimos 30 días; la primera: '{feed.entries[0].title[:70]}'"


@prueba("Groq (clave de la IA, sin gastar tokens)")
def groq():
    url, clave = os.getenv("IA_URL"), os.getenv("IA_KEY")
    if not url or not clave:
        raise RuntimeError("faltan IA_URL o IA_KEY en el .env")
    # Pedir la lista de modelos no gasta tokens y confirma que la clave sirve
    r = requests.get(url.rstrip("/") + "/models", headers={"Authorization": f"Bearer {clave}"}, timeout=30)
    if r.status_code == 401:
        raise RuntimeError("la clave no es válida (401): revísala o crea una nueva en Groq")
    r.raise_for_status()
    modelos = [m.get("id") for m in r.json().get("data", [])]
    modelo = os.getenv("IA_MODELO")
    if modelo and modelo not in modelos:
        raise RuntimeError(f"la clave sirve, pero el modelo '{modelo}' no está disponible")
    return f"la clave sirve y el modelo '{modelo}' está disponible"


@prueba("API propia de EpiBot (Flask en http://127.0.0.1:5000)")
def api_propia():
    try:
        r = requests.get("http://127.0.0.1:5000/api/zonas", timeout=10)
    except requests.ConnectionError:
        raise RuntimeError("Flask no está corriendo: abre otra terminal con 'python app.py' y repite")
    r.raise_for_status()
    zonas = r.json().get("zonas", [])
    con_alerta = [z[1] for z in zonas if any(v[0] != "sin" for v in z[5].values())]
    return f"{len(zonas)} departamentos; con alguna alerta: {', '.join(con_alerta) or 'ninguno'}"


print("\n================ RESUMEN ================")
for nombre, ok, detalle in resultados:
    print(f"{'OK   ' if ok else 'FALLA'}  {nombre}")
print(f"\n{sum(ok for _, ok, _ in resultados)} de {len(resultados)} funcionan.")