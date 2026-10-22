def calcular_nivel(casos, esperado, num_fuentes, hay_oficial):
    """Decide el nivel con una regla fija, sin IA."""
    razon = casos / esperado if casos and esperado else 0

    if razon >= 2 or num_fuentes >= 3:
        return "critico"
    if razon >= 1.5 or num_fuentes >= 2:
        return "alto"
    if hay_oficial:
        return "moderado"
    return "bajo"