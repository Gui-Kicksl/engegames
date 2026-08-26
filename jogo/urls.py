from django.urls import path

from . import views

urlpatterns = [
    path("partidas/<uuid:partida_id>/carta/", views.carta_atual, name="carta"),
    path("partidas/<uuid:partida_id>/resposta/", views.responder, name="responder"),
    path("partidas/", views.criar_partida, name="criar_partida"),
]