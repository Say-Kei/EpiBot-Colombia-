"""Piezas comunes para armar alertas: las usan main.py (noticias) y oficial.py (boletines)."""
import json
from datetime import timedelta
from pathlib import Path

from recolector import base
from recolector.validar import normalizar

try:   # filtro de seguridad de municipios (validar.py nuevo); si no existe, se dejan como vienen
    from recolector.validar import limpiar_municipios
except ImportError:
    def limpiar_municipios(valor):
        return [m for m in (valor or []) if isinstance(m, str)]

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
            # limpiar_municipios: también filtra lo que ya estaba guardado antes de los filtros
            "municipios": sorted(set(limpiar_municipios(vieja["municipios"])) | set(nueva["municipios"])),
            "casos": max(casos) if casos else None,
            "fecha_deteccion": vieja["fecha_deteccion"]}   # se conserva el día en que apareció


def exportar_json(hoy):
    """Deja en alertas.json las alertas de los últimos 30 días (la copia de respaldo de la web)."""
    recientes = base.buscar_alertas(desde=str(hoy - timedelta(days=30)), limite=500, solo_lectura=False)
    if recientes:
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        SALIDA.write_text(json.dumps(recientes, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(recientes)