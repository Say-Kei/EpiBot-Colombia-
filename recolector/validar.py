import re
import unicodedata
from datetime import date, timedelta


def normalizar(t):
    """Quita tildes, pasa a minúsculas y quita espacios de los extremos."""
    t = unicodedata.normalize("NFD", str(t) if t is not None else "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


DEPARTAMENTOS = ["Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.", "Bolívar",
    "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba",
    "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena", "Meta",
    "Nariño", "Norte de Santander", "Putumayo", "Quindío", "Risaralda",
    "San Andrés y Providencia", "Santander", "Sucre", "Tolima", "Valle del Cauca",
    "Vaupés", "Vichada"]

# Formas en que puede venir escrito cada departamento -> nombre oficial
ALIAS = {normalizar(d): d for d in DEPARTAMENTOS}
ALIAS.update({"bogota": "Bogotá D.C.", "bogota d.c.": "Bogotá D.C.", "bogota dc": "Bogotá D.C.",
              "bogota, d.c.": "Bogotá D.C.",
              "valle": "Valle del Cauca", "guajira": "La Guajira",
              "norte santander": "Norte de Santander",
              "san andres": "San Andrés y Providencia",
              "archipielago de san andres": "San Andrés y Providencia",
              "archipielago de san andres, providencia y santa catalina": "San Andrés y Providencia"})

# Códigos DIVIPOLA de departamento (por si el INS trae números en vez de nombres)
CODIGOS = {"05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar",
           "15": "Boyacá", "17": "Caldas", "18": "Caquetá", "19": "Cauca", "20": "Cesar",
           "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó", "41": "Huila",
           "44": "La Guajira", "47": "Magdalena", "50": "Meta", "52": "Nariño",
           "54": "Norte de Santander", "63": "Quindío", "66": "Risaralda", "68": "Santander",
           "70": "Sucre", "73": "Tolima", "76": "Valle del Cauca", "81": "Arauca",
           "85": "Casanare", "86": "Putumayo", "88": "San Andrés y Providencia",
           "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés", "99": "Vichada"}

# Patógenos del proyecto y su tipo
PATOGENOS = {"dengue": "virus", "malaria": "parasito",
             "fiebre amarilla": "virus", "oropouche": "virus", "chikungunya": "virus"}

# Formas en que se puede escribir un patógeno -> nombre de PATOGENOS
ALIAS_PATOGENO = {"chikunguna": "chikungunya", "chicungunya": "chikungunya",
                  "chikungunia": "chikungunya", "chikungunya": "chikungunya",
                   "paludismo": "malaria"}


# Seguridad: los municipios los escribe la IA a partir de noticias de internet. Un texto armado
# a propósito (prompt injection) podría traer código HTML. Solo se aceptan nombres que parezcan
# nombres de municipio: letras (con tildes), espacios, puntos, comas, guiones y apóstrofos.
MAX_MUNICIPIOS = 15
NOMBRE_MUNICIPIO = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ .,'\-]{2,60}")


def limpiar_municipios(valor):
    """Lista de municipios segura: solo textos con forma de nombre, sin repetir, máximo 15.

    Cualquier otra cosa (un texto suelto, null, números, objetos, HTML) se descarta.
    """
    if not isinstance(valor, list):
        return []
    limpios = []
    for m in valor:
        if not isinstance(m, str):
            continue
        m = " ".join(m.split())          # quita espacios de más y saltos de línea
        if NOMBRE_MUNICIPIO.fullmatch(m) and m not in limpios:
            limpios.append(m)
    return limpios[:MAX_MUNICIPIOS]


def nombre_depto(valor):
    """Convierte nombre, abreviatura o código del INS al nombre oficial. None si no lo reconoce."""
    if valor is None:
        return None
    s = str(valor).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        return CODIGOS.get(s.zfill(2))
    return ALIAS.get(normalizar(s))


def validar(d):
    """Revisa lo que devolvió la IA. Devuelve un diccionario limpio, o None si no sirve."""
    if not d:
        return None
    pat = normalizar(d.get("patogeno"))
    pat = ALIAS_PATOGENO.get(pat, pat)
    depto = nombre_depto(d.get("departamento"))
    if pat not in PATOGENOS or depto is None:
        return None
    casos = d.get("casos")
    if isinstance(casos, str):                           # "1.200" o "1,200" -> 1200
        casos = casos.replace(".", "").replace(",", "").strip()
        casos = int(casos) if casos.isdigit() else None
    elif isinstance(casos, float) and casos.is_integer():  # 340.0 -> 340
        casos = int(casos)
    if not isinstance(casos, int) or isinstance(casos, bool) or casos < 0:
        casos = None

    fecha = d.get("fecha")
    try:
        f = date.fromisoformat(fecha)
        if f > date.today() or f < date.today() - timedelta(days=60):
            return None
    except (TypeError, ValueError):
        fecha = None

    return {"patogeno": pat.capitalize(), "tipo": PATOGENOS[pat], "departamento": depto,
            "municipios": limpiar_municipios(d.get("municipios")), "casos": casos, "fecha": fecha}