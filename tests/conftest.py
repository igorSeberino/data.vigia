import pytest

from manutencao.dados import carregar_bruto
from manutencao.preparacao import preparar


@pytest.fixture(scope="session")
def df_bruto():
    return carregar_bruto(baixar_se_ausente=False)


@pytest.fixture(scope="session")
def df(df_bruto):
    return preparar(df_bruto)
