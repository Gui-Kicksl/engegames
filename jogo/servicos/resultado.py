import json

from django.db import connection

from . import baralhos


def montar(partida):
    chave = partida.id.hex

    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT p.categoria,
                   COUNT(*),
                   SUM(CASE WHEN r.certa THEN 1 ELSE 0 END),
                   AVG(r.segundos)
            FROM jogo_resposta r
            JOIN jogo_pergunta p ON p.id = r.pergunta_id
            WHERE r.partida_id = %s
            GROUP BY p.categoria
            ORDER BY p.categoria
            """,
            [chave],
        )
        por_categoria = [
            {
                "categoria": linha[0],
                "naipe": baralhos.NAIPES.get(linha[0], "★"),
                "nome": baralhos.NOMES.get(linha[0], linha[0]),
                "total": linha[1],
                "acertos": linha[2],
                "tempo_medio": round(linha[3] or 0, 1),
            }
            for linha in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT p.enunciado, p.alternativas, p.correta, p.explicacao
            FROM jogo_resposta r
            JOIN jogo_pergunta p ON p.id = r.pergunta_id
            WHERE r.partida_id = %s AND r.certa = 0
            ORDER BY r.id
            """,
            [chave],
        )
        erros = []
        for linha in cur.fetchall():
            alternativas = linha[1]
            if isinstance(alternativas, str):
                alternativas = json.loads(alternativas)
            erros.append(
                {
                    "enunciado": linha[0],
                    "correta": alternativas[linha[2]],
                    "explicacao": linha[3],
                }
            )

        cur.execute(
            "SELECT COUNT(*), AVG(segundos) FROM jogo_resposta WHERE partida_id = %s",
            [chave],
        )
        total, tempo_medio = cur.fetchone()

    acertos = sum(item["acertos"] for item in por_categoria)

    return {
        "pontos": partida.pontos,
        "acertos": acertos,
        "total": total or 0,
        "melhor_sequencia": partida.melhor_sequencia,
        "tempo_medio": round(tempo_medio or 0, 1),
        "por_categoria": por_categoria,
        "erros": erros,
    }
