"""Datos OFICIALES: boletines del INS y de las secretarías de salud.

- recolectar_bes(): lo llama main.py en cada corrida. Busca el Boletín Epidemiológico Semanal (BES)
  más reciente que aún no se haya cargado, lo lee y lo guarda como fuente oficial. Igual que con
  las noticias, si ya lo leyó no lo vuelve a leer (tabla procesadas).
- guardar_oficiales(): une cada cifra oficial a la alerta de esta semana. La usan también
  cargar_bes.py (a mano) y cargar_oficial.py (cifras copiadas de boletines de secretarías).
"""
from datetime import date, timedelta

from recolector import base
from recolector.alertas import id_alerta, unir, exportar_json
from recolector.fuentes import bes, ins
from recolector.niveles import calcular_nivel
from recolector.validar import PATOGENOS, normalizar

MAX_DIAS = 30        # un boletín más viejo que esto ya no confirma la situación de esta semana
MIN_CASOS = 10       # con menos casos, una diferencia (ej. 2 frente a 1) es azar, no un brote
SEMANAS_ATRAS = 6    # el INS publica con 1 a 3 semanas de retraso: se buscan las últimas 6


def nivel_oficial(casos, esperado):
    """Nivel con la cifra oficial: casos del periodo frente a lo esperado para ese periodo."""
    if casos is None or esperado is None:
        return None
    if esperado == 0:
        return "moderado" if casos > 0 else "bajo"
    razon = casos / esperado
    if razon >= 2:
        nivel = "critico"
    elif razon >= 1.5:
        nivel = "alto"
    elif razon >= 1:
        nivel = "moderado"
    else:
        nivel = "bajo"
    if casos < MIN_CASOS and nivel in ("critico", "alto"):
        nivel = "moderado"
    return nivel


def guardar_oficiales(registros, hoy, simular=False, hist=None, mostrar=True):
    """Une cada dato oficial a la alerta de esta semana de ese patógeno y departamento.

    registros: diccionarios con patogeno, tipo, departamento, casos, esperado, municipios, fuente
    (y opcionalmente "detalle", un texto corto para el resumen). La cifra oficial manda sobre la
    de prensa y el nivel lo decide la comparación oficial casos / esperado.
    """
    hist = base.leer_historico() if hist is None else hist
    semana = hoy.isocalendar().week
    alertas = []
    for d in registros:
        nueva = {"id": id_alerta(d["patogeno"], d["departamento"], hoy),
                 "patogeno": d["patogeno"], "tipo": d["tipo"], "departamento": d["departamento"],
                 "municipios": d.get("municipios") or [], "casos": d["casos"],
                 "fecha_deteccion": str(hoy), "fuentes": [d["fuente"]]}
        a = unir(base.una_alerta(nueva["id"], solo_lectura=False), nueva)
        if d["casos"] is not None:
            a["casos"] = d["casos"]                     # la cifra oficial manda sobre la de prensa
        esperado = d["esperado"] if d["esperado"] is not None else ins.esperado(
            hist, d["patogeno"], d["departamento"], semana)
        a["esperado"] = esperado
        a["nivel"] = (nivel_oficial(a["casos"], esperado)
                      or calcular_nivel(a["casos"], esperado, len(a["fuentes"]), True))
        a["resumen"] = f"Confirmado por fuente oficial ({d['fuente']['nombre']})."
        if d.get("detalle"):
            a["resumen"] += " " + d["detalle"]
        elif esperado is not None:
            a["resumen"] += f" Lo normal para esta semana son unos {esperado} casos (INS)."
        alertas.append(a)
        if mostrar:
            print(f"  {a['patogeno']:<12} {a['departamento']:<26} nivel {a['nivel']:<9} "
                  f"casos {a['casos']}  esperado {esperado}  ({len(a['fuentes'])} fuentes)")

    if simular or not alertas:
        print("Simulación: no se guardó nada." if simular else "No hay nada que guardar.")
        return alertas
    base.guardar_alertas(alertas)
    exportar_json(hoy)
    print(f"{len(alertas)} alertas oficiales guardadas en {base.RUTA}")
    return alertas


def registros_desde_bes(ruta, hoy):
    """Lee un PDF del BES y lo convierte en registros para guardar_oficiales()."""
    corte, semana, filas = bes.leer_bes(ruta)
    if not semana:
        raise bes.FormatoCambiado("no encontré el número de semana en el boletín")
    if corte < hoy - timedelta(days=MAX_DIAS):
        raise bes.FormatoCambiado(f"el boletín es del {corte}: tiene más de {MAX_DIAS} días")
    url = bes.URL_BES.format(ano=corte.year, semana=semana)
    registros = []
    for f in filas:
        if f["observado"] == 0 and f["acumulado"] == 0:
            continue                                    # sin casos: queda "Sin alertas reportadas"
        registros.append({
            "patogeno": f["patogeno"], "tipo": PATOGENOS[normalizar(f["patogeno"])],
            "departamento": f["departamento"], "casos": f["observado"], "esperado": f["esperado"],
            "municipios": [],
            "fuente": {"nombre": f"INS · BES semana {semana}", "tipo": "oficial", "url": url,
                       "fecha": str(corte)},
            "detalle": (f"{f['observado']} casos en las {f['periodo']} frente a {f['esperado']} esperados; "
                        f"{f['acumulado']} en lo que va del año."
                        if f["periodo"] == "últimas 4 semanas" else
                        f"{f['acumulado']} casos en el año frente a {f['esperado']} esperados.")})
    return corte, semana, url, registros


def recolectar_bes(hoy=None, hist=None):
    """Busca el BES más reciente que aún no se ha cargado y lo guarda. No gasta tokens.

    Devuelve cuántas alertas oficiales guardó (0 si no había boletín nuevo).
    """
    hoy = hoy or date.today()
    ya = base.urls_procesadas()
    # Semana epidemiológica aproximada de hoy; se prueban de la más nueva a la más vieja
    aprox = (hoy - date(hoy.year, 1, 1)).days // 7 + 1
    for semana in range(aprox, max(aprox - SEMANAS_ATRAS, 0), -1):
        url = bes.URL_BES.format(ano=hoy.year, semana=semana)
        if url in ya:
            print(f"BES del INS: el de la semana {semana} ya está cargado")
            return 0
        try:
            ruta = bes.descargar(hoy.year, semana)
        except bes.NoPublicado:
            continue
        except Exception as e:                          # sin internet, INS caído...
            print(f"BES del INS: no se pudo revisar la semana {semana} ({e})")
            return 0
        try:
            corte, semana, url, registros = registros_desde_bes(ruta, hoy)
        except bes.FormatoCambiado as e:
            print(f"BES del INS semana {semana}: no se carga, para no leer mal ({e}). "
                  "Pruebo con la semana anterior.")
            continue
        print(f"BES del INS semana {semana} (corte {corte}): {len(registros)} cifras oficiales")
        guardar_oficiales(registros, hoy, hist=hist, mostrar=False)
        base.marcar_procesadas([url])
        return len(registros)
    print(f"BES del INS: no hay boletín publicado en las últimas {SEMANAS_ATRAS} semanas")
    return 0
