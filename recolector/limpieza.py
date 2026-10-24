"""Limpia las noticias antes de mandarlas a la IA."""
import html
import re
import pandas as pd

from recolector.validar import DEPARTAMENTOS, normalizar
from recolector.fuentes.noticias import CIUDADES_DENGUE

# Solo pasan textos que mencionen alguno de estos patógenos
PATOGENOS = ("dengue|malaria|paludismo|fiebre amarilla|oropouche"
             "|chikungunya|chikunguña|chicungunya")


# "colombia" + departamentos + ciudades, sin tildes. \b evita coincidencias dentro de otras palabras
_LUGARES = ["colombia"] + [normalizar(d) for d in DEPARTAMENTOS + CIUDADES_DENGUE]
LUGARES_COLOMBIA = r"\b(?:" + "|".join(re.escape(l) for l in _LUGARES) + r")\b"


def limpiar(filas):
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    df["texto"] = df["titulo"].fillna("") + ". " + df["texto"].fillna("")
    df["texto"] = df["texto"].str.replace(r"<[^>]+>", " ", regex=True)        # quita HTML
    df["texto"] = df["texto"].map(html.unescape)                               
    df["texto"] = df["texto"].str.replace(r"\s+", " ", regex=True).str.strip()
    df = df.drop_duplicates(subset=["url"]).drop_duplicates(subset=["titulo"])
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", utc=True)
    hace_60 = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=60)
    df = df[df["fecha"] >= hace_60]                                            # últimos 60 días
    df = df[df["texto"].str.contains(PATOGENOS, case=False)]
    # Que hable de Colombia: basta con que diga "Colombia" o el nombre de un departamento o
    # de una ciudad buscada (una noticia de "dengue en Montería" no siempre dice "Colombia")
    df = df[df["texto"].map(normalizar).str.contains(LUGARES_COLOMBIA)]
    df["texto"] = df["texto"].str.slice(0, 1500)
    return df.reset_index(drop=True)