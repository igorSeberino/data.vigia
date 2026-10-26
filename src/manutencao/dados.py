"""Coleta e validação do dataset AI4I 2020 (UCI, id 601)."""

import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from manutencao.config import CAMINHO_CSV, COLS_MODOS, MAPA_COLUNAS, SHA256_CSV, URL_ZIP


def sha256_arquivo(caminho: Path) -> str:
    """Calcula o SHA-256 de um arquivo."""
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def baixar_csv(destino: Path = CAMINHO_CSV, url: str = URL_ZIP) -> Path:
    """Baixa o zip oficial da UCI, extrai ``ai4i2020.csv`` em ``destino`` e confere o SHA-256."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as resposta:
        conteudo = resposta.read()
    with zipfile.ZipFile(io.BytesIO(conteudo)) as zf:
        destino.write_bytes(zf.read("ai4i2020.csv"))
    obtido = sha256_arquivo(destino)
    if obtido != SHA256_CSV:
        raise ValueError(f"SHA-256 inesperado para {destino}: {obtido}")
    return destino


def carregar_bruto(caminho: Path = CAMINHO_CSV, baixar_se_ausente: bool = True) -> pd.DataFrame:
    """Lê o CSV original com os nomes de coluna da fonte.

    O arquivo tem BOM UTF-8 no cabeçalho, por isso ``encoding="utf-8-sig"``.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        if not baixar_se_ausente:
            raise FileNotFoundError(caminho)
        baixar_csv(caminho)
    return pd.read_csv(caminho, encoding="utf-8-sig")


def validar(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Executa as verificações de qualidade e devolve uma tabela ``verificacao, esperado, obtido, ok``."""
    df = df_bruto.rename(columns=MAPA_COLUNAS)
    flags = ["falha", *COLS_MODOS]
    checagens = [
        ("colunas esperadas", sorted(MAPA_COLUNAS.values()), sorted(df.columns)),
        ("quantidade de linhas", 10000, len(df)),
        ("valores ausentes", 0, int(df.isna().sum().sum())),
        ("linhas duplicadas", 0, int(df.duplicated().sum())),
        ("udi único", True, bool(df["udi"].is_unique)),
        ("id_produto único", True, bool(df["id_produto"].is_unique)),
        ("tipo em {L, M, H}", True, bool(df["tipo"].isin(["L", "M", "H"]).all())),
        (
            "1ª letra do id_produto = tipo",
            True,
            bool((df["id_produto"].str[0] == df["tipo"]).all()),
        ),
        (
            "temperaturas entre 290 e 320 K",
            True,
            bool(df[["temp_ar_k", "temp_processo_k"]].stack().between(290, 320).all()),
        ),
        ("temp_processo > temp_ar", True, bool((df["temp_processo_k"] > df["temp_ar_k"]).all())),
        ("rotação > 0", True, bool((df["rotacao_rpm"] > 0).all())),
        ("torque >= 0", True, bool((df["torque_nm"] >= 0).all())),
        ("desgaste >= 0", True, bool((df["desgaste_ferramenta_min"] >= 0).all())),
        ("flags binárias (0/1)", True, bool(df[flags].isin([0, 1]).all().all())),
    ]
    tabela = pd.DataFrame(checagens, columns=["verificacao", "esperado", "obtido"])
    tabela["ok"] = [
        str(e) == str(o) for e, o in zip(tabela["esperado"], tabela["obtido"], strict=True)
    ]
    tabela[["esperado", "obtido"]] = tabela[["esperado", "obtido"]].astype(str)
    return tabela


def inconsistencias_rotulo(df: pd.DataFrame) -> pd.DataFrame:
    """Linhas cujo rótulo geral não bate com os modos de falha.

    Aceita o DataFrame bruto ou o preparado. Devolve as colunas originais mais ``inconsistencia``
    com os valores ``"falha sem modo"`` ou ``"modo sem falha"``.
    """
    d = df.rename(columns=MAPA_COLUNAS)
    algum_modo = d[COLS_MODOS].sum(axis=1) > 0
    sem_modo = (d["falha"] == 1) & ~algum_modo
    sem_falha = (d["falha"] == 0) & algum_modo
    saida = d[sem_modo | sem_falha].copy()
    saida["inconsistencia"] = "falha sem modo"
    saida.loc[sem_falha[sem_modo | sem_falha], "inconsistencia"] = "modo sem falha"
    return saida
