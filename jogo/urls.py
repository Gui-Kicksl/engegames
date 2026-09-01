from django.urls import path

from . import views

urlpatterns = [
    path("baralhos/", views.listar_baralhos, name="listar_baralhos"),
    path("partidas/", views.criar_partida, name="criar_partida"),
    path("partidas/<uuid:partida_id>/carta/", views.carta_atual, name="carta_atual"),
    path("partidas/<uuid:partida_id>/descarte/", views.descartar, name="descartar"),
    path("partidas/<uuid:partida_id>/resposta/", views.responder, name="responder"),
    path("partidas/<uuid:partida_id>/resultado/", views.resultado_da_partida, name="resultado"),
]
