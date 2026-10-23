# Tarefas do Adrian — T3 (análise exploratória) e T5 (introdução, objetivos e referências)

> Leia antes: `00-VISAO-GERAL.md` (principalmente §2, §3, §8 e §9).
> Identidade git: `Adrian Cesar Gonçalves <adriancg3006@gmail.com>` · login `adrian-cesar`.
> Revisor do seu T3: **Gabriel**. Revisor do seu T5: **Igor**. Você revisa: **T2 (Gabriel)** e **T7 (Igor)**.

O código de referência abaixo foi executado e testado antes de entrar no plano (ruff e pytest
verdes, resultados conferidos no dataset real).

---

## Preparação (uma vez)

```bash
# 1) aceitar o convite: https://github.com/igorSeberino/data.vigia/invitations
git clone https://github.com/igorSeberino/data.vigia.git   # fora de OneDrive/Drive
cd data.vigia
git config user.name "Adrian Cesar Gonçalves"
git config user.email "adriancg3006@gmail.com"
gh auth refresh -h github.com -s project                  # para mover os cards do Project
uv venv --python 3.12 .venv
source .venv/Scripts/activate        # Windows Git Bash (macOS/Linux: source .venv/bin/activate)
uv pip install -r requirements.txt
claude                               # na sessão: /setup — só siga com tudo OK
```

Fluxo de cada tarefa (detalhe na §8 e §11 do plano mestre): `/tbd-start <issue>` →
implementação seguindo este arquivo → `/tbd-commit` a cada commit sugerido → `/tbd-pr` → merge →
`/tbd-pr` de novo para finalizar.

Ordem: **T5 pode começar já** (só texto, depende só do T0). **T3 começa depois do T1 mergeado.**
São dois branches e dois PRs separados.

---

## T5 — Introdução, objetivos e referências (issue #5 · `docs/5-intro-references`)

```bash
/tbd-start 5      # assume a issue #5, card em In Progress, branch docs/5-intro-references
```

Edita **apenas** as seções 1.1, 1.2, 1.3 e 4 do `README.md` (troca o "_Em construção_").
Estilo: português formal, frases curtas, citações ABNT autor-data no texto — (MATZKA, 2020),
(KAGERMANN; WAHLSTER; HELBIG, 2013), (ZONTA *et al.*, 2020).

### §1.1 A Indústria 4.0 e sua importância (3–4 parágrafos)

Conteúdo obrigatório:
- Origem do termo: iniciativa estratégica alemã *Industrie 4.0*, recomendações de 2013
  (KAGERMANN; WAHLSTER; HELBIG, 2013).
- Pilares: sistemas ciberfísicos, Internet das Coisas industrial, big data/analytics, computação
  em nuvem, integração vertical e horizontal (LEE; BAGHERI; KAO, 2015).
- Por que importa hoje: produtividade, qualidade, flexibilidade, decisões orientadas por dados;
  contexto brasileiro (CNI, 2016).
- A ciência de dados é o elo que transforma dados de sensores em decisão; a **manutenção
  preditiva** é uma das aplicações mais citadas (ZONTA *et al.*, 2020; CARVALHO *et al.*, 2019).

### §1.2 Definição do problema (2–3 parágrafos)

- Três estratégias de manutenção: corretiva (conserta depois que quebra), preventiva (por tempo/uso),
  preditiva (por condição, com dados) (MOBLEY, 2002).
- Problema real: falhas não planejadas param a linha, geram refugo e custo; troca preventiva
  cedo demais desperdiça ferramenta, tarde demais não evita a falha.
- **Problema deste trabalho:** em uma máquina de usinagem monitorada por sensores (temperaturas
  do ar e do processo, rotação, torque e desgaste da ferramenta), prever se um ciclo de processo
  vai falhar e decidir quando intervir com o menor custo esperado.
- Dados: AI4I 2020, conjunto sintético publicado para reproduzir dados reais de manutenção
  preditiva (MATZKA, 2020). Dizer já aqui que ser sintético é uma limitação discutida em §3.3.

### §1.3 Objetivos

