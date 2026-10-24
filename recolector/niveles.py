# Seguridad / calidad: una noticia falsa o mal leída por la IA no debe poner a un departamento
# en rojo. Por eso:
# 1. Crítico solo si hay al menos una fuente oficial (INS, OMS...). Sin fuente oficial, máximo Alto.
#    (Requerimientos: "una señal no confirmada nunca vuelve rojo un municipio por sí sola").
# 2. Si los casos son más de 20 veces lo esperado, la cifra no se usa: casi siempre es un total
#    nacional o acumulado que la IA asignó a un departamento.
CRITICO_SOLO_CON_OFICIAL = True
MAX_RAZON_CREIBLE = 20


def calcular_nivel(casos, esperado, num_fuentes, hay_oficial):
    """Decide el nivel con una regla fija, sin IA."""
    razon = casos / esperado if casos and esperado else 0
    if razon > MAX_RAZON_CREIBLE:
        razon = 0   # cifra no creíble: se decide solo por las fuentes

    if razon >= 2 or num_fuentes >= 3:
        nivel = "critico"
    elif razon >= 1.5 or num_fuentes >= 2:
        nivel = "alto"
    elif hay_oficial:
        nivel = "moderado"
    else:
        nivel = "bajo"

    if nivel == "critico" and CRITICO_SOLO_CON_OFICIAL and not hay_oficial:
        nivel = "alto"
    return nivel