// URL do backend (API GreenEats)
const API_URL = "https://6ab7f0a0-2326-411e-82a3-58337be09b77-00-2g69l1n36f36.janeway.replit.dev";

const form = document.getElementById("produtoForm");
const resultadoDiv = document.getElementById("resultado");
const botaoValidar = document.getElementById("btn-validar");

const tbodyProdutos = document.getElementById("produtos-tbody");
const statusLista = document.getElementById("produtos-status");
const btnRecarregar = document.getElementById("btn-recarregar");

/* ===========================
   PARTE 2 - VALIDAÇÃO
   =========================== */

form.addEventListener("submit", function (event) {
  event.preventDefault();

  const titulo = document.getElementById("titulo").value;
  const preco = parseFloat(document.getElementById("preco").value);
  const categoria = document.getElementById("categoria").value;

  const dados = { titulo, preco, categoria };

  botaoValidar.disabled = true;
  botaoValidar.textContent = "Validando...";
  resultadoDiv.className = "resultado escondido";
  resultadoDiv.textContent = "";

  fetch(API_URL + "/validar-produto", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dados),
  })
    .then(async (response) => {
      const corpo = await response.json();

      if (response.ok) {
        resultadoDiv.className = "resultado ok";
        resultadoDiv.textContent = corpo.mensagem;
      } else {
        resultadoDiv.className = "resultado erro";
        resultadoDiv.textContent = corpo.erros.join("\n");
      }
    })
    .catch((erro) => {
      console.error("Erro na requisição:", erro);
      resultadoDiv.className = "resultado erro";
      resultadoDiv.textContent = "Erro ao conectar com o servidor da GreenEats.";
    })
    .finally(() => {
      botaoValidar.disabled = false;
      botaoValidar.textContent = "Validar produto";
      resultadoDiv.classList.remove("escondido");
    });
});

/* ===========================
   PARTE 3 - LISTAGEM (GET /produtos)
   =========================== */

function formatarPreco(valor) {
  if (typeof valor !== "number") return "-";
  return valor.toFixed(2).replace(".", ",");
}

function carregarProdutos() {
  console.log("Recarregando lista de produtos...");

  tbodyProdutos.innerHTML = `
    <tr>
      <td colspan="6" class="empty">Carregando produtos cadastrados...</td>
    </tr>
  `;
  statusLista.textContent = "";

  fetch(API_URL + "/produtos", { cache: "no-store" })
    .then((resp) => resp.json())
    .then((records) => {
      console.log("Resposta /produtos:", records);

      if (!Array.isArray(records) || records.length === 0) {
        tbodyProdutos.innerHTML = `
          <tr>
            <td colspan="6" class="empty">Nenhum produto cadastrado ainda.</td>
          </tr>
        `;
        statusLista.textContent = "Lista sincronizada com o Airtable (0 itens).";
        return;
      }

      tbodyProdutos.innerHTML = "";

      records.forEach((rec, index) => {
        const fields = rec.fields || {};
        const nome = fields.nome || "-";
        const categoria = fields.categoria || "-";
        const preco = fields.preco;
        const estoque = fields.estoque ?? "-";
        const produtor = fields.produtor || "-";

        const tr = document.createElement("tr");

        tr.innerHTML = `
          <td>${index + 1}</td>
          <td>${nome}</td>
          <td><span class="tag-categoria">${categoria}</span></td>
          <td>${formatarPreco(preco)}</td>
          <td>${estoque}</td>
          <td>${produtor}</td>
        `;

        tbodyProdutos.appendChild(tr);
      });

      statusLista.textContent = `Lista sincronizada com o Airtable (${records.length} produto(s)).`;
    })
    .catch((erro) => {
      console.error("Erro ao carregar produtos:", erro);
      tbodyProdutos.innerHTML = `
        <tr>
          <td colspan="6" class="empty">Erro ao carregar produtos do servidor.</td>
        </tr>
      `;
      statusLista.textContent = "Não foi possível sincronizar com o Airtable.";
    });
}

// só adiciona o evento se o botão existir
if (btnRecarregar) {
  btnRecarregar.addEventListener("click", carregarProdutos);
} else {
  console.warn("Botão #btn-recarregar não encontrado no HTML.");
}

// carrega automaticamente ao abrir a página
carregarProdutos();