**Objetivo geral:** aplicar o ciclo de ciência de dados (coleta, preparação, modelagem de dados,
análise e avaliação) para propor uma política de manutenção preditiva baseada em dados para a
máquina do AI4I 2020.

**Objetivos específicos** (numerados — o Igor vai retomá-los um a um em §3.5):
1. Coletar, validar e preparar o conjunto de dados, documentando a qualidade e as inconsistências.
2. Construir um modelo de dados dimensional (esquema estrela) que permita consultas analíticas sobre os ciclos e as falhas.
3. Caracterizar estatisticamente as variáveis associadas à falha.
4. Treinar e comparar modelos de classificação para prever a falha de um ciclo, com validação adequada a dados desbalanceados.
5. Estimar o impacto financeiro da manutenção preditiva frente às estratégias corretiva e preventiva.
6. Disponibilizar uma implementação em Python reprodutível e documentada.

### §4 Referências (ABNT NBR 6023, ordem alfabética)

**Antes de colar, abrir cada DOI/URL e conferir autor, título, ano, volume e páginas.** Se algum
não abrir ou divergir, corrigir pelo que a página oficial mostra; se não for possível confirmar,
remover a referência e a citação correspondente. Lista base (os colegas podem acrescentar no PR
deles):

```text
BREIMAN, L. Random forests. Machine Learning, v. 45, n. 1, p. 5-32, 2001. DOI: https://doi.org/10.1023/A:1010933404324.

CARVALHO, T. P. et al. A systematic literature review of machine learning methods applied to predictive maintenance. Computers & Industrial Engineering, v. 137, 106024, 2019. DOI: https://doi.org/10.1016/j.cie.2019.106024.

CHICCO, D.; JURMAN, G. The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. BMC Genomics, v. 21, 6, 2020. DOI: https://doi.org/10.1186/s12864-019-6413-7.

CONFEDERAÇÃO NACIONAL DA INDÚSTRIA (CNI). Desafios para a indústria 4.0 no Brasil. Brasília: CNI, 2016. Disponível em: https://www.portaldaindustria.com.br/publicacoes/2016/8/desafios-para-industria-40-no-brasil/. Acesso em: <data>.

FRIEDMAN, J. H. Greedy function approximation: a gradient boosting machine. The Annals of Statistics, v. 29, n. 5, p. 1189-1232, 2001. DOI: https://doi.org/10.1214/aos/1013203451.

KAGERMANN, H.; WAHLSTER, W.; HELBIG, J. Recommendations for implementing the strategic initiative INDUSTRIE 4.0: final report of the Industrie 4.0 Working Group. Frankfurt am Main: acatech, 2013. Disponível em: https://www.acatech.de/wp-content/uploads/2018/03/Final_report__Industrie_4.0_accessible.pdf. Acesso em: <data>.

KIMBALL, R.; ROSS, M. The data warehouse toolkit: the definitive guide to dimensional modeling. 3. ed. Indianapolis: Wiley, 2013.

LEE, J.; BAGHERI, B.; KAO, H.-A. A cyber-physical systems architecture for Industry 4.0-based manufacturing systems. Manufacturing Letters, v. 3, p. 18-23, 2015. DOI: https://doi.org/10.1016/j.mfglet.2014.12.001.

MANN, H. B.; WHITNEY, D. R. On a test of whether one of two random variables is stochastically larger than the other. The Annals of Mathematical Statistics, v. 18, n. 1, p. 50-60, 1947. DOI: https://doi.org/10.1214/aoms/1177730491.

MATZKA, S. Explainable artificial intelligence for predictive maintenance applications. In: INTERNATIONAL CONFERENCE ON ARTIFICIAL INTELLIGENCE FOR INDUSTRIES (AI4I), 3., 2020, Irvine. Proceedings [...]. IEEE, 2020. p. 69-74. DOI: https://doi.org/10.1109/AI4I49448.2020.00023.

MOBLEY, R. K. An introduction to predictive maintenance. 2. ed. Amsterdam: Butterworth-Heinemann, 2002.

PEDREGOSA, F. et al. Scikit-learn: machine learning in Python. Journal of Machine Learning Research, v. 12, p. 2825-2830, 2011.

SAITO, T.; REHMSMEIER, M. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLOS ONE, v. 10, n. 3, e0118432, 2015. DOI: https://doi.org/10.1371/journal.pone.0118432.

SHEARER, C. The CRISP-DM model: the new blueprint for data mining. Journal of Data Warehousing, v. 5, n. 4, p. 13-22, 2000.

UCI MACHINE LEARNING REPOSITORY. AI4I 2020 predictive maintenance dataset. 2020. DOI: https://doi.org/10.24432/C5HS5C. Acesso em: <data>.

ZONTA, T. et al. Predictive maintenance in the Industry 4.0: a systematic literature review. Computers & Industrial Engineering, v. 150, 106889, 2020. DOI: https://doi.org/10.1016/j.cie.2020.106889.
```

