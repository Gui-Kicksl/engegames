import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .servicos import baralhos, julgamento, partidas, resultado


@ensure_csrf_cookie
def pagina_do_jogo(request):
    return render(request, "jogo/index.html")


@require_GET
def listar_baralhos(request):
    return JsonResponse({"baralhos": baralhos.listar()})


@require_POST
def criar_partida(request):
    dados = _corpo(request)
    if dados is None:
        return _erro("corpo não é JSON válido", 400)

    baralho = dados.get("baralho")
    if baralho not in baralhos.VALIDOS:
        return _erro("escolha um dos baralhos", 400)

    partida = partidas.criar(baralho)
    if partida is None:
        return _erro("esse baralho não tem perguntas cadastradas", 400)

    return JsonResponse(
        {"partida_id": str(partida.id), "total_cartas": len(partida.cartas)}
    )


@require_GET
def carta_atual(request, partida_id):
    partida = partidas.buscar(partida_id)
    if partida is None:
        return _erro("partida não encontrada", 404)
    if partidas.acabou(partida):
        return _erro("a partida já acabou", 409)

    carta = partidas.entregar_carta(partida)
    if carta is None:
        return _erro("carta não encontrada", 404)

    return JsonResponse(carta)


@require_POST
def descartar(request, partida_id):
    partida = partidas.buscar(partida_id)
    if partida is None:
        return _erro("partida não encontrada", 404)
    if partidas.acabou(partida):
        return _erro("a partida já acabou", 409)

    eliminadas = partidas.usar_descarte(partida)
    if eliminadas is None:
        return _erro("o descarte já foi usado nesta partida", 409)

    return JsonResponse({"eliminadas": eliminadas})


@require_POST
def responder(request, partida_id):
    dados = _corpo(request)
    if dados is None:
        return _erro("corpo não é JSON válido", 400)

    escolha = dados.get("escolha")
    if escolha not in (0, 1, 2, 3):
        return _erro("escolha inválida", 400)

    partida = partidas.buscar(partida_id)
    if partida is None:
        return _erro("partida não encontrada", 404)
    if partidas.acabou(partida):
        return _erro("a partida já acabou", 409)
    if partida.carta_entregue_em is None:
        return _erro("peça a carta antes de responder", 409)

    return JsonResponse(julgamento.julgar(partida, escolha))


@require_GET
def resultado_da_partida(request, partida_id):
    partida = partidas.buscar(partida_id)
    if partida is None:
        return _erro("partida não encontrada", 404)

    return JsonResponse(resultado.montar(partida))


def _corpo(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


def _erro(mensagem, status):
    return JsonResponse({"erro": mensagem}, status=status)
