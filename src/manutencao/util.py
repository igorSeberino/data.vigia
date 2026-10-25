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
