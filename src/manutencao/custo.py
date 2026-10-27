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
