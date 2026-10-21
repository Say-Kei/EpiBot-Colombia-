from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/panel")
def inicio():
    return render_template("inicio.html")

@app.route("/busqueda")
def busqueda():
    return render_template("busqueda.html")

@app.route("/alerta")
def alerta():
    return render_template("alerta.html")

@app.route("/fuentes")
def fuentes():
    return render_template("fuentes.html")

if __name__ == "__main__":
    app.run(debug=True)