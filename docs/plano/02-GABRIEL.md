# Tarefas do Gabriel — T2 (modelo dimensional em SQLite) e T6 (impacto no negócio)

> Leia antes: `00-VISAO-GERAL.md` (principalmente §3, §7 e §8).
> Identidade git: `Gabriel Carvalho <gabriellccarvalho.dev@gmail.com>` · login `gabrielcarvallho`.
> Revisor do seu T2: **Adrian**. Revisor do seu T6: **Renato**. Você revisa: **T3 (Adrian)** e **T7 (Igor)**.

O código de referência abaixo foi executado e testado antes de entrar no plano (ruff e pytest
verdes, resultados conferidos com o dataset real). Pode usar como está; se mudar algo, os testes
continuam valendo como especificação.

---

## Preparação (uma vez)

```bash
# 1) aceitar o convite: https://github.com/igorSeberino/data.vigia/invitations
git clone https://github.com/igorSeberino/data.vigia.git   # fora de OneDrive/Drive
cd data.vigia
git config user.name "Gabriel Carvalho"
git config user.email "gabriellccarvalho.dev@gmail.com"
gh auth refresh -h github.com -s project                  # para mover os cards do Project
uv venv --python 3.12 .venv
source .venv/Scripts/activate        # Windows Git Bash (macOS/Linux: source .venv/bin/activate)
uv pip install -r requirements-dev.txt
claude                               # na sessão: /setup — só siga com tudo OK
```

Fluxo de cada tarefa (detalhe na §8 e §12 do plano mestre): `/tbd-start <issue>` →
implementação seguindo este arquivo → `/tbd-commit` a cada commit sugerido → `/tbd-pr` → merge →
`/tbd-pr` de novo para finalizar.

---

## T2 — Modelo dimensional em SQLite (issue #2 · `feat/2-star-schema`)

```bash
/tbd-start 2      # assume a issue #2, card em In Progress, branch feat/2-star-schema
```

### Por que um modelo dimensional (o que você vai defender)

- O enunciado pede "construir modelos de dados" e "ferramentas e técnicas de modelagem de dados".
  Além do modelo preditivo (Renato), o grupo entrega um **modelo de dados analítico**: esquema
  estrela (KIMBALL; ROSS, 2013), que é como dados de sensores de chão de fábrica costumam ser
  organizados para BI/análise.
- **Grão** da fato: 1 linha = 1 ciclo de processo (`udi`).
- `id_produto` é único por linha (10.000 valores) → **dimensão degenerada** (fica na fato; uma
  tabela de produto teria 1 linha por fato, sem ganho).
- `dim_tipo_produto` guarda atributos do tipo, inclusive o **limite de esforço** (11/12/13 mil
  min·Nm) — conhecimento de engenharia que vira atributo de dimensão e permite consultas como
  "ciclos acima do limite do seu tipo".
- `dim_faixa_desgaste` é uma **dimensão de faixas** (*band dimension*) para agrupar o desgaste.
- Um ciclo pode ter mais de um modo de falha (24 ciclos) → relação N:N → **tabela ponte**
  `ponte_ciclo_modo`.
- Não há data/hora no dataset → **não existe dimensão de tempo** (limitação, citar).
- SQLite: vem com o Python (`sqlite3`), zero instalação, roda no Colab.

### T2.1 `src/manutencao/modelo_dados.py`

```python
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
```

### T2.2 `tests/test_modelo_dados.py`

