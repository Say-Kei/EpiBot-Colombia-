"""Lee el Boletín Epidemiológico Semanal (BES) del INS en PDF.

Usa las "tablas de mando por departamento" del final del boletín, que vienen como texto:
para cada entidad territorial trae el acumulado del año, lo esperado y lo observado en el
último periodo de 4 semanas. No usa IA ni tokens: lee los números tal como están en el PDF.

Si el INS cambia el formato del boletín, lee_bes() lo detecta y avisa en vez de leer mal.
"""
import re
import unicodedata
from datetime import date
from pathlib import Path

import pdfplumber

from recolector.validar import nombre_depto

URL_BES = "https://www.ins.gov.co/BibliotecaDigital/{ano}-boletin-epidemiologico-semana-{semana}.pdf"
CARPETA = Path(__file__).resolve().parents[2] / "datos" / "crudos" / "bes"

# Distritos que el INS reporta aparte: se suman a su departamento
DISTRITOS = {"barranquilla": "Atlántico", "santiago de cali": "Valle del Cauca",
             "cali": "Valle del Cauca", "buenaventura": "Valle del Cauca",
             "cartagena": "Bolívar", "cartagena de indias": "Bolívar",
             "santa marta": "Magdalena", "providencia": "San Andrés y Providencia"}

# Cómo reconocer el título de cada evento en las tablas de mando. La posición del evento en la
# tabla y el orden de sus columnas NO se fijan: se miden en cada boletín (el INS los cambia).
EVENTOS = {
    "Dengue": "Dengue",          # el primer "Dengue" de la izquierda es "Dengue general"
    "Malaria": "Malaria",
    "Chikungunya": "Chikun",
}
MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
         "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}


class FormatoCambiado(Exception):
    """El boletín no tiene la forma esperada: mejor no leer que leer mal."""


def _sin_tildes(t):
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


def departamento(nombre):
    """'Barranquilla D.E.' -> Atlántico; 'Meta' -> Meta; 'Exterior' -> None."""
    limpio = re.sub(r"\s+d\.?\s*[et]\.?$", "", _sin_tildes(nombre)).strip()   # quita D.E. / D.T.
    return DISTRITOS.get(limpio) or nombre_depto(nombre) or nombre_depto(limpio)


def fecha_corte(pdf):
    """Último día de la semana del boletín: '04 al 10 de octubre de 2026' -> 2026-10-10."""
    texto = pdf.pages[0].extract_text() or ""
    m = re.search(r"\d{1,2}\s+al\s+(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", texto, re.I)
    if not m or _sin_tildes(m.group(2)) not in MESES:
        raise FormatoCambiado("no encontré la fecha de la semana en la primera página")
    return date(int(m.group(3)), MESES[_sin_tildes(m.group(2))], int(m.group(1)))


def _es_numero(t):
    return re.fullmatch(r"\d[\d.]*", t) is not None


def _renglones(palabras):
    """Agrupa las palabras de una página en renglones (por su altura)."""
    renglones = []
    for w in sorted(palabras, key=lambda w: (round(w["top"]), w["x0"])):
        if renglones and abs(renglones[-1][0] - w["top"]) < 3:
            renglones[-1][1].append(w)
        else:
            renglones.append([w["top"], [w]])
    return [(top, sorted(ws, key=lambda w: w["x0"])) for top, ws in renglones]


ROLES = {"esperado": "esperado", "observado": "observado", "lado": "acumulado",
         "acumulado": "acumulado", "2026": "acumulado"}


