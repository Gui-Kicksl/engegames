from django.contrib import admin, messages
from django.db.models import Count, Q
from django.utils.html import format_html

from .forms import PerguntaForm
from .models import Partida, Pergunta, Resposta

NAIPES = {"sql": "♦", "python": "♠", "logica": "♥", "tech": "♣"}
VERMELHOS = {"sql", "logica"}

admin.site.site_header = "Engegames"
admin.site.site_title = "Engegames"
admin.site.index_title = "Banco de cartas e partidas"


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    form = PerguntaForm
    list_display = ("naipe", "resumo", "dificuldade", "gabarito", "tem_codigo", "desempenho")
    list_display_links = ("resumo",)
    list_filter = ("categoria", "dificuldade", "linguagem")
    search_fields = ("enunciado", "explicacao")
    list_per_page = 30
    save_on_top = True
    actions = ["duplicar"]

    fieldsets = (
        ("A pergunta", {"fields": ("categoria", "dificuldade", "enunciado")}),
        ("Bloco de código", {"fields": ("linguagem", "codigo"), "classes": ("collapse",)}),
        ("Alternativas", {"fields": ("alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d", "correta")}),
        ("Verso da carta", {"fields": ("explicacao",)}),
    )

    class Media:
        css = {"all": ("jogo/css/admin.css",)}

    def get_queryset(self, request):
        consulta = super().get_queryset(request)
        return consulta.annotate(
            _respondidas=Count("respostas"),
            _acertos=Count("respostas", filter=Q(respostas__certa=True)),
        )

    @admin.display(description="")
    def naipe(self, obj):
        simbolo = NAIPES.get(obj.categoria, "★")
        cor = "#AE2B32" if obj.categoria in VERMELHOS else "#1A1917"
        return format_html('<span style="font-size:20px;color:{}">{}</span>', cor, simbolo)

    @admin.display(description="Pergunta", ordering="enunciado")
    def resumo(self, obj):
        texto = obj.enunciado if len(obj.enunciado) <= 90 else obj.enunciado[:90] + "…"
        return texto

    @admin.display(description="Resposta certa")
    def gabarito(self, obj):
        letra = "ABCD"[obj.correta] if 0 <= obj.correta < 4 else "?"
        return format_html("<b>{}</b> · {}", letra, obj.texto_correta[:40])

    @admin.display(description="Código", boolean=True)
    def tem_codigo(self, obj):
        return bool(obj.codigo)

    @admin.display(description="Acertos")
    def desempenho(self, obj):
        respondidas = getattr(obj, "_respondidas", 0)
        if not respondidas:
            return format_html('<span style="color:#999">nunca jogada</span>')
        acertos = getattr(obj, "_acertos", 0)
        pct = round(100 * acertos / respondidas)
        cor = "#2C7A55" if pct >= 60 else "#AE2B32"
        return format_html('<b style="color:{}">{}%</b> <span style="color:#999">({}x)</span>', cor, pct, respondidas)

    @admin.action(description="Duplicar as perguntas selecionadas")
    def duplicar(self, request, queryset):
        total = 0
        for pergunta in queryset:
            pergunta.pk = None
            pergunta.enunciado = "[cópia] " + pergunta.enunciado
            pergunta.save()
            total += 1
        self.message_user(request, f"{total} pergunta(s) duplicada(s).", messages.SUCCESS)


class RespostaInline(admin.TabularInline):
    model = Resposta
    extra = 0
    can_delete = False
    readonly_fields = ("pergunta", "escolha", "certa", "segundos", "pontos")
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("criada_em", "baralho", "progresso", "pontos", "melhor_sequencia", "descarte_usado")
    list_filter = ("baralho", "descarte_usado", "criada_em")
    date_hierarchy = "criada_em"
    inlines = [RespostaInline]
    readonly_fields = (
        "id", "baralho", "cartas", "indice", "pontos", "sequencia",
        "melhor_sequencia", "descarte_usado", "descarte_na_carta",
        "criada_em", "carta_entregue_em",
    )
    list_per_page = 30

    class Media:
        css = {"all": ("jogo/css/admin.css",)}

    @admin.display(description="Progresso")
    def progresso(self, obj):
        total = len(obj.cartas or [])
        return format_html("{} de {}", obj.indice, total)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