```python
import pytest

from manutencao.modelo_dados import (
    CONSULTAS,
    carregar,
    conectar,
    consultar,
    criar_schema,
    executar_consultas,
    verificar_integridade,
)


@pytest.fixture(scope="module")
def conn(df):
    c = conectar(":memory:")
    criar_schema(c)
    carregar(c, df)
    yield c
    c.close()


def test_contagem_das_tabelas(conn):
    contagens = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in [
            "dim_tipo_produto",
            "dim_faixa_desgaste",
            "dim_modo_falha",
            "fato_ciclo",
            "ponte_ciclo_modo",
        ]
    }
    assert contagens == {
        "dim_tipo_produto": 3,
        "dim_faixa_desgaste": 5,
        "dim_modo_falha": 5,
        "fato_ciclo": 10000,
        "ponte_ciclo_modo": 373,
    }


def test_integridade(conn, df):
    tabela = verificar_integridade(conn, df)
    assert tabela["ok"].all(), tabela[~tabela["ok"]]


def test_taxa_falha_por_tipo(conn):
    t = consultar(conn, CONSULTAS["taxa_falha_por_tipo"]).set_index("tipo")
    assert t["falhas"].to_dict() == {"L": 235, "M": 83, "H": 21}
    assert t.loc["L", "taxa_falha_pct"] == pytest.approx(3.92)


def test_falhas_por_faixa_de_desgaste(conn):
    t = consultar(conn, CONSULTAS["taxa_falha_por_faixa_desgaste"])
    assert t["ciclos"].tolist() == [2349, 2271, 2290, 2289, 801]
    assert t["falhas"].tolist() == [52, 51, 52, 61, 123]


def test_inconsistencias(conn):
    t = consultar(conn, CONSULTAS["inconsistencias_rotulo"]).set_index("inconsistencia")
    assert t["ciclos"].to_dict() == {"falha sem modo": 9, "modo sem falha": 18}


def test_esforco_acima_do_limite_bate_com_osf(conn):
    t = consultar(conn, CONSULTAS["esforco_acima_do_limite"])
    assert (t["ciclos_acima"] == t["ciclos_com_osf"]).all()
    assert int(t["ciclos_acima"].sum()) == 98


def test_todas_as_consultas_rodam(conn):
    resultados = executar_consultas(conn)
    assert set(resultados) == set(CONSULTAS)
    assert all(len(r) > 0 for r in resultados.values())
```

### T2.3 `docs/modelo-de-dados.md`

Conteúdo (nesta ordem):

1. **Objetivo** do modelo (2–3 linhas) e **grão** da fato.
2. **Diagrama ER** em Mermaid (o GitHub renderiza):

   ````markdown
   ```mermaid
   erDiagram
       dim_tipo_produto ||--o{ fato_ciclo : "classifica"
       dim_faixa_desgaste ||--o{ fato_ciclo : "agrupa"
       fato_ciclo ||--o{ ponte_ciclo_modo : "registra"
       dim_modo_falha ||--o{ ponte_ciclo_modo : "descreve"
       dim_tipo_produto {
           INTEGER id_tipo PK
           TEXT codigo "L, M, H"
           TEXT descricao
           REAL participacao_nominal
           REAL limite_esforco_min_nm
       }
       dim_faixa_desgaste {
           INTEGER id_faixa PK
           TEXT rotulo
           INTEGER minimo_min
           INTEGER maximo_min
       }
       dim_modo_falha {
           INTEGER id_modo PK
           TEXT sigla "TWF HDF PWF OSF RNF"
           TEXT nome
           TEXT regra
       }
       fato_ciclo {
           INTEGER udi PK
           TEXT id_produto "dimensão degenerada"
           INTEGER id_tipo FK
           INTEGER id_faixa FK
           REAL temp_ar_k
           REAL temp_processo_k
           INTEGER rotacao_rpm
           REAL torque_nm
           INTEGER desgaste_ferramenta_min
           REAL dif_temperatura_k
           REAL potencia_w
           REAL esforco_ferramenta_min_nm
           INTEGER falha
       }
       ponte_ciclo_modo {
           INTEGER udi PK, FK
           INTEGER id_modo PK, FK
       }
   ```
   ````
3. **Decisões de modelagem** (as bullets da seção "Por que um modelo dimensional").
4. **Dicionário das tabelas**: para cada tabela, uma tabela Markdown `coluna | tipo | descrição | origem`.
5. **Integridade**: as 6 verificações de `verificar_integridade` e o resultado (copiar de
   `reports/tables/02_integridade.csv`).
6. **Consultas analíticas**: nome, pergunta de negócio que responde, e o arquivo de resultado.

### T2.4 `notebooks/02_modelo_de_dados_sql.ipynb` — célula por célula

