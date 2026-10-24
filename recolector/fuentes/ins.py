import json
import os
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from recolector.validar import nombre_depto

load_dotenv()

URL = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
CRUDOS = Path(__file__).resolve().parents[2] / "datos" / "crudos"
CARPETA_XLSX = CRUDOS / "ins"
HISTORICO = CRUDOS.parent / "historico_ins.csv"
LOTE = 50000

# Patógeno (como lo usa validar.py) -> texto que aparece en el nombre del evento.
# "DENGUE" también trae DENGUE GRAVE; "MALARIA" trae las formas mixtas y complicada.
EVENTOS = {"Dengue": "DENGUE", "Malaria": "MALARIA",
           "Fiebre amarilla": "FIEBRE AMARILLA", "Oropouche": "OROPOUCHE",
           "Chikungunya": "CHIKUNGUNYA"}

# Eventos que NO se cuentan (la persona ya puede estar contada como caso)
EXCLUIR = "MORTALIDAD"
# Años en que un patógeno solo tiene parte de sus eventos (no sirven para el total)
INCOMPLETOS = {"Malaria": {2023, 2024, 2025}}  # en SIVIGILA solo hay malaria complicada

# Nombres de las columnas en los XLSX de SIVIGILA
COLUMNAS_XLSX = {"evento": "nombre_evento", "ano": "ano", "semana": "semana",
                 "departamento": "departamento_ocurrencia"}

NECESARIAS = set(COLUMNAS_XLSX.values()) | {"ajuste"}

VACIO = pd.DataFrame(columns=["evento", "ano", "semana", "departamento", "conteo"])


# ---------- Fuente 1: XLSX descargados de SIVIGILA ----------
def leer_xlsx():
    """Lee todos los .xlsx de datos/crudos/ins en una sola tabla."""
    tablas = []
    for a in sorted(CARPETA_XLSX.glob("*.xlsx")):
        print("Leyendo", a.name)
        # usecols: solo carga las columnas que se usan (ahorra mucha RAM)
        df = pd.read_excel(a, usecols=lambda c: str(c).strip().lower() in NECESARIAS)
        df.columns = [str(c).strip().lower() for c in df.columns]
        faltan = [c for c in COLUMNAS_XLSX.values() if c not in df.columns]
        if faltan:
            print("  Se salta: no tiene las columnas", faltan)
            continue
        tablas.append(df)
    if not tablas:
        print("No hay XLSX en", CARPETA_XLSX)
        return pd.DataFrame()
    return pd.concat(tablas, ignore_index=True)


def desde_xlsx(xlsx, texto):
    """Filtra un patógeno y deja las columnas comunes. Cada fila del XLSX es un caso."""
    if xlsx.empty:
        return VACIO.copy()
    c = COLUMNAS_XLSX
    ev = xlsx[c["evento"]].astype(str).str.upper().str.strip()
    df = xlsx[ev.str.contains(texto, na=False) & ~ev.str.contains(EXCLUIR, na=False)]
    # Ajuste 6 = caso descartado, D = error de digitación
    if "ajuste" in df.columns:
        df = df[~df["ajuste"].astype(str).str.strip().str.upper().isin(["6", "D"])]
    return pd.DataFrame({"evento": df[c["evento"]].astype(str).str.upper().str.strip(),
                         "ano": pd.to_numeric(df[c["ano"]], errors="coerce"),
                         "semana": pd.to_numeric(df[c["semana"]], errors="coerce"),
                         "departamento": df[c["departamento"]],
                         "conteo": 1})


