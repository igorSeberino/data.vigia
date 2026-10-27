import pytest

from manutencao.modelo_dados import (
    CONSULTAS,
    carregar,
    conectar,
    consultar,
    criar_schema,
    executar_consultas,
    verificar_integridade,
)


@pytest.fixture(scope="module")
def conn(df):
    c = conectar(":memory:")
    criar_schema(c)
    carregar(c, df)
    yield c
    c.close()


def test_contagem_das_tabelas(conn):
    contagens = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in [
            "dim_tipo_produto",
            "dim_faixa_desgaste",
            "dim_modo_falha",
            "fato_ciclo",
            "ponte_ciclo_modo",
        ]
    }
    assert contagens == {
        "dim_tipo_produto": 3,
        "dim_faixa_desgaste": 5,
        "dim_modo_falha": 5,
        "fato_ciclo": 10000,
        "ponte_ciclo_modo": 373,
    }


def test_integridade(conn, df):
    tabela = verificar_integridade(conn, df)
    assert tabela["ok"].all(), tabela[~tabela["ok"]]


def test_taxa_falha_por_tipo(conn):
    t = consultar(conn, CONSULTAS["taxa_falha_por_tipo"]).set_index("tipo")
    assert t["falhas"].to_dict() == {"L": 235, "M": 83, "H": 21}
    assert t.loc["L", "taxa_falha_pct"] == pytest.approx(3.92)


def test_falhas_por_faixa_de_desgaste(conn):
    t = consultar(conn, CONSULTAS["taxa_falha_por_faixa_desgaste"])
    assert t["ciclos"].tolist() == [2349, 2271, 2290, 2289, 801]
    assert t["falhas"].tolist() == [52, 51, 52, 61, 123]


def test_inconsistencias(conn):
    t = consultar(conn, CONSULTAS["inconsistencias_rotulo"]).set_index("inconsistencia")
    assert t["ciclos"].to_dict() == {"falha sem modo": 9, "modo sem falha": 18}


def test_esforco_acima_do_limite_bate_com_osf(conn):
    t = consultar(conn, CONSULTAS["esforco_acima_do_limite"])
    assert (t["ciclos_acima"] == t["ciclos_com_osf"]).all()
    assert int(t["ciclos_acima"].sum()) == 98


def test_todas_as_consultas_rodam(conn):
    resultados = executar_consultas(conn)
    assert set(resultados) == set(CONSULTAS)
    assert all(len(r) > 0 for r in resultados.values())
