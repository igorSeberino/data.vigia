"""Caminhos, constantes e nomes de colunas compartilhados por todo o projeto."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_FIGURAS = RAIZ / "reports" / "figures"
DIR_TABELAS = RAIZ / "reports" / "tables"

CAMINHO_CSV = DIR_RAW / "ai4i2020.csv"
CAMINHO_DB = DIR_PROCESSED / "industria40.db"

URL_ZIP = (
    "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
)
SHA256_CSV = "dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e"

SEED = 42

MAPA_COLUNAS = {
    "UDI": "udi",
    "Product ID": "id_produto",
    "Type": "tipo",
    "Air temperature [K]": "temp_ar_k",
    "Process temperature [K]": "temp_processo_k",
    "Rotational speed [rpm]": "rotacao_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "desgaste_ferramenta_min",
    "Machine failure": "falha",
    "TWF": "falha_twf",
    "HDF": "falha_hdf",
    "PWF": "falha_pwf",
    "OSF": "falha_osf",
    "RNF": "falha_rnf",
}

COL_ALVO = "falha"
COL_TIPO = "tipo"
ORDEM_TIPO = ["L", "M", "H"]
COLS_MODOS = ["falha_twf", "falha_hdf", "falha_pwf", "falha_osf", "falha_rnf"]
COLS_NUMERICAS_BRUTAS = [
    "temp_ar_k",
    "temp_processo_k",
    "rotacao_rpm",
    "torque_nm",
    "desgaste_ferramenta_min",
]
COLS_ENGENHARIA = ["dif_temperatura_k", "potencia_w", "esforco_ferramenta_min_nm"]
COLS_VAZAMENTO = ["udi", "id_produto", *COLS_MODOS]

ATRIBUTOS_BRUTO = [COL_TIPO, *COLS_NUMERICAS_BRUTAS]
ATRIBUTOS_ENGENHARIA = [*ATRIBUTOS_BRUTO, *COLS_ENGENHARIA]

MODOS_FALHA = {
    "TWF": ("falha_twf", "Desgaste da ferramenta"),
    "HDF": ("falha_hdf", "Falha de dissipação de calor"),
    "PWF": ("falha_pwf", "Falha de potência"),
    "OSF": ("falha_osf", "Sobrecarga (overstrain)"),
    "RNF": ("falha_rnf", "Falha aleatória"),
}
