from django.db import connection

CARTAS_POR_RODADA = 10

NOMES = {
    "todos": "Baralho completo",
    "sql": "SQL",
    "python": "Python",
    "logica": "Lógica",
    "tech": "Tecnologia",
}

NAIPES = {
    "todos": "★",
    "sql": "♦",
    "python": "♠",
    "logica": "♥",
    "tech": "♣",
}

VALIDOS = list(NOMES.keys())


def listar():
    with connection.cursor() as cur:
        cur.execute("SELECT categoria, COUNT(*) FROM jogo_pergunta GROUP BY categoria")
        contagem = dict(cur.fetchall())

    baralhos = [
        {
            "chave": "todos",
            "nome": NOMES["todos"],
            "naipe": NAIPES["todos"],
            "cartas": sum(contagem.values()),
        }
    ]
    for chave in ("sql", "python", "logica", "tech"):
        baralhos.append(
            {
                "chave": chave,
                "nome": NOMES[chave],
                "naipe": NAIPES[chave],
                "cartas": contagem.get(chave, 0),
            }
        )
    return baralhos


def sortear(baralho):
    if baralho == "todos":
        query = "SELECT id FROM jogo_pergunta ORDER BY RANDOM() LIMIT %s"
        parametros = [CARTAS_POR_RODADA]
    else:
        query = (
            "SELECT id FROM jogo_pergunta WHERE categoria = %s "
            "ORDER BY RANDOM() LIMIT %s"
        )
        parametros = [baralho, CARTAS_POR_RODADA]

    with connection.cursor() as cur:
        cur.execute(query, parametros)
        return [linha[0] for linha in cur.fetchall()]