def _leer_pagina(pagina, patogeno, titulo):
    """Lee un evento de una página de tablas de mando. None si el evento no está en esta página."""
    palabras = pagina.extract_words()
    arriba = " ".join(w["text"] for w in palabras if w["top"] < 200)
    if "Comportamiento" not in arriba or "notificaci" not in arriba:
        return None                                     # no es una tabla de mando
    renglones = _renglones(palabras)
    ref = next(((t, ws) for t, ws in renglones if ws[0]["text"] == "Amazonas"), None)
    if not ref:
        return None
    top_ref, ws_ref = ref
    xs = [w["x0"] for w in ws_ref if _es_numero(w["text"]) and w["x0"] > ws_ref[0]["x1"]]
    titulos = [w for w in palabras if w["text"].startswith(titulo) and w["top"] < top_ref - 30]
    if not titulos or not xs:
        return None
    x_titulo = min(w["x0"] for w in titulos)

    # Columnas: cuántos eventos trae la página (un "Esperado" por evento) y cuántos números cada uno
    banda = [w for w in palabras if top_ref - 30 < w["top"] < top_ref - 2]
    eventos = sum(1 for w in banda if w["text"].lower() == "esperado")
    if not eventos or len(xs) % eventos:
        raise FormatoCambiado(f"{patogeno}: la tabla trae {len(xs)} números para {eventos} eventos")
    columnas = len(xs) // eventos
    inicios = xs[::columnas] + [float("inf")]
    bloque = next((b for b in range(eventos) if inicios[b] - 15 <= x_titulo < inicios[b + 1] - 15), None)
    if bloque is None:
        raise FormatoCambiado(f"{patogeno}: no supe en qué columna está")
    a = bloque * columnas

    # Qué es cada columna del evento (acumulado, esperado, observado), por el encabezado más cercano
    claves = [w for w in banda if w["text"].lower() in ROLES]
    roles = {}
    for j in range(columnas):
        x = xs[a + j]
        cerca = min(claves, key=lambda w: abs(w["x0"] - x), default=None)
        if not cerca or abs(cerca["x0"] - x) > 30:
            raise FormatoCambiado(f"{patogeno}: no reconocí el encabezado de una columna")
        rol = ROLES[cerca["text"].lower()]
        if rol in roles:
            raise FormatoCambiado(f"{patogeno}: dos columnas parecen ser '{rol}'")
        roles[rol] = a + j
    if "esperado" not in roles or "acumulado" not in roles:
        raise FormatoCambiado(f"{patogeno}: faltan las columnas de esperado o acumulado")

    filas, completas, total = {}, 0, None
    for _, ws in renglones:
        # Solo los números dentro de la tabla (el número de página del margen no cuenta)
        ws = [w for w in ws if not _es_numero(w["text"]) or xs[0] - 20 <= w["x0"] <= xs[-1] + 20]
        nombre = " ".join(w["text"] for w in ws if not _es_numero(w["text"]))
        numeros = [w["text"] for w in ws if _es_numero(w["text"])]
        if nombre.lower().startswith("total nacional"):
            total = [int(n.replace(".", "")) for n in numeros]
            continue
        depto = departamento(nombre) if nombre and numeros else None
        if not depto:
            continue
        if len(numeros) != len(xs):
            raise FormatoCambiado(f"{patogeno}: la fila de {nombre} tiene {len(numeros)} números "
                                  f"y se esperaban {len(xs)}")
        numeros = [int(n.replace(".", "")) for n in numeros]
        completas += 1
        acumulado, esperado = numeros[roles["acumulado"]], numeros[roles["esperado"]]
        observado = numeros[roles["observado"]] if "observado" in roles else acumulado
        d = filas.setdefault(depto, {"acumulado": 0, "esperado": 0, "observado": 0})
        d["acumulado"] += acumulado                     # los distritos se suman a su departamento
        d["esperado"] += esperado
        d["observado"] += observado
    if completas < 30:
        raise FormatoCambiado(f"{patogeno}: solo leí {completas} entidades territoriales")
    # Control de calidad: la suma de los departamentos debe dar el "Total nacional" del boletín
    if not total or len(total) != len(xs):
        raise FormatoCambiado(f"{patogeno}: no encontré la fila 'Total nacional' para comprobar")
    suma, esperado_total = sum(d["acumulado"] for d in filas.values()), total[roles["acumulado"]]
    if abs(suma - esperado_total) > max(5, esperado_total * 0.01):
        raise FormatoCambiado(f"{patogeno}: la suma por departamento ({suma}) no coincide con el "
                              f"total nacional del boletín ({esperado_total})")
    periodo = "últimas 4 semanas" if "observado" in roles else "acumulado del año"
    return [{"patogeno": patogeno, "departamento": k, "periodo": periodo, **v} for k, v in filas.items()]


def _leer_evento(pdf, patogeno, titulo):
    errores = []
    for pagina in pdf.pages:
        try:
            filas = _leer_pagina(pagina, patogeno, titulo)
        except FormatoCambiado as e:                   # puede estar en otra página: se sigue buscando
            errores.append(str(e))
            continue
        if filas:
            return filas
    raise FormatoCambiado(errores[0] if errores else f"{patogeno}: no encontré su tabla de mando en el boletín")


def semana_del_pdf(pdf, ruta=None):
    """Número de semana que dice el boletín ('40 Semana epidemiológica', en las primeras páginas)."""
    for pagina in pdf.pages[:5]:
        m = re.search(r"(\d{1,2})\s+Semana\s+epidemiol", pagina.extract_text() or "", re.I)
        if m:
            return int(m.group(1))
    m = re.search(r"semana[-_ ]?(\d{1,2})", Path(ruta or "").name, re.I)   # o el nombre del archivo
    return int(m.group(1)) if m else None


def leer_bes(ruta_pdf):
    """Devuelve (fecha de corte, semana, filas) con dengue, malaria y chikungunya por departamento."""
    with pdfplumber.open(ruta_pdf) as pdf:
        corte = fecha_corte(pdf)
        semana = semana_del_pdf(pdf, ruta_pdf)
        filas, avisos = [], []
        for patogeno, conf in EVENTOS.items():
            # Cada evento se comprueba por separado (suma = total nacional). Si uno no se puede
            # leer, se salta solo ese y los demás sí se cargan.
            try:
                filas += _leer_evento(pdf, patogeno, conf)
            except FormatoCambiado as e:
                avisos.append(str(e))
                print(f"  Aviso BES: {e}. Ese evento no se carga; los demás sí.")
    if not filas:
        raise FormatoCambiado("; ".join(avisos))
    return corte, semana, filas


class NoPublicado(Exception):
    """El INS todavía no ha subido el boletín de esa semana."""


def descargar(ano, semana):
    """Baja el BES de esa semana desde la página del INS y devuelve la ruta del PDF."""
    import requests
    try:
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass
    CARPETA.mkdir(parents=True, exist_ok=True)
    destino = CARPETA / f"bes_{ano}_semana_{semana}.pdf"
    r = requests.get(URL_BES.format(ano=ano, semana=semana), timeout=120)
    if r.status_code == 404 or not r.content.startswith(b"%PDF"):
        raise NoPublicado(f"el BES semana {semana} de {ano} aún no está publicado")
    r.raise_for_status()
    destino.write_bytes(r.content)
    return destino