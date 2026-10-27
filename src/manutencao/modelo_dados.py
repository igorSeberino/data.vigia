"""Modelo dimensional (esquema estrela) do AI4I 2020 em SQLite e consultas analíticas.

Grão da fato: 1 linha = 1 ciclo de processo (``udi``). ``id_produto`` é dimensão degenerada
(10.000 valores distintos, 1 por ciclo). Modos de falha ficam numa tabela ponte porque um ciclo
pode ter mais de um modo (relação N:N).
"""

import sqlite3
from pathlib import Path

import pandas as pd

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

TIPOS = pd.DataFrame(
    {
        "id_tipo": [1, 2, 3],
        "codigo": ["L", "M", "H"],
        "descricao": ["Baixa qualidade", "Média qualidade", "Alta qualidade"],
        "participacao_nominal": [0.5, 0.3, 0.2],
        "limite_esforco_min_nm": [11000.0, 12000.0, 13000.0],
    }
)

FAIXAS = pd.DataFrame(
    {
        "id_faixa": [1, 2, 3, 4, 5],
        "rotulo": ["000-049 min", "050-099 min", "100-149 min", "150-199 min", "200+ min"],
        "minimo_min": [0, 50, 100, 150, 200],
        "maximo_min": [49, 99, 149, 199, None],
    }
)

MODOS = pd.DataFrame(
    {
        "id_modo": [1, 2, 3, 4, 5],
        "sigla": ["TWF", "HDF", "PWF", "OSF", "RNF"],
        "nome": [
            "Desgaste da ferramenta",
            "Dissipação de calor",
            "Potência",
            "Sobrecarga",
            "Aleatória",
        ],
        "regra": [
            "troca/falha da ferramenta com desgaste entre ~200 e 240 min",
            "dif. temperatura < 8,6 K e rotação < 1380 rpm",
            "potência < 3500 W ou > 9000 W",
            "desgaste × torque acima do limite do tipo (11/12/13 mil min·Nm)",
            "0,1 % de chance por ciclo, independente do processo",
        ],
    }
)

_COLS_FATO = [
    "udi",
    "id_produto",
    "id_tipo",
    "id_faixa",
    "temp_ar_k",
    "temp_processo_k",
    "rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
    "dif_temperatura_k",
    "potencia_w",
    "esforco_ferramenta_min_nm",
    "falha",
]


def conectar(caminho: Path | str = CAMINHO_DB) -> sqlite3.Connection:
    """Abre conexão com chaves estrangeiras ligadas (``":memory:"`` é aceito)."""
    conn = sqlite3.connect(str(caminho))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_schema(conn: sqlite3.Connection) -> None:
    """Cria tabelas e índices do esquema estrela."""
    conn.executescript(DDL)


def _id_faixa(desgaste: pd.Series) -> pd.Series:
    limites = [-1, 49, 99, 149, 199, float("inf")]
    return pd.cut(desgaste, bins=limites, labels=[1, 2, 3, 4, 5]).astype("int64")


def carregar(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    """Carrega dimensões, fato e ponte a partir do DataFrame preparado (T1)."""
    TIPOS.to_sql("dim_tipo_produto", conn, if_exists="append", index=False)
    FAIXAS.to_sql("dim_faixa_desgaste", conn, if_exists="append", index=False)
    MODOS.to_sql("dim_modo_falha", conn, if_exists="append", index=False)

    fato = df.copy()
    fato["id_tipo"] = (
        fato["tipo"].astype(str).map(dict(zip(TIPOS["codigo"], TIPOS["id_tipo"], strict=True)))
    )
    fato["id_faixa"] = _id_faixa(fato["desgaste_ferramenta_min"])
    fato[_COLS_FATO].to_sql("fato_ciclo", conn, if_exists="append", index=False)

    colunas_modo = {
        f"falha_{s.lower()}": i for s, i in zip(MODOS["sigla"], MODOS["id_modo"], strict=True)
    }
    longo = df[["udi", *colunas_modo]].melt(id_vars="udi", var_name="coluna", value_name="flag")
    ponte = longo[longo["flag"] == 1].assign(id_modo=lambda d: d["coluna"].map(colunas_modo))
    ponte[["udi", "id_modo"]].sort_values(["udi", "id_modo"]).to_sql(
        "ponte_ciclo_modo", conn, if_exists="append", index=False
    )
    conn.commit()


def construir_banco(df: pd.DataFrame, caminho: Path | str = CAMINHO_DB) -> Path | str:
    """Recria o banco do zero (apaga o arquivo anterior) e devolve o caminho."""
    if str(caminho) != ":memory:":
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.unlink(missing_ok=True)
    with conectar(caminho) as conn:
        criar_schema(conn)
        carregar(conn, df)
    return caminho
