import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Pergunta


def carta_atual(request, partida_id):
    pergunta = Pergunta.objects.first()

    carta = {
        "numero": 1,
        "total": 10,
        "categoria": pergunta.categoria,
        "enunciado": pergunta.enunciado,
        "codigo": pergunta.codigo,
        "linguagem": pergunta.linguagem,
        "alternativas": pergunta.alternativas,
        "segundos": 25,
    }
    return JsonResponse(carta)


@csrf_exempt
@require_POST
def responder(request, partida_id):
    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"erro": "corpo não é JSON válido"}, status=400)

    escolha = dados.get("escolha")
    if escolha not in (0, 1, 2, 3):
        return JsonResponse({"erro": "escolha inválida"}, status=400)

    CORRETA = 1
    certa = escolha == CORRETA

    julgamento = {
        "certa": certa,
        "correta_indice": CORRETA,
        "explicacao": "O LEFT JOIN mantém o cliente mesmo sem pedido, preenchendo as colunas de pedido com NULL. COUNT(p.id) ignora NULL, então o total é 0.",
        "pontos_ganhos": 100 if certa else 0,
        "pontos_total": 100 if certa else 0,
        "sequencia": 1 if certa else 0,
        "acabou": False,
    }
    return JsonResponse(julgamento, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_POST
def criar_partida(request):
    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"erro": "corpo não é JSON válido"}, status=400)

    baralho = dados.get("baralho")

    baralhos_validos = ["todos", "sql", "python", "logica", "tech"]
    if baralho not in baralhos_validos:
        return JsonResponse({"erro": "escolha um dos baralhos"}, status=400)

    return JsonResponse({"partida_id": "11111111-1111-1111-1111-111111111111", "total_cartas": 10})


def pagina_do_jogo(request):
    return render(request, "jogo/index.html")
