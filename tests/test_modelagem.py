import numpy as np
import pandas as pd
import pytest

from manutencao.config import ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA
from manutencao.modelagem import (
    avaliar_cv,
    metricas_teste,
    modelos_candidatos,
    montar_pipeline,
    recall_por_modo,
)
from manutencao.preparacao import dividir_treino_teste


@pytest.fixture(scope="module")
def treino(df):
    return dividir_treino_teste(df)[0]


def test_candidatos():
    assert list(modelos_candidatos()) == [
        "dummy",
        "regressao_logistica",
        "arvore_decisao",
        "random_forest",
        "gradient_boosting",
    ]


@pytest.mark.parametrize("atributos", [ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA])
def test_pipeline_ajusta_e_preve(treino, atributos):
    pipe = montar_pipeline("arvore_decisao", atributos).fit(treino[atributos], treino["falha"])
    proba = pipe.predict_proba(treino[atributos])[:, 1]
    assert proba.shape == (len(treino),) and ((proba >= 0) & (proba <= 1)).all()


def test_dummy_tem_pr_auc_igual_a_prevalencia(treino):
    r = avaliar_cv(
        montar_pipeline("dummy", ATRIBUTOS_BRUTO), treino[ATRIBUTOS_BRUTO], treino["falha"]
    )
    assert r["pr_auc_media"] == pytest.approx(treino["falha"].mean(), abs=0.005)
    assert r["roc_auc_media"] == pytest.approx(0.5)


def test_engenharia_supera_bruto_na_arvore(treino):
    y = treino["falha"]
    bruto = avaliar_cv(
        montar_pipeline("arvore_decisao", ATRIBUTOS_BRUTO), treino[ATRIBUTOS_BRUTO], y
    )
    eng = avaliar_cv(
        montar_pipeline("arvore_decisao", ATRIBUTOS_ENGENHARIA), treino[ATRIBUTOS_ENGENHARIA], y
    )
    assert eng["pr_auc_media"] > bruto["pr_auc_media"]


def test_metricas_teste_classificador_perfeito():
    y = pd.Series([0, 0, 1, 1])
    m = metricas_teste(y, np.array([0.1, 0.2, 0.8, 0.9]))
    assert m["pr_auc"] == 1 and m["recall"] == 1 and m["mcc"] == pytest.approx(1)


def test_recall_por_modo(df):
    _, teste = dividir_treino_teste(df)
    pred = teste["falha"].to_numpy()
    t = recall_por_modo(teste, pred).set_index("modo")
    assert t.loc["HDF", "recall"] == 1.0
    assert t.loc["SEM MODO", "ciclos_no_teste"] >= 0
