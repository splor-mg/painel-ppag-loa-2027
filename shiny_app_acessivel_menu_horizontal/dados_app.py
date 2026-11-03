"""Carrega os CSVs pré-processados (gerados por ../gerar_dados_shiny.py) uma
única vez, na importação do módulo (cache de processo).
"""

import json
from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).resolve().parent / "data"


def _ler(nome: str) -> pd.DataFrame:
    return pd.read_csv(PASTA_DADOS / nome)


cards = _ler("cards.csv").iloc[0].to_dict()
visao_geral = _ler("visao_geral.csv")

despesa_fiscal_detalhe = _ler("despesa_fiscal_detalhe.csv")

acao_orcamentaria = _ler("acao_orcamentaria.csv")

programa_programas = _ler("programa_programas.csv")
programa_programas["ods"] = programa_programas["ods"].fillna("").apply(
    lambda v: v.split(";") if v else []
)
programa_indicadores = _ler("programa_indicadores.csv")

receita_fiscal = _ler("receita_fiscal.csv")
despesa_orgao = _ler("despesa_orgao.csv")

loa_investimentos_uo = _ler("loa_investimentos_uo.csv")["uo"].tolist()
loa_investimentos_receita = _ler("loa_investimentos_receita.csv")
loa_investimentos_despesa = _ler("loa_investimentos_despesa.csv")

qdd = _ler("qdd.csv")

regionalizacao = _ler("regionalizacao.csv")
regionalizacao["municipio_ibge"] = regionalizacao["municipio_ibge"].astype(str)

glossario = _ler("glossario.csv").to_dict(orient="records")

with open(PASTA_DADOS / "mg_municipios.geojson", encoding="utf-8") as f:
    mg_municipios_geojson = json.load(f)
