"""Modelo dimensional (esquema estrela) do AI4I 2020 em SQLite e consultas analíticas.

Grão da fato: 1 linha = 1 ciclo de processo (``udi``). ``id_produto`` é dimensão degenerada
(10.000 valores distintos, 1 por ciclo). Modos de falha ficam numa tabela ponte porque um ciclo
pode ter mais de um modo (relação N:N).
"""

import sqlite3
from pathlib import Path

from manutencao.config import CAMINHO_DB

DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE dim_tipo_produto (
    id_tipo                INTEGER PRIMARY KEY,
    codigo                 TEXT    NOT NULL UNIQUE CHECK (codigo IN ('L', 'M', 'H')),
    descricao              TEXT    NOT NULL,
    participacao_nominal   REAL    NOT NULL,
    limite_esforco_min_nm  REAL    NOT NULL
);

CREATE TABLE dim_faixa_desgaste (
    id_faixa     INTEGER PRIMARY KEY,
    rotulo       TEXT    NOT NULL UNIQUE,
    minimo_min   INTEGER NOT NULL,
    maximo_min   INTEGER            -- NULL = sem limite superior
);

CREATE TABLE dim_modo_falha (
    id_modo      INTEGER PRIMARY KEY,
    sigla        TEXT    NOT NULL UNIQUE,
    nome         TEXT    NOT NULL,
    regra        TEXT    NOT NULL
);

CREATE TABLE fato_ciclo (
    udi                        INTEGER PRIMARY KEY,
    id_produto                 TEXT    NOT NULL UNIQUE,
    id_tipo                    INTEGER NOT NULL REFERENCES dim_tipo_produto (id_tipo),
    id_faixa                   INTEGER NOT NULL REFERENCES dim_faixa_desgaste (id_faixa),
    temp_ar_k                  REAL    NOT NULL,
    temp_processo_k            REAL    NOT NULL,
    rotacao_rpm                INTEGER NOT NULL,
    torque_nm                  REAL    NOT NULL,
    desgaste_ferramenta_min    INTEGER NOT NULL,
    dif_temperatura_k          REAL    NOT NULL,
    potencia_w                 REAL    NOT NULL,
    esforco_ferramenta_min_nm  REAL    NOT NULL,
    falha                      INTEGER NOT NULL CHECK (falha IN (0, 1))
);

CREATE TABLE ponte_ciclo_modo (
    udi      INTEGER NOT NULL REFERENCES fato_ciclo (udi),
    id_modo  INTEGER NOT NULL REFERENCES dim_modo_falha (id_modo),
    PRIMARY KEY (udi, id_modo)
);

CREATE INDEX ix_fato_tipo   ON fato_ciclo (id_tipo);
CREATE INDEX ix_fato_faixa  ON fato_ciclo (id_faixa);
CREATE INDEX ix_ponte_modo  ON ponte_ciclo_modo (id_modo);
"""


def conectar(caminho: Path | str = CAMINHO_DB) -> sqlite3.Connection:
    """Abre conexão com chaves estrangeiras ligadas (``":memory:"`` é aceito)."""
    conn = sqlite3.connect(str(caminho))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_schema(conn: sqlite3.Connection) -> None:
    """Cria tabelas e índices do esquema estrela."""
    conn.executescript(DDL)