Também incluir as bibliotecas usadas (conferir cada uma):
`HARRIS, C. R. et al. Array programming with NumPy. Nature, v. 585, p. 357-362, 2020.`;
`McKINNEY, W. Data structures for statistical computing in Python. In: PYTHON IN SCIENCE CONFERENCE, 9., 2010, Austin. Proceedings [...]. p. 56-61.`;
`VIRTANEN, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods, v. 17, p. 261-272, 2020.`;
`HUNTER, J. D. Matplotlib: a 2D graphics environment. Computing in Science & Engineering, v. 9, n. 3, p. 90-95, 2007.`;
`WASKOM, M. L. seaborn: statistical data visualization. Journal of Open Source Software, v. 6, n. 60, 3021, 2021.`

Formatação no Markdown: cada referência num parágrafo; título do periódico/livro em **negrito**
(ABNT aceita negrito como destaque). Substituir `<data>` pela data em que você conferiu
(ex.: `23 out. 2026`).

Commits sugeridos:
1. `docs(readme): introdução sobre a Indústria 4.0 (seção 1.1)`
2. `docs(readme): definição do problema (seção 1.2)`
3. `docs(readme): objetivo geral e específicos (seção 1.3)`
4. `docs(readme): referências em ABNT (seção 4)`

PR: `/tbd-pr` — título = título da issue #5, `Closes #5`, revisor `igorSeberino`. Por ser só
texto, pode pedir para pular a execução de notebook (o skill registra o pulo no PR).

Critérios de aceite do T5:
- [ ] Toda citação do texto está em §4 e toda referência de §4 abriu e foi conferida.
- [ ] Os objetivos específicos correspondem ao que os notebooks 01–05 fazem.
- [ ] Nenhum dado numérico sobre a Indústria 4.0 sem fonte (se não tiver fonte, não escreva o número).

---

## T3 — Análise exploratória e testes estatísticos (issue #3 · `feat/3-eda`)

```bash
/tbd-start 3      # assume a issue #3, card em In Progress, branch feat/3-eda
```

### O que você vai mostrar (e defender)

1. O alvo é muito desbalanceado (3,39 %) → acurácia não serve como métrica.
2. Como cada variável se distribui com e sem falha (gráficos + teste de Mann-Whitney, que não
   supõe normalidade, com tamanho de efeito rank-bisserial e correção de Bonferroni).
3. O tipo de produto tem associação estatisticamente significativa com falha, mas de efeito
   pequeno (qui-quadrado + V de Cramér).
4. As correlações entre variáveis (Spearman), inclusive as fortes por construção
   (potência × torque; temperatura do ar × do processo).
5. Validação visual das três regras físicas (HDF, PWF, OSF): os gráficos mostram as falhas
   exatamente nas regiões definidas pelas fronteiras — é o que justifica os atributos de
   engenharia que o Renato usa.

A EDA usa o conjunto completo (10.000 ciclos) porque é descritiva; nenhuma escolha de modelo sai
dela olhando o teste — os atributos físicos foram definidos *a priori* pela documentação (T1) e
os hiperparâmetros por validação cruzada só no treino (T4). Escreva isso no notebook.