| # | Tipo | Conteúdo |
|---|---|---|
| 1 | md | `# 02 · Modelo de dados dimensional (SQLite)` · autor Gabriel Carvalho · fase CRISP-DM: preparação dos dados · objetivo · badge Colab |
| 2 | code | Célula padrão de ambiente (CLAUDE.md) |
| 3 | code | `import matplotlib.pyplot as plt`, `import seaborn as sns`, `import pandas as pd` · `from manutencao.config import CAMINHO_DB` · `from manutencao.preparacao import carregar_preparado` · `from manutencao import modelo_dados as md` · `from manutencao.util import configurar_graficos, salvar_figura, salvar_tabela` · `configurar_graficos()` |
| 4 | md | Por que um modelo dimensional; grão; dimensão degenerada; ponte; sem dimensão de tempo. Diagrama Mermaid (mesmo do doc) |
| 5 | code | `df = carregar_preparado()` · `caminho = md.construir_banco(df)` · `conn = md.conectar(caminho)` |
| 6 | code | Esquema físico: `md.consultar(conn, "SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type DESC, name")` |
| 7 | code | Volume por tabela: DataFrame `tabela, linhas` para as 5 tabelas · `salvar_tabela(..., "02_volume_tabelas")` |
| 8 | md | Integridade: o que cada verificação garante |
| 9 | code | `integ = md.verificar_integridade(conn, df)` · `salvar_tabela(integ, "02_integridade")` · `assert integ["ok"].all()` · `integ` |
| 10 | md | Consultas analíticas: para cada uma, a **pergunta de negócio** |
| 11 | code | `resultados = md.executar_consultas(conn)` · `for nome, tab in resultados.items(): salvar_tabela(tab, f"02_{nome}")` |
| 12 | code | Exibir `md.CONSULTAS["taxa_falha_por_tipo"]` (print do SQL) e `resultados["taxa_falha_por_tipo"]`; gráfico de barras de `taxa_falha_pct` por tipo → `salvar_figura(fig, "02_taxa_falha_por_tipo")` |
| 13 | code | `falhas_por_modo`: SQL + tabela + barras horizontais → `"02_falhas_por_modo"` |
| 14 | code | `coocorrencia_modos`: SQL + tabela; comentar que 24 ciclos têm mais de um modo |
| 15 | code | `taxa_falha_por_faixa_desgaste`: SQL + tabela + barras → `"02_taxa_falha_por_faixa_desgaste"` |
| 16 | code | `taxa_falha_por_tipo_e_faixa`: pivot (`tipo` × `faixa_desgaste`, valor `taxa_falha_pct`) + `sns.heatmap(annot=True, fmt=".1f")` → `"02_heatmap_tipo_faixa"` |
| 17 | code | `perfil_sensores_por_modo`: SQL + tabela; comentar o que cada modo tem de diferente frente a "SEM FALHA" |
| 18 | code | `esforco_acima_do_limite`: SQL + tabela; mostrar que `ciclos_acima == ciclos_com_osf` (o atributo da dimensão explica 100 % do OSF) |
| 19 | code | `inconsistencias_rotulo`: SQL + tabela; mesma contagem do notebook 01 (9 e 18) |
| 20 | code | `conn.close()` |
| 21 | md | **Conclusões** (5–7 bullets com números das tabelas): ex. salto da taxa de falha na faixa 200+ min, diferença entre tipos, modos mais frequentes, coocorrência, OSF totalmente explicado pelo limite do tipo |

Executar `jupyter nbconvert --to notebook --execute --inplace notebooks/02_modelo_de_dados_sql.ipynb`
e `ruff format notebooks/02_modelo_de_dados_sql.ipynb`. O arquivo `data/processed/industria40.db`
**não** é commitado (está no `.gitignore`).

### T2.5 README — o que escrever

- **§2.3.1 Modelagem dimensional**: técnica (esquema estrela, Kimball), grão, dimensões, fato,
  dimensão degenerada, dimensão de faixas, tabela ponte, ausência de dimensão de tempo; SQLite.
  Link para `docs/modelo-de-dados.md`.
- **§3.1.1 Modelo dimensional (implementação)**: o diagrama Mermaid; volumes das tabelas
  (`02_volume_tabelas.csv`); verificações de integridade (`02_integridade.csv`); como o banco é
  gerado (`construir_banco`), por que é recriado a cada execução.
- **§3.2.2 Consultas analíticas**: 4–6 achados, cada um com o número e o arquivo de origem;
  embutir `02_heatmap_tipo_faixa.png` e `02_taxa_falha_por_faixa_desgaste.png`.
- **§4**: acrescentar KIMBALL; ROSS (2013) se o Adrian ainda não tiver colocado (combinar com ele).
- Linha na tabela **Uso de IA**.

