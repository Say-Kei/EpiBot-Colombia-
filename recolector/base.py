"""Base de datos de EpiBot (SQLite): un solo archivo, datos/epibot.db.

Dos tablas:
- casos_semanales: histórico oficial del INS desde 2020 (casos por departamento y semana).
- alertas: todas las alertas que genera EpiBot. Nunca se borran, así quedan para el historial.
  Hay una por patógeno + departamento + semana; si llegan noticias nuevas esa semana, se unen.
- procesadas: enlaces de noticias que la IA ya leyó, para no gastar tokens leyéndolas otra vez.
"""
import json
import sqlite3
from datetime import date
from contextlib import contextmanager
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "datos" / "epibot.db"
ANO_INICIO = 2020

ESQUEMA = """
CREATE TABLE IF NOT EXISTS casos_semanales (
    patogeno     TEXT    NOT NULL,
    evento       TEXT    NOT NULL,
    departamento TEXT    NOT NULL,
    ano          INTEGER NOT NULL,
    semana       INTEGER NOT NULL,
    casos        INTEGER NOT NULL,
    PRIMARY KEY (patogeno, evento, departamento, ano, semana)
);
CREATE INDEX IF NOT EXISTS idx_casos_depto ON casos_semanales (departamento, ano, semana);

CREATE TABLE IF NOT EXISTS alertas (
    id              TEXT PRIMARY KEY,
    patogeno        TEXT NOT NULL,
    tipo            TEXT,
    departamento    TEXT NOT NULL,
    nivel           TEXT NOT NULL,
    casos           INTEGER,
    esperado        INTEGER,
    resumen         TEXT,
    fecha_deteccion TEXT NOT NULL,
    municipios      TEXT,
    fuentes         TEXT
);
CREATE INDEX IF NOT EXISTS idx_alertas_fecha ON alertas (fecha_deteccion);
CREATE INDEX IF NOT EXISTS idx_alertas_depto ON alertas (departamento);

CREATE TABLE IF NOT EXISTS procesadas (
    url   TEXT PRIMARY KEY,
    fecha TEXT NOT NULL
);
"""


@contextmanager
def conectar(solo_lectura=False):
    """Abre la base, guarda los cambios al terminar y siempre la cierra (libera memoria).

    En solo lectura (la página web) no puede modificar nada.
    """
    if solo_lectura:
        con = sqlite3.connect(f"file:{RUTA}?mode=ro", uri=True)
    else:
        RUTA.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(RUTA)
        con.executescript(ESQUEMA)
    con.row_factory = sqlite3.Row  # cada fila se puede leer como diccionario
    try:
        yield con
        con.commit()
    finally:
        con.close()


# ---------- Escribir (lo usa el recolector) ----------
def guardar_historico(hist):
    """Reemplaza el histórico del INS con la tabla de ins.historico() (desde 2020)."""
    hist = hist[hist["ano"] >= ANO_INICIO]
    filas = [(r.patogeno, r.evento, r.departamento, int(r.ano), int(r.semana), int(r.casos))
             for r in hist.itertuples(index=False)]
    with conectar() as con:
        con.execute("DELETE FROM casos_semanales")
        con.executemany("INSERT INTO casos_semanales VALUES (?, ?, ?, ?, ?, ?)", filas)
    return len(filas)


def guardar_alertas(alertas):
    """Agrega las alertas nuevas. Si una alerta con el mismo id ya existe, la actualiza."""
    filas = [(a["id"], a["patogeno"], a["tipo"], a["departamento"], a["nivel"], a["casos"],
              a["esperado"], a["resumen"], a["fecha_deteccion"],
              json.dumps(a["municipios"], ensure_ascii=False),
              json.dumps(a["fuentes"], ensure_ascii=False))
             for a in alertas]
    with conectar() as con:
        con.executemany("INSERT OR REPLACE INTO alertas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        filas)
    return len(filas)


def marcar_procesadas(urls):
    """Anota los enlaces que la IA ya leyó (hoy)."""
    hoy = date.today().isoformat()
    with conectar() as con:
        con.executemany("INSERT OR IGNORE INTO procesadas VALUES (?, ?)",
                        [(u, hoy) for u in urls if u])


def urls_procesadas():
    """Conjunto con todos los enlaces que la IA ya leyó."""
    with conectar() as con:
        return {f[0] for f in con.execute("SELECT url FROM procesadas")}


# ---------- Leer (lo usan el recolector y la página) ----------
def _a_diccionario(fila):
    d = dict(fila)
    d["municipios"] = json.loads(d["municipios"] or "[]")
    d["fuentes"] = json.loads(d["fuentes"] or "[]")
    return d


def buscar_alertas(departamento=None, patogeno=None, nivel=None, desde=None, hasta=None,
                   limite=200, solo_lectura=True):
    """Alertas filtradas. Todos los filtros son opcionales y se pueden combinar."""
    condiciones, valores = [], []
    if departamento:
        condiciones.append("departamento = ?"); valores.append(departamento)
    if patogeno:
        condiciones.append("lower(patogeno) = lower(?)"); valores.append(patogeno)
    if nivel:
        condiciones.append("nivel = ?"); valores.append(nivel)
    if desde:
        condiciones.append("fecha_deteccion >= ?"); valores.append(desde)
    if hasta:
        condiciones.append("fecha_deteccion <= ?"); valores.append(hasta)
    donde = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    sql = f"SELECT * FROM alertas {donde} ORDER BY fecha_deteccion DESC LIMIT ?"
    with conectar(solo_lectura) as con:
        return [_a_diccionario(f) for f in con.execute(sql, [*valores, limite])]


def contar_alertas(solo_lectura=True):
    """Cuántas alertas hay en total (0 si la tabla está vacía)."""
    with conectar(solo_lectura) as con:
        return con.execute("SELECT COUNT(*) FROM alertas").fetchone()[0]


def una_alerta(id, solo_lectura=True):
    with conectar(solo_lectura) as con:
        fila = con.execute("SELECT * FROM alertas WHERE id = ?", [id]).fetchone()
    return _a_diccionario(fila) if fila else None


def serie_semanal(patogeno, departamento=None, desde_ano=ANO_INICIO, solo_lectura=True):
    """Casos por año y semana (todo el país si no se da departamento). Sirve para gráficas."""
    valores = [patogeno, desde_ano]
    filtro_depto = ""
    if departamento:
        filtro_depto = "AND departamento = ?"
        valores.append(departamento)
    sql = f"""SELECT ano, semana, SUM(casos) AS casos FROM casos_semanales
              WHERE lower(patogeno) = lower(?) AND ano >= ? {filtro_depto}
              GROUP BY ano, semana ORDER BY ano, semana"""
    with conectar(solo_lectura) as con:
        return [dict(f) for f in con.execute(sql, valores)]


def leer_historico():
    """Todo el histórico como tabla de pandas (para calcular lo esperado en el recolector)."""
    import pandas as pd  # se importa aquí para que la página web no cargue pandas (ahorra RAM)
    with conectar() as con:
        return pd.read_sql_query("SELECT * FROM casos_semanales", con)