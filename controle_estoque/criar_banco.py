import sqlite3

# cria ou conecta ao banco
conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

# tabela de itens
cursor.execute("""
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    categoria TEXT,
    quantidade INTEGER,
    descricao TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# tabela de histórico
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    acao TEXT,
    dados_antes TEXT,
    dados_depois TEXT,
    data DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# tabela de prints
cursor.execute("""
CREATE TABLE IF NOT EXISTS prints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    caminho_imagem TEXT,
    descricao TEXT,
    data DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Banco criado com sucesso!")