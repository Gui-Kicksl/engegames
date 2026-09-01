const estado = {
  tela: "menu",
  baralhos: [],
  baralho: "todos",
  partidaId: null,
  totalCartas: 0,
  carta: null,
  julgamento: null,
  historico: [],
  travado: false,
  segundos: 25,
  cronometro: null
};

function limparPartida() {
  estado.partidaId = null;
  estado.totalCartas = 0;
  estado.carta = null;
  estado.julgamento = null;
  estado.historico = [];
  estado.travado = false;
  pararCronometro();
}

function pararCronometro() {
  if (estado.cronometro !== null) {
    clearInterval(estado.cronometro);
    estado.cronometro = null;
  }
}
