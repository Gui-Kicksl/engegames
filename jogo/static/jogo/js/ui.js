const LETRAS = ["A", "B", "C", "D"];
const VERMELHOS = ["♦", "♥"];

function el(id) {
  return document.getElementById(id);
}

function mostrarTela(nome) {
  estado.tela = nome;
  for (const secao of document.querySelectorAll(".tela")) {
    secao.classList.toggle("ativa", secao.id === "tela-" + nome);
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function desenharBaralhos() {
  el("baralhos").innerHTML = estado.baralhos
    .map(function (b) {
      const cor = VERMELHOS.includes(b.naipe) ? "v" : "";
      const marcado = b.chave === estado.baralho;
      return `<button class="baralho" data-baralho="${b.chave}" aria-pressed="${marcado}">
        <span class="qtd">${b.cartas} cartas</span>
        <span class="simbolo ${cor}">${b.naipe}</span>
        <div class="nome">${b.nome}</div>
      </button>`;
    })
    .join("");
}

function desenharPips() {
  const total = estado.totalCartas;
  let html = "";
  for (let i = 0; i < total; i++) {
    let classe = "pip";
    if (i < estado.historico.length) {
      classe += estado.historico[i] ? " acerto" : " erro";
    } else if (i === estado.historico.length) {
      classe += " agora";
    }
    html += `<span class="${classe}"></span>`;
  }
  el("pips").innerHTML = html;
}

function desenharCarta(carta) {
  const cor = VERMELHOS.includes(carta.naipe) ? "v" : "";
  const canto = `<span class="${cor}">${carta.naipe}</span>`;
  el("canto-ce").innerHTML = canto;
  el("canto-cd").innerHTML = canto;

  el("meta").textContent = `${carta.categoria} · carta ${carta.numero} de ${carta.total}`;
  el("enunciado").textContent = carta.enunciado;

  el("area-codigo").innerHTML = carta.codigo
    ? `<pre class="codigo">${escapar(carta.codigo)}</pre>`
    : "";

  el("alternativas").innerHTML = carta.alternativas
    .map(function (texto, i) {
      return `<button class="alternativa" data-escolha="${i}">
        <span class="letra">${LETRAS[i]}</span><span>${escapar(texto)}</span>
      </button>`;
    })
    .join("");

  const botaoDescarte = el("btn-descarte");
  botaoDescarte.disabled = !carta.descarte_disponivel;
  botaoDescarte.textContent = carta.descarte_disponivel
    ? "Descarte · elimina 2"
    : "Descarte usado";

  el("pontos").textContent = `${carta.pontos_total} pts`;
  atualizarMultiplicador(carta.sequencia);
  desenharPips();
}

function atualizarMultiplicador(sequencia) {
  let m = 1;
  if (sequencia >= 8) m = 2;
  else if (sequencia >= 5) m = 1.5;
  else if (sequencia >= 3) m = 1.2;
  el("multiplicador").textContent = "×" + m.toFixed(1).replace(".", ",");
}

function desenharRelogio(restante, total) {
  const barra = el("barra-tempo");
  barra.style.transform = `scaleX(${Math.max(0, restante / total)})`;
  barra.classList.toggle("pouco", restante <= 7);
  const relogio = el("relogio");
  relogio.textContent = Math.max(0, restante) + "s";
  relogio.classList.toggle("pouco", restante <= 7);
}

function marcarAlternativas(escolha, correta) {
  const botoes = el("alternativas").children;
  for (let i = 0; i < botoes.length; i++) {
    botoes[i].disabled = true;
    if (i === correta) botoes[i].classList.add("certa");
    else if (i === escolha) botoes[i].classList.add("errada");
  }
}

function desenharVerso(julgamento, carta, ultima) {
  const veredito = el("veredito");
  if (julgamento.certa) {
    veredito.textContent = "Certa.";
    veredito.className = "veredito certo";
  } else {
    veredito.textContent = julgamento.tempo_esgotado ? "Tempo." : "Errou.";
    veredito.className = "veredito errado";
  }

  el("ganho").textContent = julgamento.pontos_ganhos > 0
    ? `+${julgamento.pontos_ganhos} pts`
    : "";

  const indice = julgamento.correta_indice;
  el("correta").textContent = `${LETRAS[indice]}. ${carta.alternativas[indice]}`;
  el("explicacao").textContent = julgamento.explicacao;
  el("btn-proxima").textContent = ultima ? "Ver resultado" : "Próxima carta";

  el("pontos").textContent = `${julgamento.pontos_total} pts`;
  atualizarMultiplicador(julgamento.sequencia);
  desenharPips();
}

function virarCarta(virada) {
  el("carta3d").classList.toggle("virada", virada);
}

function desenharResultado(dados) {
  const titulos = ["Ainda dá pra virar", "Boa mão", "Mão quase perfeita", "Baralho dominado"];
  const proporcao = dados.total ? dados.acertos / dados.total : 0;
  let faixa = 0;
  if (proporcao === 1) faixa = 3;
  else if (proporcao >= 0.8) faixa = 2;
  else if (proporcao >= 0.5) faixa = 1;

  el("titulo-fim").textContent = titulos[faixa];
  el("fim-pontos").textContent = dados.pontos;
  el("fim-acertos").textContent = `${dados.acertos}/${dados.total}`;
  el("fim-sequencia").textContent = dados.melhor_sequencia;
  el("fim-tempo").textContent = String(dados.tempo_medio).replace(".", ",") + "s";

  el("fim-barras").innerHTML = dados.por_categoria
    .map(function (c) {
      const pct = c.total ? Math.round((100 * c.acertos) / c.total) : 0;
      return `<div class="barra">
        <span>${c.naipe} ${c.nome}</span>
        <span class="trilho"><span class="preenchida" style="width:${pct}%"></span></span>
        <span class="conta">${c.acertos}/${c.total}</span>
      </div>`;
    })
    .join("");

  el("fim-erros").innerHTML = dados.erros.length
    ? `<h3 class="etiqueta">Cartas para revisar</h3><div class="revisao">` +
      dados.erros
        .map(function (e) {
          return `<div class="erro-carta">
            <p>${escapar(e.enunciado)}</p>
            <span>Resposta certa: <b>${escapar(e.correta)}</b> — ${escapar(e.explicacao)}</span>
          </div>`;
        })
        .join("") +
      `</div>`
    : `<h3 class="etiqueta">Cartas para revisar</h3><p class="chamada">Nenhuma. Você zerou o baralho.</p>`;
}

function escapar(texto) {
  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