# ---------- Fuente 2: API de datos.gov.co ----------
def descargar(texto):
    """Baja de la API solo el evento pedido, de a 50.000 filas."""
    headers = {}
    if os.getenv("DATOS_GOV_TOKEN"):
        headers["X-App-Token"] = os.getenv("DATOS_GOV_TOKEN")
    filas, offset = [], 0
    while True:
        params = {"$select": "nombre_evento, ano, semana, departamento_ocurrencia, conteo",
                  "$where": (f"upper(nombre_evento) like '%{texto}%' "
                             f"AND upper(nombre_evento) not like '%{EXCLUIR}%'"),
                  "$order": ":id", "$limit": LOTE, "$offset": offset}
        r = requests.get(URL, params=params, headers=headers, timeout=60)
        r.raise_for_status()
        lote = r.json()
        filas += lote
        if len(lote) < LOTE:
            return filas
        offset += LOTE


def desde_api(patogeno, texto):
    """Descarga, guarda los crudos y deja las columnas comunes."""
    try:
        filas = descargar(texto)
    except requests.RequestException as e:
        print("datos.gov.co no disponible:", e)
        return VACIO.copy()
    nombre = patogeno.lower().replace(" ", "_")
    (CRUDOS / f"ins_{nombre}_{date.today()}.json").write_text(
        json.dumps(filas, ensure_ascii=False), encoding="utf-8")
    if not filas:
        return VACIO.copy()
    df = pd.DataFrame(filas)
    return pd.DataFrame({"evento": df["nombre_evento"].astype(str).str.upper().str.strip(),
                         "ano": pd.to_numeric(df["ano"], errors="coerce"),
                         "semana": pd.to_numeric(df["semana"], errors="coerce"),
                         "departamento": df["departamento_ocurrencia"],
                         "conteo": pd.to_numeric(df["conteo"], errors="coerce")})


# ---------- Unir las dos fuentes ----------
def historico(usar_cache=True):
    """Tabla de casos por patógeno, evento, departamento, año y semana."""
    # Si ya se armó hoy, se lee el CSV y no se vuelve a descargar
    if usar_cache and HISTORICO.exists() and date.fromtimestamp(HISTORICO.stat().st_mtime) == date.today():
        return pd.read_csv(HISTORICO)

    CRUDOS.mkdir(parents=True, exist_ok=True)
    xlsx = leer_xlsx()
    partes = []
    for patogeno, texto in EVENTOS.items():
        xl = desde_xlsx(xlsx, texto)
        api = desde_api(patogeno, texto)
        api = api[~api["ano"].isin(set(xl["ano"].dropna()))]  # si un año está en los dos, gana el XLSX
        df = pd.concat([api, xl], ignore_index=True).dropna()
        df["departamento"] = df["departamento"].map(nombre_depto)
        df = df.dropna(subset=["departamento"])
        df["patogeno"] = patogeno
        print(f"{patogeno}: {len(xl)} filas XLSX, {len(api)} filas API, "
              f"eventos: {sorted(df['evento'].unique())}")
        partes.append(df)

    hist = (pd.concat(partes, ignore_index=True)
              .groupby(["patogeno", "evento", "departamento", "ano", "semana"])["conteo"].sum()
              .reset_index(name="casos"))
    hist.to_csv(HISTORICO, index=False)
    if not hist.empty:
        print("Años en el histórico:", sorted(hist["ano"].astype(int).unique()))
    return hist


# ---------- Lo esperado para una semana ----------
def esperado(hist, patogeno, departamento, semana, evento=None, anos=3):
    """Promedio de casos de esa semana del año en los últimos `anos` años con datos.

    Sin `evento` suma todo el patógeno (ej. dengue + dengue grave).
    Con `evento` cuenta solo ese (ej. evento="DENGUE GRAVE").
    Sin `evento` se saltan los años de INCOMPLETOS.
    """
    g = hist[(hist["patogeno"] == patogeno) & (hist["departamento"] == departamento)]
    if evento:
        g = g[g["evento"] == evento.upper()]
    else:
        g = g[~g["ano"].isin(INCOMPLETOS.get(patogeno, set()))]
    if g.empty:
        return None
    ultimos = sorted(g["ano"].unique())[-anos:]
    total = g[(g["ano"].isin(ultimos)) & (g["semana"] == semana)]["casos"].sum()
    return round(total / len(ultimos))  # los años sin casos esa semana cuentan como 0