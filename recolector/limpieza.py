"""Limpia las noticias antes de mandarlas a la IA."""
import html
import pandas as pd

# Solo pasan textos que mencionen alguno de estos patógenos
PATOGENOS = ("dengue|malaria|paludismo|tosferina|tos ferina|fiebre amarilla|oropouche"
             "|chikungunya|chikunguña|chicungunya")


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
    df = df[df["texto"].str.contains("colombia", case=False)]
    df["texto"] = df["texto"].str.slice(0, 6000)
    return df.reset_index(drop=True)