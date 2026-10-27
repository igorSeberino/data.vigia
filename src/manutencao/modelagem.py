"""Modelagem preditiva: pipelines, validação cruzada, ajuste e avaliação."""

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from manutencao.config import COL_TIPO, ORDEM_TIPO, SEED


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
