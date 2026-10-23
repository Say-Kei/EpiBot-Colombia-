import json
import sqlite3
from pathlib import Path

from flask import Flask, render_template, jsonify, abort, request

from recolector import base

app = Flask(__name__)
DATOS = Path(__file__).parent / "datos"


# ---------- Plan B: los JSON, por si la base no existe o falla ----------
def cargar_json():
    """Primero alertas.json; si no existe, está dañado o vacío, alertas_respaldo.json."""
    for nombre in ("alertas.json", "alertas_respaldo.json"):
        try:
            with open(DATOS / nombre, encoding="utf-8") as f:
                datos = json.load(f)
            if datos:
                return datos
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    return []   # va FUERA del for: solo si ninguno de los dos sirvió


def filtrar_json(alertas, departamento, patogeno, nivel, desde, hasta):
    """Los mismos filtros que la base, pero sobre la lista del JSON."""
    res = []
    for a in alertas:
        if departamento and a.get("departamento") != departamento:
            continue
        if patogeno and a.get("patogeno", "").lower() != patogeno.lower():
            continue
        if nivel and a.get("nivel") != nivel:
            continue
        if desde and a.get("fecha_deteccion", "") < desde:
            continue
        if hasta and a.get("fecha_deteccion", "") > hasta:
            continue
        res.append(a)
    return res


def buscar(**filtros):
    """Busca en la base. Solo usa los JSON si la base no existe, falla o no tiene alertas.

    Si la base sí tiene alertas y el filtro da 0 resultados, devuelve [] (eso es correcto:
    no hay alertas con ese filtro), en vez de mostrar datos del JSON que no coinciden.
    """
    try:
        if base.contar_alertas() > 0:
            return base.buscar_alertas(**filtros)
    except sqlite3.Error:
        pass
    res = filtrar_json(cargar_json(), filtros.get("departamento"), filtros.get("patogeno"),
                       filtros.get("nivel"), filtros.get("desde"), filtros.get("hasta"))
    return res[:filtros.get("limite", 200)]


def buscar_una(id):
    try:
        a = base.una_alerta(id)
        if a:
            return a
    except sqlite3.Error:
        pass
    return next((a for a in cargar_json() if a.get("id") == id), None)


def filtros_de_la_url():
    """Lee ?departamento=...&patogeno=...&nivel=...&desde=...&hasta=... de la dirección."""
    return {"departamento": request.args.get("departamento") or None,
            "patogeno": request.args.get("patogeno") or None,
            "nivel": request.args.get("nivel") or None,
            "desde": request.args.get("desde") or None,   # AAAA-MM-DD
            "hasta": request.args.get("hasta") or None}   # AAAA-MM-DD


# ---------- Páginas ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/panel")
def inicio():
    return render_template("inicio.html", activo="panel")


@app.route("/busqueda")
def busqueda():
    return render_template("busqueda.html", activo="busqueda")


@app.route("/fuentes")
def fuentes():
    return render_template("fuentes.html", activo="fuentes")


@app.route("/alerta")
@app.route("/alerta/<id>")
def alerta(id=None):
    a = buscar_una(id) if id else next(iter(buscar(limite=1)), None)
    if a is None:
        abort(404)
    return render_template("alerta.html", activo="alerta", alerta=a)


# ---------- API (datos en JSON para el JavaScript) ----------
@app.route("/api/alertas")
def api_alertas():
    return jsonify(buscar(**filtros_de_la_url()))


@app.route("/api/alertas/<id>")
def api_alerta(id):
    a = buscar_una(id)
    return jsonify(a) if a else (jsonify({"error": "no existe"}), 404)


@app.route("/api/historico")
def api_historico():
    patogeno = request.args.get("patogeno")
    if not patogeno:
        return jsonify({"error": "falta ?patogeno="}), 400
    try:
        serie = base.serie_semanal(patogeno, request.args.get("departamento") or None,
                                   int(request.args.get("desde_ano", base.ANO_INICIO)))
    except (sqlite3.Error, ValueError):
        serie = []
    return jsonify(serie)


if __name__ == "__main__":
    app.run(debug=True)