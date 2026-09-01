PONTOS_BASE = 100
BONUS_MAXIMO = 50
SEGUNDOS_POR_CARTA = 25


def multiplicador(sequencia):
    if sequencia >= 8:
        return 2.0
    if sequencia >= 5:
        return 1.5
    if sequencia >= 3:
        return 1.2
    return 1.0


def calcular(segundos, sequencia, usou_descarte):
    sobrou = max(0, SEGUNDOS_POR_CARTA - segundos)
    bonus = round(BONUS_MAXIMO * sobrou / SEGUNDOS_POR_CARTA)
    total = round((PONTOS_BASE + bonus) * multiplicador(sequencia))
    if usou_descarte:
        total = round(total / 2)
    return total