### T2.6 Commits sugeridos

1. `feat(modelo-dados): DDL do esquema estrela com dimensão degenerada e tabela ponte`
2. `feat(modelo-dados): carga das dimensões, fato e ponte a partir do DataFrame preparado`
3. `feat(modelo-dados): consultas analíticas e verificação de integridade`
4. `test(modelo-dados): contagens, integridade e resultados das consultas`
5. `docs(modelo-dados): diagrama ER e dicionário das tabelas`
6. `feat(notebook): 02 modelo de dados executado`
7. `docs(readme): seções 2.3.1, 3.1.1 e 3.2.2`

PR: `/tbd-pr` — título = título da issue #2, corpo pelo template com `Closes #2`, revisor
`adrian-cesar` (o skill pede a revisão e move o card para *In Review*).

### T2.7 Critérios de aceite

- [ ] `pytest -q` verde (os 7 testes do T2 + os anteriores).
- [ ] Notebook 02 roda do início ao fim; 8 tabelas de consulta `02_*.csv` + `02_volume_tabelas.csv` + `02_integridade.csv`; 4 figuras.
- [ ] `docs/modelo-de-dados.md` com Mermaid renderizando no GitHub.
- [ ] Commits aparecem como `gabrielcarvallho`.

---

## T6 — Impacto no negócio: custo e estratégias de manutenção (issue #6 · `feat/6-business-impact`)

**Dependência:** o notebook 05 lê `reports/tables/04_oof_treino.csv` e
`reports/tables/04_predicoes_teste.csv`, gerados pelo Renato (T4). Você pode criar o branch, o
`custo.py` e os testes **logo depois do T1**; o notebook só depois do T4 mergeado
(`git pull --rebase origin main`).

```bash
/tbd-start 6      # assume a issue #6, card em In Progress, branch feat/6-business-impact
```

### Modelo de custo (o que você vai defender)

| Situação | O que acontece | Custo |
|---|---|---|
| Alerta e o ciclo ia falhar (VP) | intervenção planejada evita a falha | `intervencao` |
| Alerta e o ciclo não ia falhar (FP) | intervenção desnecessária | `intervencao` |
| Sem alerta e o ciclo falha (FN) | parada não planejada, reparo, refugo | `falha` |
| Sem alerta e sem falha (VN) | nada | 0 |

- Valores são **hipóteses do grupo**: `intervencao = R$ 500`, `falha = R$ 5.000` (razão 10).
  O dataset não traz custos; o que muda as decisões é a **razão** falha/intervenção, por isso a
  **análise de sensibilidade** com razões 2, 5, 10, 20, 50. Escrever isso explicitamente no
  notebook e no README — nunca apresentar como custo real de mercado.
- Três estratégias, todas com parâmetros escolhidos **no treino** e medidas **no teste**:
  1. **Corretiva**: nunca intervém.
  2. **Preventiva**: intervém quando `desgaste_ferramenta_min >= L`; `L` escolhido no treino
     (grade 0–255 de 5 em 5) minimizando o custo.
  3. **Preditiva**: intervém quando `proba >= t`; `t` escolhido nas predições *out-of-fold* do
     treino (`04_oof_treino.csv`), minimizando o custo.

### T6.1 `src/manutencao/custo.py`

