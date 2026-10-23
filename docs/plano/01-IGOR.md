# Tarefas do Igor — T0 (estrutura), T1 (coleta e preparação), T7 (integração e entrega)

> Leia antes: `00-VISAO-GERAL.md`. Identidade git deste repositório:
> `Igor Seberino <igorseberino@gmail.com>` (configurado **local** no clone) · login `igorSeberino`.

Todo o código abaixo foi executado e testado antes de entrar neste plano (Python 3.14, pandas 3.1,
scikit-learn 1.9, ruff e pytest verdes). Pode copiar como está.

---

## T0 — Estrutura do repositório — **feito**

O que existe:

- **Repositório** https://github.com/igorSeberino/data.vigia — commit inicial com `pyproject.toml`,
  `requirements.txt`, `.gitignore`, `.gitattributes`, `CLAUDE.md`, README-esqueleto
  (logo, título, frase, badges) com todas as seções do relatório e os
  marcadores de responsável, `src/manutencao/__init__.py`, `tests/test_estrutura.py`,
  `data/raw/ai4i2020.csv` (SHA-256 conferido), CI (`.github/workflows/ci.yml`), templates de issue
  (bug, débito técnico), `PULL_REQUEST_TEMPLATE.md`, `.github/assets/logo.svg`,
  este plano em `docs/plano/` e o time de agentes em `.claude/` (§11 do plano mestre).
- **Configuração**: só "Create a merge commit"; branch apagada após merge; `main` protegida
  (PR obrigatório, 1 aprovação, check `ci`).
- **Project** `@vigia`: https://github.com/users/igorSeberino/projects/2 (campos, visões e editores na §12).
- **Issues** #1–#7 (tarefas) e #8 (issue-mãe), com labels e Status *Backlog*.
- **Convites** enviados para `adrian-cesar`, `gabrielcarvallho`, `rcolinneto`.

### O que ainda é seu no T0

