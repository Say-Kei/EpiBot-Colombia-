import json, os
from flask import Flask, render_template, abort, jsonify

app = Flask(__name__)
RUTA = os.path.join(os.path.dirname(__file__), "data", "dengue.json")
PAGINAS = [
    # Páginas de la rama frone
    "que-es", "sintomas", "tratamiento", "prevencion", "panel", "centros",
    # Páginas nuevas de EpiBot
    "zona", "enfermedades", "mapa", "como-funciona",
]
_cache = {"mtime": 0, "datos": {}}


def cargar():
    """Relee data/dengue.json solo cuando el archivo cambia."""
    m = os.path.getmtime(RUTA)
    if m != _cache["mtime"]:
        with open(RUTA, encoding="utf-8") as f:
            _cache["datos"] = json.load(f)
        _cache["mtime"] = m
    return _cache["datos"]


@app.context_processor
def inyectar_datos():
    return {"datos": cargar()}   # {{ datos.casos_total }} en cualquier plantilla


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dengue")
def api_dengue():
    return jsonify(cargar())


@app.route("/<pagina>")
def pagina(pagina):
    pagina = pagina.removesuffix(".html")   # acepta /mapa y /mapa.html
    if pagina == "index":
        return index()
    if pagina not in PAGINAS:
        abort(404)
    return render_template(f"{pagina}.html")


if __name__ == "__main__":
    app.run(debug=True)