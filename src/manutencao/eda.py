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