**Armadilha:** nenhuma função em `src/` pode começar com `test`/`teste` — o pytest a trata como
teste e quebra. Por isso os nomes são `mann_whitney` e `qui_quadrado`.

### T3.1 `src/manutencao/eda.py`

```python
"""Funções da análise exploratória: resumos, testes estatísticos e gráficos."""

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


def resumo_numerico(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Estatísticas descritivas (contagem, média, desvio, mín, quartis, máx, assimetria)."""
    tabela = df[colunas].describe().T
    tabela["assimetria"] = df[colunas].skew()
    return tabela.round(3)


def taxa_por_categoria(df: pd.DataFrame, coluna: str, alvo: str = "falha") -> pd.DataFrame:
    """Ciclos, falhas e taxa de falha (%) por categoria."""
    g = df.groupby(coluna, observed=True)[alvo].agg(ciclos="count", falhas="sum")
    g["taxa_falha_pct"] = (100 * g["falhas"] / g["ciclos"]).round(2)
    return g.reset_index()


def mann_whitney(df: pd.DataFrame, colunas: list[str], alvo: str = "falha") -> pd.DataFrame:
    """Mann-Whitney U (bilateral) falha=1 vs falha=0 para cada coluna.

    Tamanho de efeito: correlação rank-bisserial ``r = 2·U1/(n1·n0) − 1`` (positivo = valores
    maiores nas falhas). p-valor ajustado por Bonferroni (× número de colunas, teto 1).
    """
    linhas = []
    for col in colunas:
        x1 = df.loc[df[alvo] == 1, col]
        x0 = df.loc[df[alvo] == 0, col]
        res = stats.mannwhitneyu(x1, x0, alternative="two-sided")
        r = 2 * res.statistic / (len(x1) * len(x0)) - 1
        linhas.append(
            {
                "variavel": col,
                "mediana_falha": float(x1.median()),
                "mediana_sem_falha": float(x0.median()),
                "U": float(res.statistic),
                "p_valor": float(res.pvalue),
                "p_bonferroni": min(1.0, float(res.pvalue) * len(colunas)),
                "rank_bisserial": float(r),
            }
        )
    saida = pd.DataFrame(linhas)
    saida["significativo_5pct"] = saida["p_bonferroni"] < 0.05
    return saida.sort_values("rank_bisserial", key=np.abs, ascending=False).reset_index(drop=True)


def cramers_v(tabela: pd.DataFrame) -> float:
    """V de Cramér a partir de uma tabela de contingência (sem correção de continuidade)."""
    chi2 = stats.chi2_contingency(tabela, correction=False)[0]
    n = tabela.to_numpy().sum()
    k = min(tabela.shape) - 1
    return float(math.sqrt(chi2 / (n * k))) if k > 0 else 0.0


def qui_quadrado(df: pd.DataFrame, coluna: str, alvo: str = "falha") -> dict:
    """Qui-quadrado de independência entre ``coluna`` e ``alvo`` + V de Cramér."""
    tabela = pd.crosstab(df[coluna], df[alvo])
    chi2, p, gl, _ = stats.chi2_contingency(tabela, correction=False)
    return {
        "variavel": coluna,
        "qui2": float(chi2),
        "gl": int(gl),
        "p_valor": float(p),
        "v_cramer": cramers_v(tabela),
    }


def grafico_balanceamento(df: pd.DataFrame, alvo: str = "falha") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    contagem = df[alvo].value_counts().sort_index()
    ax.bar(["Sem falha (0)", "Falha (1)"], contagem.values, color=["#4C72B0", "#C44E52"])
    for i, v in enumerate(contagem.values):
        ax.text(i, v, f"{v} ({100 * v / contagem.sum():.2f}%)", ha="center", va="bottom")
    ax.set_title("Balanceamento do alvo")
    ax.set_ylabel("Ciclos")
    return fig


def grafico_distribuicoes(df: pd.DataFrame, colunas: list[str], alvo: str = "falha") -> plt.Figure:
    n = len(colunas)
    ncols = 3
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4 * nrows))
    for ax, col in zip(axes.flat, colunas, strict=False):
        sns.histplot(
            data=df, x=col, hue=alvo, stat="density", common_norm=False, element="step", ax=ax
        )
        ax.set_title(col)
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    fig.suptitle("Distribuição das variáveis por classe (densidade normalizada por classe)")
    fig.tight_layout()
    return fig


def grafico_boxplot_por_tipo(
    df: pd.DataFrame, colunas: list[str], tipo: str = "tipo"
) -> plt.Figure:
    n = len(colunas)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    for ax, col in zip(np.atleast_1d(axes), colunas, strict=True):
        sns.boxplot(data=df, x=tipo, y=col, hue="falha", ax=ax)
        ax.set_title(col)
    fig.tight_layout()
    return fig


def grafico_correlacao(df: pd.DataFrame, colunas: list[str]) -> plt.Figure:
    corr = df[colunas].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlação de Spearman")
    return fig


def grafico_regra_hdf(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=df,
        x="rotacao_rpm",
        y="dif_temperatura_k",
        hue="falha_hdf",
        palette={0: "#BBBBBB", 1: "#C44E52"},
        s=10,
        alpha=0.6,
        ax=ax,
    )
    ax.axhline(8.6, ls="--", c="k")
    ax.axvline(1380, ls="--", c="k")
    ax.set_title("HDF: dif. de temperatura < 8,6 K e rotação < 1380 rpm")
    return fig


def grafico_regra_pwf(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=df,
        x="rotacao_rpm",
        y="torque_nm",
        hue="falha_pwf",
        palette={0: "#BBBBBB", 1: "#C44E52"},
        s=10,
        alpha=0.6,
        ax=ax,
    )
    rpm = np.linspace(df["rotacao_rpm"].min(), df["rotacao_rpm"].max(), 200)
    for p in (3500, 9000):
        ax.plot(rpm, p / (rpm * 2 * np.pi / 60), "k--", lw=1)
        ax.annotate(f"{p} W", (rpm[-1], p / (rpm[-1] * 2 * np.pi / 60)))
    ax.set_ylim(0, df["torque_nm"].max() * 1.05)
    ax.set_title("PWF: potência fora de [3500, 9000] W")
    return fig


def grafico_regra_osf(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=df,
        x="desgaste_ferramenta_min",
        y="torque_nm",
        hue="falha_osf",
        style="tipo",
        palette={0: "#BBBBBB", 1: "#C44E52"},
        s=12,
        alpha=0.6,
        ax=ax,
    )
    d = np.linspace(40, df["desgaste_ferramenta_min"].max(), 200)
    for limite, tipo in ((11000, "L"), (12000, "M"), (13000, "H")):
        ax.plot(d, limite / d, "--", lw=1, label=f"limite {tipo}")
    ax.set_ylim(0, df["torque_nm"].max() * 1.05)
    ax.legend(fontsize=8)
    ax.set_title("OSF: desgaste × torque acima do limite do tipo")
    return fig
```

