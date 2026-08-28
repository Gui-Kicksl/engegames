from django.db import models


class Pergunta(models.Model):
    categoria = models.CharField(max_length=20)
    dificuldade = models.IntegerField()
    enunciado = models.TextField()
    codigo = models.TextField(blank=True)
    linguagem = models.CharField(max_length=20, blank=True)
    alternativas = models.JSONField()
    correta = models.IntegerField()
    explicacao = models.TextField()
