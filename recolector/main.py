"""Une todo: noticias + OMS -> limpieza -> IA -> validación -> alertas, comparadas con el INS."""
import json
import os
from datetime import date
from pathlib import Path

from recolector.ia import extraer, LimiteAgotado
from recolector.fuentes import noticias, oms, ins
from recolector.limpieza import limpiar
from recolector.validar import validar
from recolector.niveles import calcular_nivel

SALIDA = Path(__file__).resolve().parents[1] / "datos" / "alertas.json"


def main():
    # 1. Histórico del INS (XLSX + API, o el CSV compartido) para saber qué es "normal"
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
            "id": f"{pat}-{depto}-{date.today()}".lower().replace(" ", "-"),
            "patogeno": pat, "tipo": items[0][0]["tipo"], "departamento": depto,
            "municipios": sorted({m for d, _ in items for m in d["municipios"]}),
            "nivel": calcular_nivel(casos, esperado, len(fuentes), oficial),
            "casos": casos, "esperado": esperado,
            "resumen": resumen,
            "fecha_deteccion": str(date.today()), "fuentes": fuentes})

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    if not alertas:
        print("No se generaron alertas nuevas; dejo el alertas.json anterior")
        return
    SALIDA.write_text(json.dumps(alertas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(alertas), "alertas guardadas en", SALIDA)


if __name__ == "__main__":
    main()