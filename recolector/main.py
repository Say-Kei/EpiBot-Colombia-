"""Recolector de EpiBot: noticias + OMS -> IA -> alertas en la base y en alertas.json.

    python -m recolector.main

Reglas para no duplicar:
- Una alerta por patógeno + departamento + SEMANA (id: dengue-cordoba-2026-s43).
- Si esa alerta ya existe, se UNE con lo nuevo (fuentes, municipios, casos) en vez de reemplazarla.
- La IA no vuelve a leer noticias que ya leyó (tabla procesadas), así no se gastan tokens dos veces.
"""
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


def id_alerta(pat, depto, hoy):
    """dengue-cordoba-2026-s43: sin tildes, sin espacios, por semana."""
    ano, semana, _ = hoy.isocalendar()
    return normalizar(f"{pat}-{depto}-{ano}-s{semana:02d}").replace(" ", "-").replace(".", "")


def unir(vieja, nueva):
    """Junta la alerta que ya estaba en la base con la nueva de esta ejecución."""
    if not vieja:
        return nueva
    urls = {f["url"] for f in vieja["fuentes"]}
    fuentes = vieja["fuentes"] + [f for f in nueva["fuentes"] if f["url"] not in urls]
    casos = [c for c in (vieja["casos"], nueva["casos"]) if c is not None]
    return {**nueva,
            "fuentes": fuentes,
            "municipios": sorted(set(vieja["municipios"]) | set(nueva["municipios"])),
            "casos": max(casos) if casos else None,
            "fecha_deteccion": vieja["fecha_deteccion"]}   # se conserva el día en que apareció


def main():
    hoy = date.today()
    semana_hoy = hoy.isocalendar().week

    # 1. Histórico del INS para saber qué es "normal": primero desde la base (rápido, poca RAM)
    hist = base.leer_historico()
    if hist.empty:
        print("La base no tiene histórico; lo armo desde el INS (ejecuta recolector.importar_historico)")
        hist = ins.historico()

    # 2. Noticias y OMS: limpiar, quitar las que la IA ya leyó y priorizar oficiales y recientes
    df = limpiar(noticias.recolectar() + oms.recolectar())
    if not df.empty:
        ya_leidas = base.urls_procesadas()
        antes = len(df)
        df = df[~df["url"].isin(ya_leidas)]
        print(f"{antes - len(df)} noticias ya leídas en otras ejecuciones (no gastan tokens)")
        df = df.assign(_oficial=df["tipo"] == "oficial")
        df = df.sort_values(["_oficial", "fecha"], ascending=False).drop(columns="_oficial")
    df = df.head(int(os.getenv("MAX_TEXTOS", "30")))
    print(len(df), "textos nuevos para la IA (máximo MAX_TEXTOS =", os.getenv("MAX_TEXTOS", "30"), ")")

    grupos, leidas = {}, []
    try:
        for i, fila in enumerate(df.to_dict("records"), start=1):
            respuesta = extraer(fila["texto"])
            if respuesta is not None:          # la IA sí respondió (aunque sea "no sirve")
                leidas.append(fila["url"])     # si falló la API, no se marca y se reintenta otro día
                base.marcar_procesadas([fila["url"]])
            ok = validar(respuesta)
            print(f"  {i}/{len(df)}", "->", f"{ok['patogeno']} en {ok['departamento']}" if ok else "descartado")
            if ok:
                fuente = {"nombre": fila["fuente"], "tipo": fila["tipo"], "url": fila["url"],
                          "fecha": str(fila["fecha"].date())}
                grupos.setdefault((ok["patogeno"], ok["departamento"]), []).append((ok, fuente))
    except LimiteAgotado as e:
        print("Paro la recolección:", e, "- guardo las alertas que ya tengo")
    base.marcar_procesadas(leidas)

    # 3. Una alerta por patógeno + departamento + semana, unida con la que ya existiera
    alertas = []
    for (pat, depto), items in grupos.items():
        nueva = {
            "id": id_alerta(pat, depto, hoy),
            "patogeno": pat, "tipo": items[0][0]["tipo"], "departamento": depto,
            "municipios": sorted({m for d, _ in items for m in d["municipios"]}),
            "casos": max((d["casos"] for d, _ in items if d["casos"]), default=None),
            "fecha_deteccion": str(hoy), "fuentes": [f for _, f in items]}
        a = unir(base.una_alerta(nueva["id"], solo_lectura=False), nueva)

        # El nivel y el resumen se calculan con TODAS las fuentes de la semana
        esperado = ins.esperado(hist, pat, depto, semana_hoy)
        oficial = any(f["tipo"] == "oficial" for f in a["fuentes"])
        a["esperado"] = esperado
        a["nivel"] = calcular_nivel(a["casos"], esperado, len(a["fuentes"]), oficial)
        a["resumen"] = f"{len(a['fuentes'])} fuente(s) reportan {pat.lower()} en {depto} esta semana."
        if esperado is not None:
            a["resumen"] += f" Lo normal para esta semana son unos {esperado} casos (INS)."
        alertas.append(a)

    # 4. Guardar en la base (se acumulan) y dejar en alertas.json las de los últimos 30 días
    if alertas:
        base.guardar_alertas(alertas)
        print(len(alertas), "alertas nuevas o actualizadas en", base.RUTA)
    else:
        print("No se generaron alertas nuevas")

    hace_30 = str(hoy - timedelta(days=30))
    recientes = base.buscar_alertas(desde=hace_30, limite=500, solo_lectura=False)
    if recientes:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        SALIDA.write_text(json.dumps(recientes, ensure_ascii=False, indent=2), encoding="utf-8")
        print(len(recientes), "alertas de los últimos 30 días en", SALIDA)


if __name__ == "__main__":
    main()