1. Mandar no grupo (texto pronto):

   > Repo do trabalho criado: https://github.com/igorSeberino/data.vigia
   > Quadro: https://github.com/users/igorSeberino/projects/2
   > 1) Aceitem o convite: https://github.com/igorSeberino/data.vigia/invitations
   > 2) Cada um tem um arquivo em `docs/plano/` (Gabriel 02, Adrian 03, Renato 04). Leiam o
   >    `00-VISAO-GERAL.md` primeiro (seções 8 e 11 explicam o fluxo).
   > 3) Configurem o git com o e-mail da seção 4 e rodem `gh auth refresh -h github.com -s project`.
   >    Abram o `claude` na pasta e rodem `/setup` — commit com e-mail errado não conta como contribuição.
   > 4) Cada um começa com `/tbd-start <número da sua issue>`. Gabriel (#2), Adrian (#3) e Renato (#4)
   >    esperam eu mergear o #1 (aviso aqui). Adrian já pode começar o #5.
2. Quando cada um aceitar (`gh api repos/igorSeberino/data.vigia/collaborators --jq '.[].login'`),
   o próprio `/tbd-start` atribui a issue a quem a assume — não precisa fazer nada.

---

## T1 — Coleta, validação e preparação (issue #1 · `feat/1-data-prep`)

```bash
cd data.vigia
uv venv --python 3.12 .venv && source .venv/Scripts/activate
uv pip install -r requirements.txt
claude      # depois: /setup  e  /tbd-start 1
```

### T1.1 Código (cole exatamente; já testado)

#### `src/manutencao/config.py`

```python
"""Caminhos, constantes e nomes de colunas compartilhados por todo o projeto."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_FIGURAS = RAIZ / "reports" / "figures"
DIR_TABELAS = RAIZ / "reports" / "tables"
DIR_MODELOS = RAIZ / "models"

CAMINHO_CSV = DIR_RAW / "ai4i2020.csv"
CAMINHO_DB = DIR_PROCESSED / "industria40.db"

URL_ZIP = (
    "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
)
SHA256_CSV = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"

SEED = 42

MAPA_COLUNAS = {
    "UDI": "udi",
    "Product ID": "id_produto",
    "Type": "tipo",
    "Air temperature [K]": "temp_ar_k",
    "Process temperature [K]": "temp_processo_k",
    "Rotational speed [rpm]": "rotacao_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "desgaste_ferramenta_min",
    "Machine failure": "falha",
    "TWF": "falha_twf",
    "HDF": "falha_hdf",
    "PWF": "falha_pwf",
    "OSF": "falha_osf",
    "RNF": "falha_rnf",
}

COL_ALVO = "falha"
COL_TIPO = "tipo"
ORDEM_TIPO = ["L", "M", "H"]
COLS_MODOS = ["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]
COLS_NUMERICAS_BRUTAS = [
    "temp_ar_k",
    "temp_processo_k",
    "rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
]
COLS_ENGENHARIA = ["dif_temperatura_k", "potencia_w", "esforco_ferramenta_min_nm"]
COLS_VAZAMENTO = ["udi", "id_produto", *COLS_MODOS]

ATRIBUTOS_BRUTO = [COL_TIPO, *COLS_NUMERICAS_BRUTAS]
ATRIBUTOS_ENGENHARIA = [*ATRIBUTOS_BRUTO, *COLS_ENGENHARIA]

MODOS_FALHA = {
    "TWF": ("falha_twf", "Desgaste da ferramenta"),
    "HDF": ("falha_hdf", "Falha de dissipação de calor"),
    "PWF": ("falha_pwf", "Falha de potência"),
    "OSF": ("falha_osf", "Sobrecarga (overstrain)"),
    "RNF": ("falha_rnf", "Falha aleatória"),
}
```

#### `src/manutencao/util.py`

```python
"""Utilidades de saída: gravação padronizada de figuras e tabelas."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from manutencao.config import DIR_FIGURAS, DIR_TABELAS


def configurar_graficos() -> None:
    """Aplica o estilo visual padrão de todos os notebooks."""
    sns.set_theme(style="whitegrid", context="notebook", palette="deep")
    plt.rcParams.update({"figure.figsize": (9, 5), "figure.dpi": 100, "axes.titleweight": "bold"})


def salvar_figura(fig: plt.Figure, nome: str) -> Path:
    """Grava ``reports/figures/<nome>.png`` e devolve o caminho."""
    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_FIGURAS / f"{nome}.png"
    fig.savefig(caminho, dpi=120, bbox_inches="tight")
    return caminho


def salvar_tabela(df: pd.DataFrame, nome: str, index: bool = False) -> Path:
    """Grava ``reports/tables/<nome>.csv`` (UTF-8, vírgula, ponto decimal) e devolve o caminho."""
    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_TABELAS / f"{nome}.csv"
    df.to_csv(caminho, index=index, encoding="utf-8")
    return caminho
```

#### `src/manutencao/dados.py`

```python
"""Coleta e validação do dataset AI4I 2020 (UCI, id 601)."""

import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from manutencao.config import CAMINHO_CSV, COLS_MODOS, MAPA_COLUNAS, SHA256_CSV, URL_ZIP


def sha256_arquivo(caminho: Path) -> str:
    """Calcula o SHA-256 de um arquivo."""
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def baixar_csv(destino: Path = CAMINHO_CSV, url: str = URL_ZIP) -> Path:
    """Baixa o zip oficial da UCI, extrai ``ai4i2020.csv`` em ``destino`` e confere o SHA-256."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as resposta:
        conteudo = resposta.read()
    with zipfile.ZipFile(io.BytesIO(conteudo)) as zf:
        destino.write_bytes(zf.read("ai4i2020.csv"))
    obtido = sha256_arquivo(destino)
    if obtido != SHA256_CSV:
        raise ValueError(f"SHA-256 inesperado para {destino}: {obtido}")
    return destino


def carregar_bruto(caminho: Path = CAMINHO_CSV, baixar_se_ausente: bool = True) -> pd.DataFrame:
    """Lê o CSV original com os nomes de coluna da fonte.

    O arquivo tem BOM UTF-8 no cabeçalho, por isso ``encoding="utf-8-sig"``.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        if not baixar_se_ausente:
            raise FileNotFoundError(caminho)
        baixar_csv(caminho)
    return pd.read_csv(caminho, encoding="utf-8-sig")


def validar(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Executa as verificações de qualidade e devolve uma tabela ``verificacao, esperado, obtido, ok``."""
    df = df_bruto.rename(columns=MAPA_COLUNAS)
    flags = ["falha", *COLS_MODOS]
    checagens = [
        ("colunas esperadas", sorted(MAPA_COLUNAS.values()), sorted(df.columns)),
        ("quantidade de linhas", 10000, len(df)),
        ("valores ausentes", 0, int(df.isna().sum().sum())),
        ("linhas duplicadas", 0, int(df.duplicated().sum())),
        ("udi único", True, bool(df["udi"].is_unique)),
        ("id_produto único", True, bool(df["id_produto"].is_unique)),
        ("tipo em {L, M, H}", True, bool(df["tipo"].isin(["L", "M", "H"]).all())),
        (
            "1ª letra do id_produto = tipo",
            True,
            bool((df["id_produto"].str[0] == df["tipo"]).all()),
        ),
        (
            "temperaturas entre 290 e 320 K",
            True,
            bool(df[["temp_ar_k", "temp_processo_k"]].stack().between(290, 320).all()),
        ),
        ("temp_processo > temp_ar", True, bool((df["temp_processo_k"] > df["temp_ar_k"]).all())),
        ("rotação > 0", True, bool((df["rotacao_rpm"] > 0).all())),
        ("torque >= 0", True, bool((df["torque_nm"] >= 0).all())),
        ("desgaste >= 0", True, bool((df["desgaste_ferramenta_min"] >= 0).all())),
        ("flags binárias (0/1)", True, bool(df[flags].isin([0, 1]).all().all())),
    ]
    tabela = pd.DataFrame(checagens, columns=["verificacao", "esperado", "obtido"])
    tabela["ok"] = [
        str(e) == str(o) for e, o in zip(tabela["esperado"], tabela["obtido"], strict=True)
    ]
    tabela[["esperado", "obtido"]] = tabela[["esperado", "obtido"]].astype(str)
    return tabela


def inconsistencias_rotulo(df: pd.DataFrame) -> pd.DataFrame:
    """Linhas cujo rótulo geral não bate com os modos de falha.

    Aceita o DataFrame bruto ou o preparado. Devolve as colunas originais mais ``inconsistencia``
    com os valores ``"falha sem modo"`` ou ``"modo sem falha"``.
    """
    d = df.rename(columns=MAPA_COLUNAS)
    algum_modo = d[COLS_MODOS].sum(axis=1) > 0
    sem_modo = (d["falha"] == 1) & ~algum_modo
    sem_falha = (d["falha"] == 0) & algum_modo
    saida = d[sem_modo | sem_falha].copy()
    saida["inconsistencia"] = "falha sem modo"
    saida.loc[sem_falha[sem_modo | sem_falha], "inconsistencia"] = "modo sem falha"
    return saida
```

#### `src/manutencao/preparacao.py`

```python
"""Preparação: renomear, tipar, criar atributos físicos e dividir treino/teste."""

import math

import pandas as pd
from sklearn.model_selection import train_test_split

from manutencao.config import (
    COL_ALVO,
    COL_TIPO,
    COLS_MODOS,
    COLS_VAZAMENTO,
    MAPA_COLUNAS,
    ORDEM_TIPO,
    SEED,
)
from manutencao.dados import carregar_bruto


def adicionar_atributos_fisicos(df: pd.DataFrame) -> pd.DataFrame:
    """Cria os três atributos derivados da física do processo (não altera o original).

    - ``dif_temperatura_k`` = temp_processo_k − temp_ar_k (dissipação de calor)
    - ``potencia_w`` = torque_nm × rotacao_rpm × 2π/60 (potência mecânica em W)
    - ``esforco_ferramenta_min_nm`` = desgaste_ferramenta_min × torque_nm (sobrecarga)
    """
    saida = df.copy()
    saida["dif_temperatura_k"] = saida["temp_processo_k"] - saida["temp_ar_k"]
    saida["potencia_w"] = saida["torque_nm"] * saida["rotacao_rpm"] * 2 * math.pi / 60
    saida["esforco_ferramenta_min_nm"] = saida["desgaste_ferramenta_min"] * saida["torque_nm"]
    return saida


def preparar(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Transforma o DataFrame bruto no DataFrame analítico usado por todos os notebooks."""
    df = df_bruto.rename(columns=MAPA_COLUNAS).copy()
    df["id_produto"] = df["id_produto"].astype(str)
    df[COL_TIPO] = pd.Categorical(df[COL_TIPO].astype(str), categories=ORDEM_TIPO, ordered=True)
    for col in ["udi", "rotacao_rpm", "desgaste_ferramenta_min", COL_ALVO, *COLS_MODOS]:
        df[col] = df[col].astype("int64")
    for col in ["temp_ar_k", "temp_processo_k", "torque_nm"]:
        df[col] = df[col].astype("float64")
    df = adicionar_atributos_fisicos(df)
    return df.sort_values("udi").reset_index(drop=True)


def carregar_preparado() -> pd.DataFrame:
    """Atalho: lê o CSV (baixando se faltar) e devolve o DataFrame preparado."""
    return preparar(carregar_bruto())


def dividir_treino_teste(
    df: pd.DataFrame, proporcao_teste: float = 0.2, seed: int = SEED
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divisão única do projeto: 80/20 estratificada pelo alvo, semente fixa."""
    treino, teste = train_test_split(
        df, test_size=proporcao_teste, stratify=df[COL_ALVO], random_state=seed
    )
    return treino.reset_index(drop=True), teste.reset_index(drop=True)


def separar_x_y(df: pd.DataFrame, atributos: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Separa atributos e alvo, recusando colunas que vazam o alvo ou identificam a linha."""
    proibidas = sorted(set(atributos) & set(COLS_VAZAMENTO + [COL_ALVO]))
    if proibidas:
        raise ValueError(f"Atributos proibidos (vazamento/identificador): {proibidas}")
    return df[atributos].copy(), df[COL_ALVO].copy()
```

#### `tests/conftest.py`

```python
import pytest

from manutencao.dados import carregar_bruto
from manutencao.preparacao import preparar


@pytest.fixture(scope="session")
def df_bruto():
    return carregar_bruto(baixar_se_ausente=False)


@pytest.fixture(scope="session")
def df(df_bruto):
    return preparar(df_bruto)
```

#### `tests/test_dados.py`

```python
from manutencao.config import CAMINHO_CSV, SHA256_CSV
from manutencao.dados import inconsistencias_rotulo, sha256_arquivo, validar


def test_csv_versionado_e_o_arquivo_oficial():
    assert sha256_arquivo(CAMINHO_CSV) == SHA256_CSV


def test_cabecalho_sem_bom(df_bruto):
    assert df_bruto.columns[0] == "UDI"


def test_volume(df_bruto):
    assert df_bruto.shape == (10000, 14)


def test_todas_as_validacoes_passam(df_bruto):
    tabela = validar(df_bruto)
    assert tabela["ok"].all(), tabela[~tabela["ok"]]


def test_inconsistencias_de_rotulo(df_bruto):
    inc = inconsistencias_rotulo(df_bruto)
    contagem = inc["inconsistencia"].value_counts().to_dict()
    assert contagem == {"modo sem falha": 18, "falha sem modo": 9}
```

#### `tests/test_preparacao.py`

```python
import math

import pytest

from manutencao.config import ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA, COLS_VAZAMENTO
from manutencao.preparacao import dividir_treino_teste, separar_x_y


def test_colunas_renomeadas_e_derivadas(df):
    for col in ATRIBUTOS_ENGENHARIA + COLS_VAZAMENTO + ["falha"]:
        assert col in df.columns


def test_tipo_categorico_ordenado(df):
    assert list(df["tipo"].cat.categories) == ["L", "M", "H"]
    assert df["tipo"].cat.ordered
    assert df["tipo"].value_counts().to_dict() == {"L": 6000, "M": 2997, "H": 1003}


def test_atributos_fisicos_da_primeira_linha(df):
    linha = df.loc[df["udi"] == 1].iloc[0]
    assert linha["dif_temperatura_k"] == pytest.approx(10.5)
    assert linha["potencia_w"] == pytest.approx(42.8 * 1551 * 2 * math.pi / 60)
    assert linha["esforco_ferramenta_min_nm"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("regra", "modo", "esperado"),
    [
        (lambda d: (d["dif_temperatura_k"] < 8.6) & (d["rotacao_rpm"] < 1380), "falha_hdf", 115),
        (lambda d: (d["potencia_w"] < 3500) | (d["potencia_w"] > 9000), "falha_pwf", 95),
        (
            lambda d: (
                d["esforco_ferramenta_min_nm"]
                > d["tipo"].map({"L": 11000, "M": 12000, "H": 13000}).astype(float)
            ),
            "falha_osf",
            98,
        ),
    ],
)
def test_atributos_reproduzem_regras_documentadas(df, regra, modo, esperado):
    mascara = regra(df)
    assert int(mascara.sum()) == esperado
    assert (mascara == (df[modo] == 1)).all()


def test_divisao_estratificada_e_deterministica(df):
    treino, teste = dividir_treino_teste(df)
    assert (len(treino), len(teste)) == (8000, 2000)
    assert set(treino["udi"]).isdisjoint(teste["udi"])
    assert abs(treino["falha"].mean() - teste["falha"].mean()) < 0.002
    treino2, _ = dividir_treino_teste(df)
    assert treino["udi"].tolist() == treino2["udi"].tolist()


def test_separar_x_y_recusa_vazamento(df):
    with pytest.raises(ValueError):
        separar_x_y(df, ATRIBUTOS_BRUTO + ["falha_hdf"])
    X, y = separar_x_y(df, ATRIBUTOS_ENGENHARIA)
    assert X.shape == (10000, 9) and y.name == "falha"
```

Commits sugeridos (nesta ordem, cada um com `ruff format . && ruff check . && pytest -q` verde):

1. `feat(config): caminhos, constantes e nomes de colunas do projeto` (config.py, util.py)
2. `feat(dados): leitura do CSV com BOM, download com SHA-256 e validação de qualidade` (dados.py, conftest.py, test_dados.py)
3. `feat(preparacao): renomeação, tipagem, atributos físicos e divisão estratificada` (preparacao.py, test_preparacao.py)
4. `docs(dados): dicionário de dados` (docs/dicionario-de-dados.md)
5. `feat(notebook): 01 coleta e preparação executado` (notebook + reports/tables/01_*)
6. `docs(readme): seções 2.1, 2.2 e tabela de ferramentas da 2.3`

### T1.2 `notebooks/01_coleta_e_preparacao.ipynb` — célula por célula

| # | Tipo | Conteúdo |
|---|---|---|
| 1 | md | `# 01 · Coleta e preparação dos dados` · autor Igor Seberino · fase CRISP-DM: *entendimento e preparação dos dados* · objetivo da etapa em 3 linhas · badge Colab deste notebook |
| 2 | code | Célula padrão de ambiente (CLAUDE.md) |
| 3 | code | `import pandas as pd` · imports de `manutencao.config`, `manutencao.dados`, `manutencao.preparacao`, `manutencao.util` · `configurar_graficos()` · `pd.set_option("display.max_columns", 30)` |
| 4 | md | **1. Fonte**: UCI id 601, Matzka (2020), DOI 10.24432/C5HS5C, CC BY 4.0, dataset sintético que reproduz dados reais de manutenção de uma máquina de usinagem. Explicar que o CSV está versionado e que `baixar_csv()` refaz o download conferindo SHA-256 |
| 5 | code | `df_bruto = carregar_bruto()` · `print(df_bruto.shape)` · `print(sha256_arquivo(CAMINHO_CSV) == SHA256_CSV)` · `df_bruto.head()` |
| 6 | code | `df_bruto.dtypes.to_frame("tipo_pandas")` |
| 7 | md | **2. Validação de qualidade** — o que cada verificação garante |
| 8 | code | `qualidade = validar(df_bruto)` · `salvar_tabela(qualidade, "01_validacao_qualidade")` · `assert qualidade["ok"].all()` · `qualidade` |
| 9 | md | **3. Inconsistências de rótulo** — explicar as 9 "falha sem modo" e 18 "modo sem falha" (RNF), a divergência com a página da UCI (que fala em 5 RNF) e a **decisão D5** (manter o rótulo publicado; tratar como ruído de rótulo; motivo: comparabilidade) |
| 10 | code | `inc = inconsistencias_rotulo(df_bruto)` · `salvar_tabela(inc, "01_inconsistencias_rotulo")` · `inc["inconsistencia"].value_counts()` · `inc.head(10)` |
| 11 | md | **4. Renomeação e tipagem** — tabela original → novo nome (de `MAPA_COLUNAS`) e por que `tipo` vira categórica ordenada L<M<H |
| 12 | code | `df = preparar(df_bruto)` · `df.info()` · `df.head()` |
| 13 | md | **5. Atributos físicos** com as fórmulas em LaTeX: $\Delta T = T_{proc} - T_{ar}$; $P = \tau \cdot \omega = \tau \cdot n \cdot 2\pi/60$; $E = \text{desgaste} \cdot \tau$. Justificar com a física do processo (dissipação de calor, potência, sobrecarga) — conhecimento de domínio que um engenheiro de processo teria |
| 14 | code | Tabela "regra documentada × rótulo": para HDF, PWF, OSF calcular a máscara da regra (mesmas expressões do teste `test_atributos_reproduzem_regras_documentadas`), e montar DataFrame `modo, ciclos_pela_regra, ciclos_com_rotulo, coincidem` · `salvar_tabela(..., "01_regras_vs_rotulos")` |
| 15 | md | Interpretar: as regras batem 100 % → 287 das 339 falhas são deterministicamente explicadas por variáveis medidas; o restante (TWF, RNF, sem modo) é estocástico. Consequência para a modelagem (expectativa de desempenho alto nesses modos, teto no resto) e para a discussão (limitação: dataset sintético) |
| 16 | md | **6. Dicionário de dados** |
| 17 | code | Montar DataFrame `coluna, origem (original/derivada), tipo, unidade, papel (identificador/atributo/alvo/modo de falha — proibido como atributo), descricao` para as 17 colunas de `df` · `salvar_tabela(dic, "01_dicionario_dados")` · exibir |
| 18 | md | **7. Divisão treino/teste** — 80/20 estratificada, SEED=42, única no projeto, teste reservado |
| 19 | code | `treino, teste = dividir_treino_teste(df)` · tabela `conjunto, ciclos, falhas, prevalencia_pct` (treino, teste, total) · `salvar_tabela(..., "01_divisao_treino_teste")` |
| 20 | code | `DIR_PROCESSED.mkdir(parents=True, exist_ok=True)` · `df.to_csv(DIR_PROCESSED / "ai4i_preparado.csv", index=False)` (arquivo ignorado pelo git, só para conferência) |
| 21 | md | **Conclusões da etapa** — 5 a 7 bullets com números tirados das saídas acima |

Executar: `jupyter nbconvert --to notebook --execute --inplace notebooks/01_coleta_e_preparacao.ipynb`
e depois `ruff format notebooks/01_coleta_e_preparacao.ipynb`.

Para criar o `.ipynb`: o Claude Code edita notebooks diretamente; alternativa robusta é escrever
um script no formato *percent* (`# %%` / `# %% [markdown]`) em uma pasta temporária e converter com
`jupytext --to ipynb <script>.py -o notebooks/01_coleta_e_preparacao.ipynb`. **Não** commitar o script.

### T1.3 `docs/dicionario-de-dados.md`

Título, fonte e licença; a mesma tabela do passo 17 em Markdown (17 linhas); uma seção
"Colunas proibidas como atributo" listando `COLS_VAZAMENTO` com o motivo de cada uma; uma seção
"Inconsistências conhecidas" (9 + 18, divergência da UCI).

### T1.4 README — o que escrever

- **§2.1 Descrição dos dados**: fonte (UCI, id 601; Matzka, 2020; DOI), licença, natureza
  (sintético que reflete dados industriais reais de uma máquina de usinagem), **volume**
  (10.000 ciclos × 14 colunas, 522 KB; 3 colunas derivadas → 17 após preparação), **tipos**
  (tabela resumida: identificadores, 1 categórica ordinal, 5 numéricas contínuas/inteiras com
  unidade, 1 alvo binário, 5 modos binários), distribuição do alvo (339 falhas, 3,39 %) e por tipo.
  Link para `docs/dicionario-de-dados.md`.
- **§2.2 Coleta e preparação**: lista numerada do pipeline (download + SHA-256 → leitura com BOM →
  14 verificações de qualidade, todas aprovadas → inconsistências de rótulo e decisão D5 →
  renomeação/tipagem → 3 atributos físicos e prova de que reproduzem as regras → divisão 80/20
  estratificada). Citar `reports/tables/01_*.csv`.
- **§2.3 (abertura) Ferramentas**: tabela `Ferramenta | Uso no trabalho`: Python 3.12; pandas e
  NumPy (manipulação); SQLite/`sqlite3` (modelo dimensional); scikit-learn (modelos, validação);
  SciPy (testes estatísticos); matplotlib e seaborn (gráficos); Jupyter e Google Colab
  (notebooks); pytest e ruff (qualidade); GitHub Actions (CI que executa testes e notebooks);
  uv (ambiente). Uma frase dizendo que a estrutura segue CRISP-DM (SHEARER, 2000) e o mapeamento
  fase → notebook: entendimento do negócio (README §1), entendimento dos dados (01, 03),
  preparação (01, 02), modelagem (04), avaliação (04, 05), implantação (fora do escopo; ver §3.5).

### T1.5 PR

`/tbd-pr` (roda os portões e o `revisor-dados`, cria o PR com o título da issue #1, `Closes #1`,
pede revisão ao `rcolinneto` e move o card para *In Review*). Manual, se precisar:

```bash
git fetch origin && git rebase origin/main
ruff format --check . && ruff check . && pytest -q
git push -u origin feat/1-data-prep
gh pr create --base main --title "feat: coleta, validação e preparação dos dados (notebook 01)" --body-file <PULL_REQUEST_TEMPLATE preenchido, com "Closes #1">
gh pr edit --add-reviewer rcolinneto
```

Depois do merge: `/tbd-pr` de novo e avisar no grupo: "#1 mergeado, podem começar (git pull na main)".

### T1.6 Critérios de aceite

- [ ] `pytest -q` mostra todos os testes passando (13 do T1 + 1 do T0).
- [ ] `validar()` com todas as linhas `ok = True`.
- [ ] Notebook 01 executa sem erro local e no CI; 5 tabelas `reports/tables/01_*.csv`.
- [ ] Commit no GitHub aparece como `igorSeberino`.

---

## T7 — Integração final e entrega (issue #7 · `docs/7-final-report`)

Começa quando T2–T6 estiverem mergeados.

```bash
# /tbd-start 7   (ou: git switch main && git pull && git switch -c docs/7-final-report)
```

### T7.1 Reexecução completa (prova de reprodutibilidade)

```bash
for nb in notebooks/0*.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
ruff format . && ruff check . && pytest -q
git status   # se figuras/tabelas mudarem só em bytes (PNG), tudo bem; se números mudarem, investigar
```

Se algum número de tabela mudou, abrir issue para o dono da seção corrigir o README — não
corrigir sozinho a seção do colega.

### T7.2 Conferência do README (checklist)

- [ ] Nenhum "_Em construção_" (`grep -n "Em construção" README.md` vazio).
- [ ] Todo número citado existe em `reports/tables/` ou saída de notebook (conferir 1 a 1 as seções 3.2 e 3.3).
- [ ] Todas as figuras referenciadas existem (`grep -o "reports/figures/[^)]*" README.md | xargs ls`).
- [ ] Toda citação (AUTOR, ano) do texto está em §4, e toda referência de §4 é citada.
- [ ] Os nomes das seções 1–4 batem com o PDF.
- [ ] Links dos notebooks e badges Colab abrem.

### T7.3 O que escrever

- **Resumo** (150–200 palavras): problema, dados, o que foi feito (modelo dimensional, EDA,
  modelos, análise de custo), principal resultado técnico e financeiro (números das tabelas
  `04_metricas_teste.csv` e `05_estrategias_teste.csv`), principal limitação (dataset sintético).
- **§3.4 Implementação em Python**: diagrama em texto da estrutura (árvore da §6 do plano,
  resumida); tabela módulo → responsabilidade → autor; como executar localmente (uv, comandos) e
  no Colab (badges); reprodutibilidade (CSV versionado + SHA-256, SEED=42, divisão única, CI que
  executa os 5 notebooks a cada PR); qualidade (quantidade de testes pelo `pytest -q`, ruff).
- **§3.5 Considerações finais**: retomar cada objetivo específico de §1.3 e dizer se foi
  atingido e com qual evidência; limitações (sintético, sem série temporal por máquina, custos
  hipotéticos, TWF/RNF estocásticos); trabalhos futuros (dados reais de sensores em série
  temporal, estimativa de vida útil remanescente — RUL, monitoramento de *drift*, implantação
  do modelo junto ao CLP/MES, retreino periódico).
- **Contribuições**: tabela `Integrante | Tarefas | PRs (links) | Revisões feitas | Seções do README`.
  Gerar os dados com:
  ```bash
  gh pr list -R igorSeberino/data.vigia --state merged --json number,title,author,url --jq '.[] | "\(.number)\t\(.author.login)\t\(.title)\t\(.url)"'
  gh api repos/igorSeberino/data.vigia/contributors --jq '.[] | "\(.login)\t\(.contributions)"'
  ```

### T7.4 Colab

Abrir cada badge no Colab (deslogado do GitHub não importa, o repo é público), "Ambiente de
execução → Executar tudo", e conferir que roda até o fim. Se algum falhar só no Colab, abrir issue
para o dono.

### T7.5 PR, release e envio

```bash
# /tbd-pr  (PR "docs: integração final do relatório e entrega", Closes #7, revisores gabrielcarvallho e adrian-cesar)
# após aprovação + CI verde + merge (e /tbd-pr de novo):
gh issue close 8 -R igorSeberino/data.vigia -c "Todas as sub-issues entregues."
git switch main && git pull
gh release create v1.0.0 -R igorSeberino/data.vigia --target main \
  --title "Entrega N2 – Ciência de Dados" \
  --notes "Versão entregue ao Prof. Claudinei Dias. Relatório no README; notebooks em notebooks/."
curl -s -o /dev/null -w "%{http_code}\n" https://github.com/igorSeberino/data.vigia   # 200
gh api repos/igorSeberino/data.vigia/contributors --jq '.[].login'                     # 4 logins
```

Enviar ao professor: `https://github.com/igorSeberino/data.vigia` (e, se o
ambiente de entrega pedir Colab, o link do badge do notebook 01). Depois da entrega, ninguém
mais faz push na `main`.

### T7.6 Critérios de aceite

- [ ] Todos os itens da "Definição de pronto" (§10 do plano mestre) marcados.

---

## Revisões que o Igor faz

- **T4 (Renato)**: conferir que o teste só é usado depois da escolha do modelo; que
  `04_oof_treino.csv` e `04_predicoes_teste.csv` têm as colunas do contrato (§7); que a
  discussão de 3.3.1 menciona o caráter sintético e os modos estocásticos.
- **T5 (Adrian)**: conferir que cada referência tem DOI/URL que abre; que o problema (1.2) e os
  objetivos (1.3) batem com o que os notebooks realmente fazem.

## Roteiro de defesa (o que saber responder)

1. Por que este dataset? (público, licença aberta, problema real de I4.0, documentado, cabe no Colab)
2. Por que o CSV está no repositório e para que serve o SHA-256? (reprodutibilidade, integridade)
3. Por que manter os rótulos inconsistentes? (D5: comparabilidade; documentado como ruído)
4. De onde vêm os três atributos físicos e por que não é "trapaça"? (física do processo; regras
   documentadas pela fonte; é conhecimento que o engenheiro de processo tem; a limitação é
   discutida)
5. Por que uma única função de divisão, estratificada? (classe rara; todos avaliam no mesmo teste)
6. Como o CI garante que o relatório não está "maquiado"? (executa os 5 notebooks do zero a cada PR)