### T3.2 `tests/test_eda.py`

```python
import numpy as np
import pandas as pd
import pytest

from manutencao.eda import cramers_v, mann_whitney, qui_quadrado, taxa_por_categoria


def _amostras(deslocamento):
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "x": np.r_[rng.normal(0, 1, 500), rng.normal(deslocamento, 1, 500)],
            "falha": [0] * 500 + [1] * 500,
        }
    )


def test_mann_whitney_separacao_total():
    r = mann_whitney(_amostras(10), ["x"]).iloc[0]
    assert r["p_bonferroni"] < 1e-10
    assert r["rank_bisserial"] == pytest.approx(1.0, abs=1e-6)


def test_mann_whitney_sem_diferenca():
    r = mann_whitney(_amostras(0), ["x"]).iloc[0]
    assert abs(r["rank_bisserial"]) < 0.1
    assert not r["significativo_5pct"]


def test_cramers_v_extremos():
    assert cramers_v(pd.DataFrame([[50, 0], [0, 50]])) == pytest.approx(1.0)
    assert cramers_v(pd.DataFrame([[25, 25], [25, 25]])) == pytest.approx(0.0)


def test_taxa_por_tipo_no_dataset(df):
    t = taxa_por_categoria(df, "tipo").set_index("tipo")
    assert t["falhas"].to_dict() == {"L": 235, "M": 83, "H": 21}


def test_qui_quadrado_tipo_falha(df):
    r = qui_quadrado(df, "tipo")
    assert r["gl"] == 2 and 0 < r["v_cramer"] < 1
```