```python
"""Análise de custo: limiar ótimo e comparação de estratégias de manutenção."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Custos:
    """Hipóteses de custo (R$). Só a razão falha/intervenção altera as decisões."""

    intervencao: float = 500.0
    falha: float = 5000.0


CUSTOS_PADRAO = Custos()


def custo_total(y: np.ndarray, alerta: np.ndarray, custos: Custos = CUSTOS_PADRAO) -> dict:
    """Custo de uma política de alertas.

    Alerta (VP ou FP) → paga ``intervencao`` (inspeção/troca planejada; a falha é evitada).
    Falha sem alerta (FN) → paga ``falha`` (parada não planejada + reparo + refugo).
    Sem falha e sem alerta (VN) → 0.
    """
    y = np.asarray(y).astype(int)
    alerta = np.asarray(alerta).astype(int)
    vp = int(((y == 1) & (alerta == 1)).sum())
    fp = int(((y == 0) & (alerta == 1)).sum())
    fn = int(((y == 1) & (alerta == 0)).sum())
    vn = int(((y == 0) & (alerta == 0)).sum())
    total = (vp + fp) * custos.intervencao + fn * custos.falha
    return {
        "vp": vp,
        "fp": fp,
        "fn": fn,
        "vn": vn,
        "intervencoes": vp + fp,
        "falhas_evitadas": vp,
        "falhas_nao_evitadas": fn,
        "custo_total": float(total),
        "custo_por_1000_ciclos": float(1000 * total / len(y)),
    }


def curva_custo_limiar(y, proba, custos: Custos = CUSTOS_PADRAO, limiares=None) -> pd.DataFrame:
    """Custo total para cada limiar de probabilidade."""
    if limiares is None:
        limiares = np.round(np.arange(0.01, 1.0, 0.01), 2)
    proba = np.asarray(proba)
    linhas = [{"limiar": float(t), **custo_total(y, proba >= t, custos)} for t in limiares]
    return pd.DataFrame(linhas)


def melhor_limiar(curva: pd.DataFrame) -> float:
    """Limiar de menor custo (empate → o maior limiar, que gera menos intervenções)."""
    minimo = curva["custo_total"].min()
    return float(curva.loc[curva["custo_total"] == minimo, "limiar"].max())


def estrategia_corretiva(y, custos: Custos = CUSTOS_PADRAO) -> dict:
    """Nunca intervém: toda falha vira parada não planejada."""
    y = np.asarray(y)
    return {"estrategia": "corretiva", "parametro": "-", **custo_total(y, np.zeros_like(y), custos)}


def melhor_limite_desgaste(
    desgaste, y, custos: Custos = CUSTOS_PADRAO, grade=range(0, 260, 5)
) -> int:
    """Limite de desgaste (min) que minimiza o custo da preventiva — escolhido no TREINO."""
    desgaste = np.asarray(desgaste)
    custos_grade = {lim: custo_total(y, desgaste >= lim, custos)["custo_total"] for lim in grade}
    minimo = min(custos_grade.values())
    return max(lim for lim, c in custos_grade.items() if c == minimo)


def estrategia_preventiva(desgaste, y, limite_min: int, custos: Custos = CUSTOS_PADRAO) -> dict:
    """Intervém sempre que o desgaste da ferramenta atinge ``limite_min``."""
    alerta = np.asarray(desgaste) >= limite_min
    return {
        "estrategia": "preventiva",
        "parametro": f"desgaste >= {limite_min} min",
        **custo_total(y, alerta, custos),
    }


def estrategia_preditiva(proba, y, limiar: float, custos: Custos = CUSTOS_PADRAO) -> dict:
    """Intervém quando a probabilidade prevista atinge ``limiar``."""
    return {
        "estrategia": "preditiva",
        "parametro": f"proba >= {limiar:.2f}",
        **custo_total(y, np.asarray(proba) >= limiar, custos),
    }


def sensibilidade(
    y_oof,
    proba_oof,
    desgaste_treino,
    y_teste,
    proba_teste,
    desgaste_teste,
    razoes=(2, 5, 10, 20, 50),
    intervencao: float = 500.0,
) -> pd.DataFrame:
    """Para cada razão falha/intervenção: escolhe parâmetros no treino e mede no teste."""
    linhas = []
    for razao in razoes:
        c = Custos(intervencao=intervencao, falha=intervencao * razao)
        lim = melhor_limiar(curva_custo_limiar(y_oof, proba_oof, c))
        lim_desg = melhor_limite_desgaste(desgaste_treino, y_oof, c)
        for r in (
            estrategia_corretiva(y_teste, c),
            estrategia_preventiva(desgaste_teste, y_teste, lim_desg, c),
            estrategia_preditiva(proba_teste, y_teste, lim, c),
        ):
            linhas.append({"razao_falha_intervencao": razao, **r})
    return pd.DataFrame(linhas)
```

### T6.2 `tests/test_custo.py`

