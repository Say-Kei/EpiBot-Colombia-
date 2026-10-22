import json
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)
DATOS = Path(__file__).parent / "datos"

def cargar_alertas():
    for nombre in ("alertas.json",
                   "alertas_respaldo.json"):
        try:
            with open (DATOS / nombre, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        return[]

def buscar(id):
    return next((a for a in cargar_alertas() if a[id] == id), None)

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
    alertas = cargar_alertas()
    a = buscar(id) if id else (alertas[0] if alertas else None)
    if a is None:
        abort(404)
    return render_template("alerta.html", activo="alerta", alerta=a)

@app.route("/api/alertas")
def api_alertas():
    return jsonify(cargar_alertas())

@app.route("/api/alertas/<id>")
def api_alerta(id):
    a = buscar(id)
    return jsonify(a) if a else (jsonify({"error": "no existe"}), 404)


if __name__ == "__main__":
    app.run(debug=True)

