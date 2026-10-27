"""Funções da análise exploratória: resumos, testes estatísticos e gráficos."""

import pandas as pd


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
