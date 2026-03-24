from flask import Flask, request, jsonify
import sqlite3
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = "banco.db"


# -------------------------
# Conexão com banco
# -------------------------
def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# Inicializar banco
# -------------------------
def init_db():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        categoria TEXT,
        quantidade INTEGER,
        descricao TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        acao TEXT,
        dados_antes TEXT,
        dados_depois TEXT,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# Listar itens
# -------------------------
@app.route("/itens", methods=["GET"])
def listar_itens():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM itens")
    rows = cur.fetchall()

    itens = []
    for r in rows:
        itens.append({
            "id": r["id"],
            "nome": r["nome"],
            "categoria": r["categoria"],
            "quantidade": r["quantidade"],
            "descricao": r["descricao"]
        })

    conn.close()
    return jsonify(itens)


# -------------------------
# Adicionar item
# -------------------------
@app.route("/itens", methods=["POST"])
def adicionar_item():
    data = request.json

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO itens (nome, categoria, quantidade, descricao)
        VALUES (?, ?, ?, ?)
    """, (
        data["nome"],
        data["categoria"],
        data["quantidade"],
        data["descricao"]
    ))

    item_id = cur.lastrowid

    # histórico
    cur.execute("""
        INSERT INTO historico (item_id, acao, dados_depois)
        VALUES (?, ?, ?)
    """, (item_id, "ADD", json.dumps(data)))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# -------------------------
# Editar item
# -------------------------
@app.route("/itens/<int:id>", methods=["PUT"])
def editar_item(id):
    data = request.json

    conn = conectar()
    cur = conn.cursor()

    # pegar dados antigos
    cur.execute("SELECT * FROM itens WHERE id=?", (id,))
    row = cur.fetchone()

    if not row:
        return jsonify({"erro": "Item não encontrado"}), 404

    antes = {
        "id": row["id"],
        "nome": row["nome"],
        "categoria": row["categoria"],
        "quantidade": row["quantidade"],
        "descricao": row["descricao"]
    }

    # atualizar
    cur.execute("""
        UPDATE itens
        SET nome=?, categoria=?, quantidade=?, descricao=?
        WHERE id=?
    """, (
        data["nome"],
        data["categoria"],
        data["quantidade"],
        data["descricao"],
        id
    ))

    # histórico
    cur.execute("""
        INSERT INTO historico (item_id, acao, dados_antes, dados_depois)
        VALUES (?, ?, ?, ?)
    """, (
        id,
        "EDIT",
        json.dumps(antes),
        json.dumps(data)
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "editado"})


# -------------------------
# Deletar item
# -------------------------
@app.route("/itens/<int:id>", methods=["DELETE"])
def deletar_item(id):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM itens WHERE id=?", (id,))
    row = cur.fetchone()

    if not row:
        return jsonify({"erro": "Item não encontrado"}), 404

    antes = {
        "id": row["id"],
        "nome": row["nome"],
        "categoria": row["categoria"],
        "quantidade": row["quantidade"],
        "descricao": row["descricao"]
    }

    cur.execute("DELETE FROM itens WHERE id=?", (id,))

    # histórico
    cur.execute("""
        INSERT INTO historico (item_id, acao, dados_antes)
        VALUES (?, ?, ?)
    """, (
        id,
        "DELETE",
        json.dumps(antes)
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "deletado"})


# -------------------------
# Listar histórico
# -------------------------
@app.route("/historico", methods=["GET"])
def listar_historico():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT * FROM historico ORDER BY data DESC")
    rows = cur.fetchall()

    historico = []
    for r in rows:
        historico.append({
            "id": r["id"],
            "item_id": r["item_id"],
            "acao": r["acao"],
            "dados_antes": r["dados_antes"],
            "dados_depois": r["dados_depois"],
            "data": r["data"]
        })

    conn.close()
    return jsonify(historico)


# -------------------------
# Rodar servidor
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)