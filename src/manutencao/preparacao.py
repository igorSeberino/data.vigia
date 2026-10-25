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