```python
import numpy as np
import pytest

from manutencao.custo import (
    Custos,
    curva_custo_limiar,
    custo_total,
    estrategia_corretiva,
    estrategia_preditiva,
    estrategia_preventiva,
    melhor_limiar,
    melhor_limite_desgaste,
)

Y = np.array([0, 0, 0, 1, 1])
C = Custos(intervencao=100, falha=1000)


def test_custo_total_a_mao():
    r = custo_total(Y, np.array([0, 1, 0, 1, 0]), C)
    assert (r["vp"], r["fp"], r["fn"], r["vn"]) == (1, 1, 1, 2)
    assert r["custo_total"] == 2 * 100 + 1 * 1000
    assert r["custo_por_1000_ciclos"] == pytest.approx(1000 * 1200 / 5)


def test_corretiva_paga_todas_as_falhas():
    assert estrategia_corretiva(Y, C)["custo_total"] == 2000


def test_preventiva_por_desgaste():
    desgaste = np.array([10, 20, 210, 220, 50])
    r = estrategia_preventiva(desgaste, Y, 200, C)
    assert (r["vp"], r["fp"], r["fn"]) == (1, 1, 1)


def test_melhor_limite_desgaste():
    desgaste = np.array([10, 20, 30, 220, 230])
    assert melhor_limite_desgaste(desgaste, Y, C, grade=range(0, 260, 5)) == 220


def test_limiar_otimo_separa_classes():
    proba = np.array([0.05, 0.1, 0.2, 0.7, 0.9])
    curva = curva_custo_limiar(Y, proba, C)
    t = melhor_limiar(curva)
    assert 0.2 < t <= 0.7
    assert estrategia_preditiva(proba, Y, t, C)["custo_total"] == 200
```

### T6.3 `notebooks/05_impacto_no_negocio.ipynb` — célula por célula

| # | Tipo | Conteúdo |
|---|---|---|
| 1 | md | `# 05 · Impacto no negócio` · autor Gabriel Carvalho · fase CRISP-DM: avaliação · objetivo · badge Colab |
| 2 | code | Célula padrão de ambiente |
| 3 | code | imports: `numpy as np`, `pandas as pd`, `matplotlib.pyplot as plt`, `seaborn as sns`; `from manutencao.config import DIR_TABELAS`; `from manutencao.preparacao import carregar_preparado, dividir_treino_teste`; `from manutencao import custo as cu`; util; `configurar_graficos()` |
| 4 | md | Modelo de custo (a tabela acima) e as hipóteses, com o aviso de que são hipotéticas |
| 5 | code | `oof = pd.read_csv(DIR_TABELAS / "04_oof_treino.csv")` · `pred = pd.read_csv(DIR_TABELAS / "04_predicoes_teste.csv")` · `treino, teste = dividir_treino_teste(carregar_preparado())` · juntar o desgaste por `udi`: `oof = oof.merge(treino[["udi", "desgaste_ferramenta_min"]], on="udi", validate="one_to_one")` e idem para `pred` com `teste` · `assert len(oof) == 8000 and len(pred) == 2000` · `assert (oof["falha"].sum(), pred["falha"].sum()) == (int(treino["falha"].sum()), int(teste["falha"].sum()))` |
| 6 | md | Escolha do limiar no treino (por que não no teste) |
| 7 | code | `custos = cu.Custos()` · `curva = cu.curva_custo_limiar(oof["falha"], oof["proba"], custos)` · `t = cu.melhor_limiar(curva)` · `salvar_tabela(curva, "05_curva_custo_limiar_treino")` · print de `t` |
| 8 | code | Gráfico: `custo_total` × `limiar` (treino OOF, linha cheia) e a mesma curva calculada no teste (`cu.curva_custo_limiar(pred["falha"], pred["proba"], custos)`, tracejada, **só para visualização**), linha vertical em `t` e em 0,5 → `"05_curva_custo_limiar"` |
| 9 | code | `L = cu.melhor_limite_desgaste(oof["desgaste_ferramenta_min"], oof["falha"], custos)` (usa só treino) |
| 10 | md | Comparação das estratégias no teste |
| 11 | code | `estrategias = pd.DataFrame([cu.estrategia_corretiva(pred["falha"], custos), cu.estrategia_preventiva(pred["desgaste_ferramenta_min"], pred["falha"], L, custos), cu.estrategia_preditiva(pred["proba"], pred["falha"], t, custos)])` · colunas extras: `economia_vs_corretiva_pct` e `economia_vs_preventiva_pct` · `salvar_tabela(estrategias, "05_estrategias_teste")` · exibir |
| 12 | code | Barras de `custo_por_1000_ciclos` por estratégia, com rótulo em R$ → `"05_comparacao_estrategias"` |
| 13 | code | Matriz de confusão da estratégia preditiva no limiar `t` (VP, FP, FN, VN de `estrategias`) em heatmap → `"05_matriz_confusao_limiar_custo"`; comparar com o limiar 0,5 do notebook 04 (quantas falhas a mais são evitadas e quantos alarmes a mais) |
| 14 | md | Sensibilidade à razão de custos |
| 15 | code | `sens = cu.sensibilidade(oof["falha"], oof["proba"], oof["desgaste_ferramenta_min"], pred["falha"], pred["proba"], pred["desgaste_ferramenta_min"])` · `salvar_tabela(sens, "05_sensibilidade")` · exibir pivot `razao × estrategia` de `custo_por_1000_ciclos` |
| 16 | code | Linhas: `custo_por_1000_ciclos` × razão, uma linha por estratégia, eixo y em escala log → `"05_sensibilidade"` |
| 17 | md | **Conclusões** com números de `05_estrategias_teste.csv` e `05_sensibilidade.csv`: economia da preditiva vs corretiva e vs preventiva na razão 10; em que razões a vantagem se mantém; quantas falhas ainda passam (e que são de quais modos — cruzar com `04_recall_por_modo.csv`); o limiar escolhido cai quando a falha fica mais cara (explicar o porquê) |

