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


def consultar(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    """Executa um SELECT e devolve DataFrame."""
    return pd.read_sql_query(sql, conn, params=params)


CONSULTAS: dict[str, str] = {
    "taxa_falha_por_tipo": """
        SELECT t.codigo AS tipo, t.descricao, COUNT(*) AS ciclos, SUM(f.falha) AS falhas,
               ROUND(100.0 * SUM(f.falha) / COUNT(*), 2) AS taxa_falha_pct
        FROM fato_ciclo f JOIN dim_tipo_produto t ON t.id_tipo = f.id_tipo
        GROUP BY t.id_tipo ORDER BY t.id_tipo""",
    "falhas_por_modo": """
        SELECT m.sigla, m.nome, COUNT(*) AS ocorrencias,
               ROUND(100.0 * COUNT(*) / (SELECT SUM(falha) FROM fato_ciclo), 2)
                   AS pct_sobre_falhas
        FROM ponte_ciclo_modo p JOIN dim_modo_falha m ON m.id_modo = p.id_modo
        GROUP BY m.id_modo ORDER BY ocorrencias DESC""",
    "coocorrencia_modos": """
        SELECT a.sigla AS modo_a, b.sigla AS modo_b, COUNT(*) AS ciclos
        FROM ponte_ciclo_modo pa
        JOIN ponte_ciclo_modo pb ON pb.udi = pa.udi AND pb.id_modo > pa.id_modo
        JOIN dim_modo_falha a ON a.id_modo = pa.id_modo
        JOIN dim_modo_falha b ON b.id_modo = pb.id_modo
        GROUP BY a.sigla, b.sigla ORDER BY ciclos DESC""",
    "taxa_falha_por_faixa_desgaste": """
        SELECT d.rotulo AS faixa_desgaste, COUNT(*) AS ciclos, SUM(f.falha) AS falhas,
               ROUND(100.0 * SUM(f.falha) / COUNT(*), 2) AS taxa_falha_pct
        FROM fato_ciclo f JOIN dim_faixa_desgaste d ON d.id_faixa = f.id_faixa
        GROUP BY d.id_faixa ORDER BY d.id_faixa""",
    "taxa_falha_por_tipo_e_faixa": """
        SELECT t.codigo AS tipo, d.rotulo AS faixa_desgaste, COUNT(*) AS ciclos,
               SUM(f.falha) AS falhas, ROUND(100.0 * SUM(f.falha) / COUNT(*), 2) AS taxa_falha_pct
        FROM fato_ciclo f
        JOIN dim_tipo_produto t ON t.id_tipo = f.id_tipo
        JOIN dim_faixa_desgaste d ON d.id_faixa = f.id_faixa
        GROUP BY t.id_tipo, d.id_faixa ORDER BY t.id_tipo, d.id_faixa""",
    "perfil_sensores_por_modo": """
        SELECT m.sigla, COUNT(*) AS ciclos,
               ROUND(AVG(f.dif_temperatura_k), 2) AS dif_temp_media_k,
               ROUND(AVG(f.rotacao_rpm), 0) AS rotacao_media_rpm,
               ROUND(AVG(f.torque_nm), 1) AS torque_medio_nm,
               ROUND(AVG(f.potencia_w), 0) AS potencia_media_w,
               ROUND(AVG(f.desgaste_ferramenta_min), 0) AS desgaste_medio_min
        FROM ponte_ciclo_modo p
        JOIN fato_ciclo f ON f.udi = p.udi
        JOIN dim_modo_falha m ON m.id_modo = p.id_modo
        GROUP BY m.id_modo
        UNION ALL
        SELECT 'SEM FALHA', COUNT(*), ROUND(AVG(dif_temperatura_k), 2), ROUND(AVG(rotacao_rpm), 0),
               ROUND(AVG(torque_nm), 1), ROUND(AVG(potencia_w), 0),
               ROUND(AVG(desgaste_ferramenta_min), 0)
        FROM fato_ciclo WHERE falha = 0""",
    "esforco_acima_do_limite": """
        SELECT t.codigo AS tipo, t.limite_esforco_min_nm,
               SUM(f.esforco_ferramenta_min_nm > t.limite_esforco_min_nm) AS ciclos_acima,
               SUM(CASE WHEN f.esforco_ferramenta_min_nm > t.limite_esforco_min_nm
                        THEN f.falha ELSE 0 END) AS falhas_acima,
               SUM(EXISTS (SELECT 1 FROM ponte_ciclo_modo p
                           WHERE p.udi = f.udi AND p.id_modo = 4)) AS ciclos_com_osf
        FROM fato_ciclo f JOIN dim_tipo_produto t ON t.id_tipo = f.id_tipo
        GROUP BY t.id_tipo ORDER BY t.id_tipo""",
    "inconsistencias_rotulo": """
        SELECT 'falha sem modo' AS inconsistencia, COUNT(*) AS ciclos
        FROM fato_ciclo f
        WHERE f.falha = 1 AND NOT EXISTS (SELECT 1 FROM ponte_ciclo_modo p WHERE p.udi = f.udi)
        UNION ALL
        SELECT 'modo sem falha', COUNT(DISTINCT p.udi)
        FROM ponte_ciclo_modo p JOIN fato_ciclo f ON f.udi = p.udi
        WHERE f.falha = 0""",
}


def executar_consultas(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Roda todas as consultas de ``CONSULTAS``."""
    return {nome: consultar(conn, sql) for nome, sql in CONSULTAS.items()}


def verificar_integridade(conn: sqlite3.Connection, df: pd.DataFrame) -> pd.DataFrame:
    """Confere o banco contra o DataFrame de origem. Devolve ``verificacao, esperado, obtido, ok``."""

    def um(sql: str) -> int:
        return int(conn.execute(sql).fetchone()[0])

    checagens = [
        ("linhas na fato = linhas do DataFrame", len(df), um("SELECT COUNT(*) FROM fato_ciclo")),
        (
            "falhas na fato = soma do alvo",
            int(df["falha"].sum()),
            um("SELECT SUM(falha) FROM fato_ciclo"),
        ),
        (
            "linhas na ponte = soma dos 5 modos",
            int(df[["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]].sum().sum()),
            um("SELECT COUNT(*) FROM ponte_ciclo_modo"),
        ),
        (
            "violações de chave estrangeira",
            0,
            len(conn.execute("PRAGMA foreign_key_check").fetchall()),
        ),
        (
            "ciclos sem tipo",
            0,
            um(
                "SELECT COUNT(*) FROM fato_ciclo f LEFT JOIN dim_tipo_produto t USING (id_tipo) "
                "WHERE t.id_tipo IS NULL"
            ),
        ),
        (
            "soma do torque confere",
            round(float(df["torque_nm"].sum()), 4),
            round(float(conn.execute("SELECT SUM(torque_nm) FROM fato_ciclo").fetchone()[0]), 4),
        ),
    ]
    tabela = pd.DataFrame(checagens, columns=["verificacao", "esperado", "obtido"])
    tabela["ok"] = tabela["esperado"] == tabela["obtido"]
    return tabela
