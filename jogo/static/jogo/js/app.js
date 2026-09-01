async function iniciar() {
  try {
    const dados = await API.baralhos();
    estado.baralhos = dados.baralhos;
    desenharBaralhos();
  } catch (erro) {
    el("aviso-menu").textContent = erro.message;
  }
}

async function comecarRodada() {
  el("aviso-menu").textContent = "";
  el("btn-comecar").disabled = true;
  try {
    const dados = await API.criarPartida(estado.baralho);
    limparPartida();
    estado.partidaId = dados.partida_id;
    estado.totalCartas = dados.total_cartas;
    mostrarTela("jogo");
    await proximaCarta();
  } catch (erro) {
    el("aviso-menu").textContent = erro.message;
  } finally {
    el("btn-comecar").disabled = false;
  }
}

async function proximaCarta() {
  virarCarta(false);
  estado.travado = false;
  el("palco").classList.add("carregando");
  try {
    const carta = await API.carta(estado.partidaId);
    estado.carta = carta;
    desenharCarta(carta);
    comecarCronometro(carta.segundos);
  } finally {
    el("palco").classList.remove("carregando");
  }
}

function comecarCronometro(segundos) {
  pararCronometro();
  estado.segundos = segundos;
  desenharRelogio(segundos, segundos);
  estado.cronometro = setInterval(function () {
    estado.segundos -= 1;
    desenharRelogio(estado.segundos, segundos);
    if (estado.segundos <= 0) {
      pararCronometro();
      responder(0);
    }
  }, 1000);
}

async function responder(escolha) {
  if (estado.travado) return;
  estado.travado = true;
  pararCronometro();

  try {
    const julgamento = await API.responder(estado.partidaId, escolha);
    estado.julgamento = julgamento;
    estado.historico.push(julgamento.certa);
    marcarAlternativas(escolha, julgamento.correta_indice);
    desenharVerso(julgamento, estado.carta, julgamento.acabou);
    setTimeout(function () {
      virarCarta(true);
      el("btn-proxima").focus();
    }, 480);
  } catch (erro) {
    estado.travado = false;
    alert(erro.message);
  }
}

async function usarDescarte() {
  if (estado.travado) return;
  try {
    const dados = await API.descarte(estado.partidaId);
    for (const indice of dados.eliminadas) {
      const botao = el("alternativas").querySelector(`[data-escolha="${indice}"]`);
      if (botao) {
        botao.classList.add("eliminada");
        botao.disabled = true;
      }
    }
    el("btn-descarte").disabled = true;
    el("btn-descarte").textContent = "Descarte usado";
  } catch (erro) {
    el("btn-descarte").disabled = true;
  }
}

async function avancar() {
  if (estado.julgamento && estado.julgamento.acabou) {
    const dados = await API.resultado(estado.partidaId);
    desenharResultado(dados);
    mostrarTela("resultado");
    return;
  }
  virarCarta(false);
  setTimeout(proximaCarta, 320);
}

el("baralhos").addEventListener("click", function (evento) {
  const botao = evento.target.closest(".baralho");
  if (!botao) return;
  estado.baralho = botao.dataset.baralho;
  desenharBaralhos();
});

el("alternativas").addEventListener("click", function (evento) {
  const botao = evento.target.closest(".alternativa");
  if (!botao || botao.disabled) return;
  responder(Number(botao.dataset.escolha));
});

el("btn-comecar").addEventListener("click", comecarRodada);
el("btn-descarte").addEventListener("click", usarDescarte);
el("btn-proxima").addEventListener("click", avancar);
el("btn-de-novo").addEventListener("click", comecarRodada);
el("btn-trocar").addEventListener("click", function () {
  limparPartida();
  mostrarTela("menu");
});

document.addEventListener("keydown", function (evento) {
  if (estado.tela !== "jogo") return;
  if (evento.key >= "1" && evento.key <= "4") {
    const botao = el("alternativas").querySelector(`[data-escolha="${Number(evento.key) - 1}"]`);
    if (botao && !botao.disabled) botao.click();
  } else if (evento.key === "Enter" && estado.travado) {
    avancar();
  } else if (evento.key.toLowerCase() === "d") {
    usarDescarte();
  }
});

iniciar();