### T6.4 README — o que escrever

- **§2.4.3 Análise de custo**: modelo de custo (tabela), hipóteses, três estratégias, regra
  "escolher no treino, medir no teste", sensibilidade.
- **§3.2.4 Impacto financeiro**: tabela resumida das 3 estratégias (custo por 1.000 ciclos,
  intervenções, falhas evitadas/não evitadas), economia percentual; embutir
  `05_comparacao_estrategias.png` e `05_sensibilidade.png`.
- **§3.3.2 Eficácia para o negócio**: a solução reduz custo? em quais condições (razões)? o
  que a preventiva por desgaste não consegue pegar (HDF/PWF não dependem de desgaste); riscos
  (custos hipotéticos, dataset sintético, falhas aleatórias continuam acontecendo); o que seria
  preciso para implantar (custos reais, piloto em uma máquina, monitoramento).
- Linha na tabela **Uso de IA**.

### T6.5 Commits sugeridos

1. `feat(custo): modelo de custo por matriz de confusão`
2. `feat(custo): curva custo × limiar e escolha do limiar no treino`
3. `feat(custo): estratégias corretiva, preventiva e preditiva e análise de sensibilidade`
4. `test(custo): casos calculados à mão`
5. `feat(notebook): 05 impacto no negócio executado`
6. `docs(readme): seções 2.4.3, 3.2.4 e 3.3.2`

PR: `/tbd-pr` — título = título da issue #6, `Closes #6`, revisor `rcolinneto`.

### T6.6 Critérios de aceite

- [ ] `pytest -q` verde (5 testes do T6 + anteriores).
- [ ] Notebook 05 roda após o 04; 3 tabelas `05_*` + curva; 4 figuras.
- [ ] Nenhum parâmetro (limiar, limite de desgaste) escolhido olhando o teste.
- [ ] Texto deixa claro que os custos são hipotéticos.

---

## Suas revisões

- **T3 (Adrian)**: rodar `pytest -q`; conferir que nenhuma função de `eda.py` começa com `test`;
  que as figuras têm título/eixos com unidade; que a conclusão sobre `tipo` usa o V de Cramér
  (efeito pequeno mesmo com p < 0,05). Comentar pelo menos 1 ponto.
- **T7 (Igor)**: conferir que os números de 3.2.2, 3.2.4 e 3.3.2 do README continuam batendo com
  as tabelas após a reexecução final, e que a tabela de Contribuições está certa para você.

## Roteiro de defesa

1. O que é grão, fato, dimensão, dimensão degenerada, ponte — e por que cada uma aqui.
2. Por que não existe `dim_produto` nem `dim_tempo`.
3. Como você garante que o banco está íntegro (6 verificações).
4. O que a consulta `esforco_acima_do_limite` prova.
5. Por que o limiar é escolhido nas predições OOF e não no teste.
6. Por que a sensibilidade importa mais que o valor absoluto de R$.
7. Por que a preventiva por desgaste perde para a preditiva (HDF e PWF não dependem de desgaste).
