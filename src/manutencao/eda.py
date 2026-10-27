"""Funções da análise exploratória: resumos, testes estatísticos e gráficos."""

import math

import numpy as np
import pandas as pd
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
