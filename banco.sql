CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

CREATE TABLE leiloes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim TEXT NOT NULL,
    valor_inicial REAL NOT NULL
    FOREIGN KEY (usuario_id) REFERENCES usuariios(id)

);

CREATE TABLE lances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor REAL NOT NULL,
    leilao_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    data_criacao TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (leilao_id) REFERENCES leiloes(id)
    FOREIGN KEY (usuario_id) REFERENCES usuariios(id)
);
