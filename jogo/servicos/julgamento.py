from django.utils import timezone

from ..models import Resposta
from . import perguntas, pontuacao


def julgar(partida, escolha):
    pergunta = perguntas.buscar(partida.cartas[partida.indice])

    segundos = pontuacao.SEGUNDOS_POR_CARTA
    if partida.carta_entregue_em is not None:
        decorrido = timezone.now() - partida.carta_entregue_em
        segundos = int(decorrido.total_seconds())

    estourou = segundos > pontuacao.SEGUNDOS_POR_CARTA
    certa = (not estourou) and escolha == pergunta["correta"]
    usou_descarte = partida.descarte_na_carta == partida.indice

    if certa:
        partida.sequencia += 1
        partida.melhor_sequencia = max(partida.melhor_sequencia, partida.sequencia)
        ganho = pontuacao.calcular(segundos, partida.sequencia, usou_descarte)
    else:
        partida.sequencia = 0
        ganho = 0

    partida.pontos += ganho

    Resposta.objects.create(
        partida=partida,
        pergunta_id=pergunta["id"],
        escolha=escolha,
        certa=certa,
        segundos=segundos,
        pontos=ganho,
    )

    partida.indice += 1
    partida.carta_entregue_em = None
    partida.save()

    return {
        "certa": certa,
        "correta_indice": pergunta["correta"],
        "explicacao": pergunta["explicacao"],
        "pontos_ganhos": ganho,
        "pontos_total": partida.pontos,
        "sequencia": partida.sequencia,
        "multiplicador": pontuacao.multiplicador(partida.sequencia),
        "tempo_esgotado": estourou,
        "acabou": partida.indice >= len(partida.cartas),
    }
