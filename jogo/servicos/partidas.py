import random

from django.utils import timezone

from ..models import Partida
from . import baralhos, perguntas, pontuacao


def criar(baralho):
    cartas = baralhos.sortear(baralho)
    if not cartas:
        return None
    return Partida.objects.create(baralho=baralho, cartas=cartas)


def buscar(partida_id):
    return Partida.objects.filter(pk=partida_id).first()


def acabou(partida):
    return partida.indice >= len(partida.cartas)


def entregar_carta(partida):
    pergunta = perguntas.buscar(partida.cartas[partida.indice])
    if pergunta is None:
        return None

    partida.carta_entregue_em = timezone.now()
    partida.save()

    return {
        "numero": partida.indice + 1,
        "total": len(partida.cartas),
        "categoria": pergunta["categoria"],
        "naipe": baralhos.NAIPES.get(pergunta["categoria"], "★"),
        "enunciado": pergunta["enunciado"],
        "codigo": pergunta["codigo"],
        "linguagem": pergunta["linguagem"],
        "alternativas": pergunta["alternativas"],
        "segundos": pontuacao.SEGUNDOS_POR_CARTA,
        "descarte_disponivel": not partida.descarte_usado,
        "pontos_total": partida.pontos,
        "sequencia": partida.sequencia,
    }


def usar_descarte(partida):
    if partida.descarte_usado:
        return None

    pergunta = perguntas.buscar(partida.cartas[partida.indice])
    erradas = [i for i in range(len(pergunta["alternativas"])) if i != pergunta["correta"]]
    eliminadas = sorted(random.sample(erradas, min(2, len(erradas))))

    partida.descarte_usado = True
    partida.descarte_na_carta = partida.indice
    partida.save()

    return eliminadas
