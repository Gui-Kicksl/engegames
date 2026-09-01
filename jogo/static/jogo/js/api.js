const API = (function () {
  function csrf() {
    const partes = document.cookie.split("; ");
    for (const parte of partes) {
      if (parte.startsWith("csrftoken=")) {
        return parte.substring("csrftoken=".length);
      }
    }
    return "";
  }

  async function pegar(url) {
    const resposta = await fetch(url);
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "erro na requisição");
    }
    return dados;
  }

  async function enviar(url, corpo) {
    const resposta = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf()
      },
      body: JSON.stringify(corpo || {})
    });
    const dados = await resposta.json();
    if (!resposta.ok) {
      throw new Error(dados.erro || "erro na requisição");
    }
    return dados;
  }

  return {
    baralhos: () => pegar("/api/baralhos/"),
    criarPartida: (baralho) => enviar("/api/partidas/", { baralho: baralho }),
    carta: (id) => pegar(`/api/partidas/${id}/carta/`),
    descarte: (id) => enviar(`/api/partidas/${id}/descarte/`),
    responder: (id, escolha) => enviar(`/api/partidas/${id}/resposta/`, { escolha: escolha }),
    resultado: (id) => pegar(`/api/partidas/${id}/resultado/`)
  };
})();
