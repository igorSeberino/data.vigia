"""Modelagem preditiva: pipelines, validação cruzada, ajuste e avaliação."""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, make_scorer, matthews_corrcoef, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from manutencao.config import COL_ALVO, COL_TIPO, ORDEM_TIPO, SEED

METRICAS = {
    "pr_auc": "average_precision",
    "roc_auc": "roc_auc",
    "recall": make_scorer(recall_score, zero_division=0),
    "precisao": make_scorer(precision_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
    "mcc": make_scorer(matthews_corrcoef),
    "acuracia_balanceada": "balanced_accuracy",
}


def validacao(seed: int = SEED) -> StratifiedKFold:
    """Validação cruzada única do projeto: 5 dobras estratificadas, embaralhadas com ``seed``."""
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)


def preprocessador(atributos: list[str], escalar: bool) -> ColumnTransformer:
    """Tipo → ordinal (L<M<H); numéricas → padronizadas (só se ``escalar``)."""
    numericas = [c for c in atributos if c != COL_TIPO]
    return ColumnTransformer(
        [
            ("tipo", OrdinalEncoder(categories=[ORDEM_TIPO]), [COL_TIPO]),
            ("num", StandardScaler() if escalar else "passthrough", numericas),
        ]
    )


def modelos_candidatos(seed: int = SEED) -> dict[str, tuple[object, bool]]:
    """Nome → (estimador, precisa_escalar)."""
    return {
        "dummy": (DummyClassifier(strategy="prior"), False),
        "regressao_logistica": (
            LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed),
            True,
        ),
        "arvore_decisao": (
            DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=seed),
            False,
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=300, class_weight="balanced_subsample", n_jobs=-1, random_state=seed
            ),
            False,
        ),
        "gradient_boosting": (
            HistGradientBoostingClassifier(class_weight="balanced", random_state=seed),
            False,
        ),
    }


def montar_pipeline(nome: str, atributos: list[str], seed: int = SEED) -> Pipeline:
    """Pré-processamento + modelo ``nome``: tudo é ajustado dentro de cada dobra (sem vazamento)."""
    estimador, escalar = modelos_candidatos(seed)[nome]
    return Pipeline([("prep", preprocessador(atributos, escalar)), ("modelo", clone(estimador))])


def avaliar_cv(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, seed: int = SEED) -> dict:
    """Validação cruzada estratificada 5-fold; devolve média e desvio de cada métrica."""
    res = cross_validate(pipeline, X, y, cv=validacao(seed), scoring=METRICAS, n_jobs=1)
    saida = {}
    for m in METRICAS:
        saida[f"{m}_media"] = float(np.mean(res[f"test_{m}"]))
        saida[f"{m}_dp"] = float(np.std(res[f"test_{m}"]))
    saida["tempo_ajuste_s"] = float(np.mean(res["fit_time"]))
    return saida


def comparar_modelos(
    treino: pd.DataFrame, conjuntos: dict[str, list[str]], seed: int = SEED
) -> pd.DataFrame:
    """Roda ``avaliar_cv`` para cada modelo × conjunto de atributos."""
    linhas = []
    y = treino[COL_ALVO]
    for nome_conj, atributos in conjuntos.items():
        X = treino[atributos]
        for nome in modelos_candidatos(seed):
            linhas.append(
                {
                    "modelo": nome,
                    "conjunto": nome_conj,
                    **avaliar_cv(montar_pipeline(nome, atributos, seed), X, y, seed),
                }
            )
    return pd.DataFrame(linhas).sort_values("pr_auc_media", ascending=False).reset_index(drop=True)
