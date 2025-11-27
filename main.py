from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 🔑 COLE AQUI SEU TOKEN COMPLETO DO AIRTABLE (começa com pat5b...)
AIRTABLE_API_KEY = "pat5bm2aY14DYyBX6.783d7b1d9d5de3e1e8af93e359b054191c3e35e9c8b14857e2401d9b8f4f18d4"

# 🔗 COLE AQUI SEU BASE ID (appXXXX...)
BASE_ID = "appX1b1hFl4lcKp8p"

TABLE_NAME = "Produtos"
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

CATEGORIAS_PERMITIDAS = ["Fruta", "Legume", "Verdura"]


@app.route("/")
def home():
    return {"mensagem": "API GreenEats com validação + CRUD Airtable"}, 200


# =======================
# PARTE 2 - VALIDAR PRODUTO
# =======================
@app.route("/validar-produto", methods=["POST"])
def validar_produto():
    dados = request.get_json()
    erros = []

    titulo = dados.get("titulo", "").strip()
    preco = dados.get("preco")
    categoria = dados.get("categoria", "")

    if preco is None or preco <= 0:
        erros.append("O preço deve ser maior que zero.")

    if len(titulo) < 5:
        erros.append("O título deve ter pelo menos 5 caracteres.")

    if categoria not in CATEGORIAS_PERMITIDAS:
        erros.append("Categoria inválida. Use: Fruta, Legume ou Verdura.")

    if erros:
        return jsonify({"valido": False, "erros": erros}), 400

    return jsonify({"valido": True, "mensagem": "Produto válido para cadastro."}), 200


# =======================
# PARTE 3 - CRUD PRODUTOS (Airtable)
# =======================

# GET /produtos -> lista todos os produtos
@app.route("/produtos", methods=["GET"])
def listar_produtos():
    resp = requests.get(BASE_URL, headers=HEADERS)
    dados = resp.json()
    # Airtable devolve { "records": [ ... ] }
    return jsonify(dados.get("records", [])), 200


# POST /produtos -> cria um novo produto
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()

    payload = {
        "fields": {
            "nome": dados.get("nome"),
            "descricao": dados.get("descricao", ""),
            "preco": dados.get("preco"),
            "categoria": dados.get("categoria"),
            "estoque": dados.get("estoque", 0),
            "produtor": dados.get("produtor", "")
        }
    }

    resp = requests.post(BASE_URL, json=payload, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code


# GET /produtos/<record_id> -> detalhe de um produto
@app.route("/produtos/<record_id>", methods=["GET"])
def obter_produto(record_id):
    url = f"{BASE_URL}/{record_id}"
    resp = requests.get(url, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code


# PUT /produtos/<record_id> -> atualiza um produto
@app.route("/produtos/<record_id>", methods=["PUT"])
def atualizar_produto(record_id):
    dados = request.get_json()

    payload = {
        "fields": {
            "nome": dados.get("nome"),
            "descricao": dados.get("descricao"),
            "preco": dados.get("preco"),
            "categoria": dados.get("categoria"),
            "estoque": dados.get("estoque"),
            "produtor": dados.get("produtor")
        }
    }

    url = f"{BASE_URL}/{record_id}"
    # no Airtable, update parcial é via PATCH
    resp = requests.patch(url, json=payload, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code


# DELETE /produtos/<record_id> -> apaga um produto
@app.route("/produtos/<record_id>", methods=["DELETE"])
def deletar_produto(record_id):
    url = f"{BASE_URL}/{record_id}"
    resp = requests.delete(url, headers=HEADERS)
    if resp.status_code == 200:
        return "", 204  # apagado com sucesso
    else:
        return jsonify({"erro": "Não foi possível apagar"}), resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
