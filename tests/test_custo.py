import numpy as np
import pytest

from manutencao.custo import (
    Custos,
    curva_custo_limiar,
    custo_total,
    estrategia_corretiva,
    estrategia_preditiva,
    estrategia_preventiva,
    melhor_limiar,
    melhor_limite_desgaste,
)

Y = np.array([0, 0, 0, 1, 1])
C = Custos(intervencao=100, falha=1000)


def test_custo_total_a_mao():
    r = custo_total(Y, np.array([0, 1, 0, 1, 0]), C)
    assert (r["vp"], r["fp"], r["fn"], r["vn"]) == (1, 1, 1, 2)
    assert r["custo_total"] == 2 * 100 + 1 * 1000
    assert r["custo_por_1000_ciclos"] == pytest.approx(1000 * 1200 / 5)


def test_corretiva_paga_todas_as_falhas():
    assert estrategia_corretiva(Y, C)["custo_total"] == 2000


def test_preventiva_por_desgaste():
    desgaste = np.array([10, 20, 210, 220, 50])
    r = estrategia_preventiva(desgaste, Y, 200, C)
    assert (r["vp"], r["fp"], r["fn"]) == (1, 1, 1)


def test_melhor_limite_desgaste():
    desgaste = np.array([10, 20, 30, 220, 230])
    assert melhor_limite_desgaste(desgaste, Y, C, grade=range(0, 260, 5)) == 220


def test_limiar_otimo_separa_classes():
    proba = np.array([0.05, 0.1, 0.2, 0.7, 0.9])
    curva = curva_custo_limiar(Y, proba, C)
    t = melhor_limiar(curva)
    assert 0.2 < t <= 0.7
    assert estrategia_preditiva(proba, Y, t, C)["custo_total"] == 200
