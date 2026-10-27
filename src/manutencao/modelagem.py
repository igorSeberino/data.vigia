"""Modelagem preditiva: pipelines, validação cruzada, ajuste e avaliação."""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    make_scorer,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
)
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


ESPACOS_BUSCA = {
    "regressao_logistica": {"modelo__C": [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]},
    "arvore_decisao": {
        "modelo__max_depth": [3, 4, 5, 6, 8, 10, 12, None],
        "modelo__min_samples_leaf": [1, 2, 5, 10, 20],
    },
    "random_forest": {
        "modelo__n_estimators": [200, 300, 500],
        "modelo__max_depth": [None, 8, 12, 16],
        "modelo__min_samples_leaf": [1, 2, 4],
        "modelo__max_features": ["sqrt", 0.5, None],
    },
    "gradient_boosting": {
        "modelo__learning_rate": [0.03, 0.05, 0.1, 0.2],
        "modelo__max_iter": [200, 400],
        "modelo__max_leaf_nodes": [15, 31, 63],
        "modelo__min_samples_leaf": [10, 20, 40],
        "modelo__l2_regularization": [0.0, 0.1, 1.0],
    },
}


def ajustar_hiperparametros(
    nome: str,
    atributos: list[str],
    X: pd.DataFrame,
    y: pd.Series,
    n_iter: int = 15,
    seed: int = SEED,
) -> RandomizedSearchCV:
    """Busca aleatória (PR-AUC, 5-fold) no espaço de ``ESPACOS_BUSCA[nome]``; refit no treino todo."""
    espaco = ESPACOS_BUSCA[nome]
    total = int(np.prod([len(v) for v in espaco.values()]))
    busca = RandomizedSearchCV(
        montar_pipeline(nome, atributos, seed),
        espaco,
        n_iter=min(n_iter, total),
        scoring="average_precision",
        cv=validacao(seed),
        random_state=seed,
        n_jobs=-1,
        refit=True,
    )
    return busca.fit(X, y)


def probabilidades_oof(
    pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, seed: int = SEED
) -> np.ndarray:
    """Probabilidade da classe 1 fora da dobra (para escolher limiar sem tocar no teste)."""
    return cross_val_predict(
        clone(pipeline), X, y, cv=validacao(seed), method="predict_proba", n_jobs=-1
    )[:, 1]


def metricas_teste(y: pd.Series, proba: np.ndarray, limiar: float = 0.5) -> dict:
    """Métricas de ranqueamento (sobre ``proba``) e de decisão (com ``proba >= limiar``)."""
    pred = (proba >= limiar).astype(int)
    return {
        "pr_auc": float(average_precision_score(y, proba)),
        "roc_auc": float(roc_auc_score(y, proba)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "precisao": float(precision_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "acuracia_balanceada": float(balanced_accuracy_score(y, pred)),
        "limiar": limiar,
    }
