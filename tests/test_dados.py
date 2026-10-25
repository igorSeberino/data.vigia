from manutencao.config import CAMINHO_CSV, SHA256_CSV
from manutencao.dados import inconsistencias_rotulo, sha256_arquivo, validar


def test_csv_versionado_e_o_arquivo_oficial():
    assert sha256_arquivo(CAMINHO_CSV) == SHA256_CSV


def test_cabecalho_sem_bom(df_bruto):
    assert df_bruto.columns[0] == "UDI"


def test_volume(df_bruto):
    assert df_bruto.shape == (10000, 14)


def test_todas_as_validacoes_passam(df_bruto):
    tabela = validar(df_bruto)
    assert tabela["ok"].all(), tabela[~tabela["ok"]]


def test_inconsistencias_de_rotulo(df_bruto):
    inc = inconsistencias_rotulo(df_bruto)
    contagem = inc["inconsistencia"].value_counts().to_dict()
    assert contagem == {"modo sem falha": 18, "falha sem modo": 9}
