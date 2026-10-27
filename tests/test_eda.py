import numpy as np
import pandas as pd
import pytest

from manutencao.eda import cramers_v, mann_whitney, qui_quadrado, taxa_por_categoria


def _amostras(deslocamento):
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "x": np.r_[rng.normal(0, 1, 500), rng.normal(deslocamento, 1, 500)],
            "falha": [0] * 500 + [1] * 500,
        }
    )


def test_mann_whitney_separacao_total():
    r = mann_whitney(_amostras(10), ["x"]).iloc[0]
    assert r["p_bonferroni"] < 1e-10
    assert r["rank_bisserial"] == pytest.approx(1.0, abs=1e-6)


def test_mann_whitney_sem_diferenca():
    r = mann_whitney(_amostras(0), ["x"]).iloc[0]
    assert abs(r["rank_bisserial"]) < 0.1
    assert not r["significativo_5pct"]


def test_cramers_v_extremos():
    assert cramers_v(pd.DataFrame([[50, 0], [0, 50]])) == pytest.approx(1.0)
    assert cramers_v(pd.DataFrame([[25, 25], [25, 25]])) == pytest.approx(0.0)


def test_taxa_por_tipo_no_dataset(df):
    t = taxa_por_categoria(df, "tipo").set_index("tipo")
    assert t["falhas"].to_dict() == {"L": 235, "M": 83, "H": 21}


def test_qui_quadrado_tipo_falha(df):
    r = qui_quadrado(df, "tipo")
    assert r["gl"] == 2 and 0 < r["v_cramer"] < 1
