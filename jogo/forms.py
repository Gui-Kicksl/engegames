from django import forms

from .models import Pergunta

CAMPOS_ALTERNATIVAS = [
    ("alternativa_a", "A"),
    ("alternativa_b", "B"),
    ("alternativa_c", "C"),
    ("alternativa_d", "D"),
]


class PerguntaForm(forms.ModelForm):
    alternativa_a = forms.CharField(label="Alternativa A", widget=forms.TextInput(attrs={"class": "alt-input"}))
    alternativa_b = forms.CharField(label="Alternativa B", widget=forms.TextInput(attrs={"class": "alt-input"}))
    alternativa_c = forms.CharField(label="Alternativa C", widget=forms.TextInput(attrs={"class": "alt-input"}))
    alternativa_d = forms.CharField(label="Alternativa D", widget=forms.TextInput(attrs={"class": "alt-input"}))
    correta = forms.ChoiceField(
        label="Qual é a certa",
        choices=[(0, "A"), (1, "B"), (2, "C"), (3, "D")],
        widget=forms.RadioSelect,
        help_text="Marque a alternativa correta.",
    )

    class Meta:
        model = Pergunta
        fields = ["categoria", "dificuldade", "enunciado", "codigo", "linguagem", "explicacao"]
        widgets = {
            "enunciado": forms.Textarea(attrs={"rows": 3}),
            "codigo": forms.Textarea(attrs={"rows": 6, "class": "campo-codigo"}),
            "explicacao": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "codigo": "Opcional. Cole o trecho como ele deve aparecer na carta.",
            "explicacao": "Aparece no verso da carta depois que a pessoa responde. É a parte que ensina.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instancia = kwargs.get("instance") or self.instance
        if instancia is not None and instancia.pk:
            alternativas = instancia.alternativas or []
            for indice, (campo, _) in enumerate(CAMPOS_ALTERNATIVAS):
                if indice < len(alternativas):
                    self.fields[campo].initial = alternativas[indice]
            self.fields["correta"].initial = instancia.correta

    def clean(self):
        dados = super().clean()
        textos = [dados.get(campo, "") for campo, _ in CAMPOS_ALTERNATIVAS]
        preenchidas = [t.strip() for t in textos if t and t.strip()]
        if len(preenchidas) == 4 and len(set(preenchidas)) < 4:
            raise forms.ValidationError("As quatro alternativas precisam ser diferentes entre si.")
        return dados

    def save(self, commit=True):
        pergunta = super().save(commit=False)
        pergunta.alternativas = [self.cleaned_data[campo].strip() for campo, _ in CAMPOS_ALTERNATIVAS]
        pergunta.correta = int(self.cleaned_data["correta"])
        if commit:
            pergunta.save()
        return pergunta
