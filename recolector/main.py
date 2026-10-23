import json
import os
from datetime import date, timedelta
from pathlib import Path

from recolector import base
from recolector.ia import extraer, LimiteAgotado
from recolector.fuentes import noticias, oms, ins
from recolector.limpieza import limpiar
from recolector.validar import validar, normalizar
from recolector.niveles import calcular_nivel

SALIDA = Path(__file__).resolve().parents[1] / "datos" / "alertas.json"


def main():
    # 1. Histórico del INS para saber qué es "normal": primero desde la base (rápido, poca RAM)
    hist = base.leer_historico()
    if hist.empty:
        print("La base no tiene histórico; lo armo desde el INS (ejecuta recolector.importar_historico)")
        hist = ins.historico()
    semana_hoy = date.today().isocalendar().week

    # 2. Noticias y OMS: limpiar y pasar cada texto por la IA
    df = limpiar(noticias.recolectar() + oms.recolectar())
    df = df.head(int(os.getenv("MAX_TEXTOS", "50")))
    print(len(df), "textos para la IA")

    grupos = {}
    try:
        for i, fila in enumerate(df.to_dict("records"), start=1):
            ok = validar(extraer(fila["texto"]))
            print(f"  {i}/{len(df)}", "->", f"{ok['patogeno']} en {ok['departamento']}" if ok else "descartado")
            if ok:
                fuente = {"nombre": fila["fuente"], "tipo": fila["tipo"], "url": fila["url"],
                          "fecha": str(fila["fecha"].date())}
                grupos.setdefault((ok["patogeno"], ok["departamento"]), []).append((ok, fuente))
    except LimiteAgotado as e:
        print("Paro la recolección:", e, "- guardo las alertas que ya tengo")

    # 3. Una alerta por patógeno + departamento, comparada con lo esperado
    alertas = []
    for (pat, depto), items in grupos.items():
        fuentes = [f for _, f in items]
        casos = max((d["casos"] for d, _ in items if d["casos"]), default=None)
        esperado = ins.esperado(hist, pat, depto, semana_hoy)
        oficial = any(f["tipo"] == "oficial" for f in fuentes)

        resumen = f"{len(fuentes)} fuente(s) reportan {pat.lower()} en {depto}."
        if esperado is not None:
            resumen += f" Lo normal para esta semana son unos {esperado} casos (INS)."

        alertas.append({
            "id": normalizar(f"{pat}-{depto}-{date.today()}").replace(" ", "-").replace(".", ""),
            "patogeno": pat, "tipo": items[0][0]["tipo"], "departamento": depto,
            "municipios": sorted({m for d, _ in items for m in d["municipios"]}),
            "nivel": calcular_nivel(casos, esperado, len(fuentes), oficial),
            "casos": casos, "esperado": esperado,
            "resumen": resumen,
            "fecha_deteccion": str(date.today()), "fuentes": fuentes})

    # 4. Guardar en la base (se acumulan) y dejar en alertas.json las de los últimos 30 días
    if alertas:
        base.guardar_alertas(alertas)
        print(len(alertas), "alertas guardadas en", base.RUTA)
    else:
        print("No se generaron alertas nuevas")

    hace_30 = str(date.today() - timedelta(days=30))
    recientes = base.buscar_alertas(desde=hace_30, limite=500, solo_lectura=False)
    if recientes:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        SALIDA.write_text(json.dumps(recientes, ensure_ascii=False, indent=2), encoding="utf-8")
        print(len(recientes), "alertas de los últimos 30 días en", SALIDA)


if __name__ == "__main__":
    main()