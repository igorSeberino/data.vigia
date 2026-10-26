import math

import pytest

from manutencao.config import ATRIBUTOS_BRUTO, ATRIBUTOS_ENGENHARIA, COLS_VAZAMENTO
from manutencao.preparacao import dividir_treino_teste, separar_x_y


def test_colunas_renomeadas_e_derivadas(df):
    for col in ATRIBUTOS_ENGENHARIA + COLS_VAZAMENTO + ["falha"]:
        assert col in df.columns


def test_tipo_categorico_ordenado(df):
    assert list(df["tipo"].cat.categories) == ["L", "M", "H"]
    assert df["tipo"].cat.ordered
    assert df["tipo"].value_counts().to_dict() == {"L": 6000, "M": 2997, "H": 1003}


def test_atributos_fisicos_da_primeira_linha(df):
    linha = df.loc[df["udi"] == 1].iloc[0]
    assert linha["dif_temperatura_k"] == pytest.approx(10.5)
    assert linha["potencia_w"] == pytest.approx(42.8 * 1551 * 2 * math.pi / 60)
    assert linha["esforco_ferramenta_min_nm"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("regra", "modo", "esperado"),
    [
        (lambda d: (d["dif_temperatura_k"] < 8.6) & (d["rotacao_rpm"] < 1380), "falha_hdf", 115),
        (lambda d: (d["potencia_w"] < 3500) | (d["potencia_w"] > 9000), "falha_pwf", 95),
        (
            lambda d: (
                d["esforco_ferramenta_min_nm"]
                > d["tipo"].map({"L": 11000, "M": 12000, "H": 13000}).astype(float)
            ),
            "falha_osf",
            98,
        ),
    ],
)
def test_atributos_reproduzem_regras_documentadas(df, regra, modo, esperado):
    mascara = regra(df)
    assert int(mascara.sum()) == esperado
    assert (mascara == (df[modo] == 1)).all()


def test_divisao_estratificada_e_deterministica(df):
    treino, teste = dividir_treino_teste(df)
    assert (len(treino), len(teste)) == (8000, 2000)
    assert set(treino["udi"]).isdisjoint(teste["udi"])
    assert abs(treino["falha"].mean() - teste["falha"].mean()) < 0.002
    treino2, _ = dividir_treino_teste(df)
    assert treino["udi"].tolist() == treino2["udi"].tolist()


def test_separar_x_y_recusa_vazamento(df):
    with pytest.raises(ValueError):
        separar_x_y(df, ATRIBUTOS_BRUTO + ["falha_hdf"])
    X, y = separar_x_y(df, ATRIBUTOS_ENGENHARIA)
    assert X.shape == (10000, 9) and y.name == "falha"