### T3.3 `notebooks/03_analise_exploratoria.ipynb` — célula por célula

| # | Tipo | Conteúdo |
|---|---|---|
| 1 | md | `# 03 · Análise exploratória` · autor Adrian Cesar Gonçalves · fase CRISP-DM: entendimento dos dados · perguntas que a EDA responde (as 5 acima) · badge Colab |
| 2 | code | Célula padrão de ambiente |
| 3 | code | imports: `pandas as pd`, `matplotlib.pyplot as plt`; `from manutencao.config import COLS_NUMERICAS_BRUTAS, COLS_ENGENHARIA, COLS_MODOS`; `from manutencao.preparacao import carregar_preparado`; `from manutencao import eda`; util; `configurar_graficos()` · `df = carregar_preparado()` · `NUMERICAS = COLS_NUMERICAS_BRUTAS + COLS_ENGENHARIA` |
| 4 | md | Nota metodológica (EDA no conjunto completo, por quê) |
| 5 | code | `resumo = eda.resumo_numerico(df, NUMERICAS)` · `salvar_tabela(resumo, "03_resumo_numerico", index=True)` · exibir |
| 6 | md | **1. Balanceamento** |
| 7 | code | `fig = eda.grafico_balanceamento(df)` · `salvar_figura(fig, "03_balanceamento")` |
| 8 | code | Modos de falha: `modos = df[COLS_MODOS].sum().rename("ciclos").to_frame()` + coluna `% das falhas` (dividir por `df["falha"].sum()`) · `salvar_tabela(modos, "03_modos_falha", index=True)` · barras horizontais → `"03_modos_falha"` · comentar: soma > 339 porque há ciclos com mais de um modo; 9 falhas sem modo |
| 9 | md | **2. Distribuições por classe** |
| 10 | code | `fig = eda.grafico_distribuicoes(df, NUMERICAS)` · `salvar_figura(fig, "03_distribuicoes")` |
| 11 | code | `mw = eda.mann_whitney(df, NUMERICAS)` · `salvar_tabela(mw, "03_mann_whitney")` · exibir |
| 12 | md | Interpretar: quais variáveis têm maior |rank-bisserial|, sinal (maior ou menor nas falhas), todas significativas após Bonferroni? Lembrar: com n grande, p pequeno é fácil — o tamanho de efeito é o que importa |
| 13 | md | **3. Tipo de produto** |
| 14 | code | `taxa = eda.taxa_por_categoria(df, "tipo")` · `salvar_tabela(taxa, "03_taxa_falha_por_tipo")` · barras → `"03_taxa_falha_por_tipo"` · `qq = eda.qui_quadrado(df, "tipo")` · `salvar_tabela(pd.DataFrame([qq]), "03_qui_quadrado_tipo")` · exibir |
| 15 | code | `fig = eda.grafico_boxplot_por_tipo(df, ["torque_nm", "rotacao_rpm", "desgaste_ferramenta_min"])` · `salvar_figura(fig, "03_boxplot_por_tipo")` |
| 16 | md | Interpretar: p < 0,05 mas V de Cramér pequeno → associação fraca; tipo importa sobretudo pelo limite de sobrecarga (OSF) |
| 17 | md | **4. Correlações** |
| 18 | code | `fig = eda.grafico_correlacao(df, NUMERICAS + ["falha"])` · `salvar_figura(fig, "03_correlacao_spearman")` |
| 19 | md | Interpretar: pares fortes por construção (potência ~ torque/rotação; temp. ar ~ processo; esforço ~ desgaste) e o que isso implica (multicolinearidade para a regressão logística; irrelevante para árvores) |
| 20 | md | **5. Regras físicas de falha** (fórmulas e fronteiras) |
| 21 | code | `salvar_figura(eda.grafico_regra_hdf(df), "03_regra_hdf")` |
| 22 | code | `salvar_figura(eda.grafico_regra_pwf(df), "03_regra_pwf")` |
| 23 | code | `salvar_figura(eda.grafico_regra_osf(df), "03_regra_osf")` |
| 24 | md | Interpretar: as falhas ficam exatamente além das fronteiras → os atributos `dif_temperatura_k`, `potencia_w` e `esforco_ferramenta_min_nm` separam esses modos; TWF e RNF não aparecem em região própria → não previsíveis por um único ciclo |
| 25 | md | **Conclusões** (6–8 bullets com números das tabelas `03_*`) e **implicações para a modelagem**: métrica PR-AUC; usar atributos físicos; esperar dificuldade em TWF/RNF; tipo como atributo ordinal |

