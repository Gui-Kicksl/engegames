import uuid

from django.db import models

CATEGORIAS = [
    ("sql", "SQL"),
    ("python", "Python"),
    ("logica", "Lógica"),
    ("tech", "Tecnologia"),
]

DIFICULDADES = [
    (1, "Fácil"),
    (2, "Média"),
    (3, "Difícil"),
]

LINGUAGENS = [
    ("", "sem código"),
    ("sql", "SQL"),
    ("python", "Python"),
]


class Pergunta(models.Model):
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    dificuldade = models.IntegerField(choices=DIFICULDADES, default=1)
    enunciado = models.TextField()
    codigo = models.TextField(blank=True)
    linguagem = models.CharField(max_length=20, choices=LINGUAGENS, blank=True)
    alternativas = models.JSONField(default=list)
    correta = models.IntegerField(default=0)
    explicacao = models.TextField()

    class Meta:
        verbose_name = "pergunta"
        verbose_name_plural = "perguntas"
        ordering = ["categoria", "id"]

    def __str__(self):
        return self.enunciado[:70]

    @property
    def texto_correta(self):
        if 0 <= self.correta < len(self.alternativas or []):
            return self.alternativas[self.correta]
        return ""


class Partida(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    baralho = models.CharField(max_length=20)
    cartas = models.JSONField()
    indice = models.IntegerField(default=0)
    pontos = models.IntegerField(default=0)
    sequencia = models.IntegerField(default=0)
    melhor_sequencia = models.IntegerField(default=0)
    descarte_usado = models.BooleanField(default=False)
    descarte_na_carta = models.IntegerField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    carta_entregue_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "partida"
        verbose_name_plural = "partidas"
        ordering = ["-criada_em"]

    def __str__(self):
        return f"{self.baralho} · {self.pontos} pts"


class Resposta(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="respostas")
    pergunta = models.ForeignKey(Pergunta, on_delete=models.PROTECT, related_name="respostas")
    escolha = models.IntegerField()
    certa = models.BooleanField()
    segundos = models.IntegerField()
    pontos = models.IntegerField()

    class Meta:
        verbose_name = "resposta"
        verbose_name_plural = "respostas"
        ordering = ["id"]

    def __str__(self):
        return "certa" if self.certa else "errada"
