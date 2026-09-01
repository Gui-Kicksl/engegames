import json

from django.db import connection

COLUNAS = "id, categoria, dificuldade, enunciado, codigo, linguagem, alternativas, correta, explicacao"


def buscar(pergunta_id):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id, categoria, dificuldade, enunciado, codigo, linguagem, "
            "alternativas, correta, explicacao FROM jogo_pergunta WHERE id = %s",
            [pergunta_id],
        )
        linha = cur.fetchone()

    if linha is None:
        return None

    return {
        "id": linha[0],
        "categoria": linha[1],
        "dificuldade": linha[2],
        "enunciado": linha[3],
        "codigo": linha[4],
        "linguagem": linha[5],
        "alternativas": _lista(linha[6]),
        "correta": linha[7],
        "explicacao": linha[8],
    }


def _lista(valor):
    if isinstance(valor, str):
        return json.loads(valor)
    return valor