Executar `jupyter nbconvert --to notebook --execute --inplace notebooks/03_analise_exploratoria.ipynb`
e `ruff format notebooks/03_analise_exploratoria.ipynb`.

### T3.4 README — o que escrever

- **§2.4.1 Análise exploratória e testes estatísticos**: estatística descritiva; gráficos de
  distribuição por classe; Mann-Whitney U (MANN; WHITNEY, 1947) com rank-bisserial e Bonferroni —
  por que não teste t (assimetrias, sem suposição de normalidade, classes de tamanhos muito
  diferentes); qui-quadrado + V de Cramér; Spearman (relações monotônicas, robusto a outliers);
  validação visual das regras.
- **§3.2.1 O que a exploração mostrou**: 5–7 achados com números (`03_*.csv`) e figuras
  embutidas: `03_balanceamento.png`, `03_distribuicoes.png`, `03_regra_hdf.png`,
  `03_regra_pwf.png`, `03_regra_osf.png`.

### T3.5 Commits sugeridos

1. `feat(eda): resumo numérico e taxa de falha por categoria`
2. `feat(eda): Mann-Whitney com rank-bisserial e qui-quadrado com V de Cramér`
3. `feat(eda): gráficos de distribuição, correlação e regras físicas`
4. `test(eda): testes estatísticos em dados sintéticos e no dataset`
5. `feat(notebook): 03 análise exploratória executado`
6. `docs(readme): seções 2.4.1 e 3.2.1`

PR: `/tbd-pr` — título = título da issue #3, `Closes #3`, revisor `gabrielcarvallho`.

### T3.6 Critérios de aceite

- [ ] `pytest -q` verde (5 testes do T3 + anteriores).
- [ ] Notebook 03 roda do início ao fim; 9 figuras `03_*.png` (balanceamento, modos_falha,
      distribuicoes, taxa_falha_por_tipo, boxplot_por_tipo, correlacao_spearman, regra_hdf,
      regra_pwf, regra_osf) e 5 tabelas `03_*.csv` (resumo_numerico, modos_falha, mann_whitney,
      taxa_falha_por_tipo, qui_quadrado_tipo).
- [ ] Toda conclusão do notebook e do README cita um número de tabela.

---

## Suas revisões

- **T2 (Gabriel)**: rodar `pytest -q`; abrir `docs/modelo-de-dados.md` no GitHub e ver o Mermaid
  renderizado; conferir que a taxa de falha por tipo do notebook 02 é a mesma do seu notebook 03.
  Comentar pelo menos 1 ponto.
- **T7 (Igor)**: conferir 1.1–1.3, 2.4.1, 3.2.1 e §4 depois da integração, e a sua linha na
  tabela de Contribuições.

## Roteiro de defesa

1. O que é Indústria 4.0 e por que manutenção preditiva é uma aplicação central.
2. Diferença entre manutenção corretiva, preventiva e preditiva.
3. Por que Mann-Whitney e não teste t; o que é o rank-bisserial.
4. Por que p-valor pequeno não basta (n = 10.000) e o papel do tamanho de efeito.
5. O que é o V de Cramér e por que o do tipo é pequeno.
6. O que os três gráficos de regra mostram e o que isso significa para os modelos.
7. Por que a EDA no conjunto completo não contamina a avaliação.
