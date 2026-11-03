"""Gera shiny_app_acessivel/data/*.csv a partir dos módulos dados_*.py / etl/*.py.

Mesma lógica e premissas do site estático original (ver docs/premissas.md)
— só muda o formato de saída (CSV, lido pelo app Shiny via pandas) e o
fato de rodar como pré-processamento (o app Shinylive roda no navegador
via Pyodide; ler as bases .xlsx/.txt brutas ali seria lento e exigiria
bundlar arquivos grandes, então o build prepara tudo antes).

Rodar sempre que os dados ou a lógica de algum dados_*.py mudarem, antes de
publicar a branch gh-pages. Se houver mais de uma variante do painel
(ex. shiny_app_acessivel_menu_horizontal/), copiar a pasta data/ gerada
aqui para a(s) outra(s) também -- mesmo padrão já usado para criá-las.
"""

import shutil
from pathlib import Path

import pandas as pd

from dados_acao_orcamentaria import ANOS, construir_base_enriquecida as construir_base_acao
from dados_despesa_fiscal import COLUNA_VALOR as COLUNA_VALOR_DESPESA_FISCAL
from dados_despesa_orgao import COLUNA_VALOR as COLUNA_VALOR_DESPESA_ORGAO
from dados_despesa_orgao import construir_base_enriquecida as construir_base_despesa_orgao
from dados_glossario import construir_lista_termos
from dados_loa_investimentos import (
    construir_base_despesa as construir_base_investimentos_despesa,
)
from dados_loa_investimentos import (
    construir_base_receita as construir_base_investimentos_receita,
)
from dados_loa_investimentos import construir_lista_uo as construir_lista_uo_investimentos
from dados_programa import construir_base_enriquecida as construir_base_programa
from dados_programa import construir_tabela_indicadores
from dados_qdd import COLUNA_VALOR as COLUNA_VALOR_QDD
from dados_qdd import construir_base_enriquecida as construir_base_qdd
from dados_receita_fiscal import COLUNA_VALOR as COLUNA_VALOR_RECEITA
from dados_receita_fiscal import construir_base_enriquecida as construir_base_receita_fiscal
from dados_regionalizacao import construir_base_enriquecida as construir_base_regionalizacao
from dados_visao_geral import COLUNA_IAG, COLUNA_PREVISAO_2027
from etl.despesa import (
    carregar_auxiliar_funcao,
    carregar_auxiliar_grupo_despesa,
    carregar_auxiliar_poder,
)
from etl.limpeza_inicial import carregar_acoes, carregar_programas
from etl.orcamento import carregar_qdd_fiscal, carregar_qdd_investimento

PASTA_SAIDA = Path(__file__).resolve().parent / "shiny_app_acessivel" / "data"
COLUNA_PROGRAMA = "Código do Programa"


def gerar() -> None:
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    _gerar_cards()
    _gerar_visao_geral()
    _gerar_despesa_fiscal()
    _gerar_acao_orcamentaria()
    _gerar_programa()
    _gerar_receita_fiscal()
    _gerar_despesa_orgao()
    _gerar_loa_investimentos()
    _gerar_qdd()
    _gerar_regionalizacao()
    _gerar_glossario()

    destino_geojson = PASTA_SAIDA / "mg_municipios.geojson"
    shutil.copyfile(
        Path(__file__).resolve().parent / "assets" / "mg_municipios.geojson", destino_geojson
    )
    print(f"Copiado: {destino_geojson}")


def _salvar(df: pd.DataFrame, nome: str) -> None:
    caminho = PASTA_SAIDA / nome
    df.to_csv(caminho, index=False)
    print(f"Gerado: {caminho} ({len(df)} linhas)")


def _gerar_cards() -> None:
    total_fiscal = carregar_qdd_fiscal()[COLUNA_VALOR_DESPESA_FISCAL].sum()
    total_investimento = carregar_qdd_investimento()["VALOR (R$)"].sum()
    qtd_programas = carregar_programas()[COLUNA_PROGRAMA].nunique()
    acoes = carregar_acoes()
    df = pd.DataFrame(
        [
            {
                "total_fiscal": float(total_fiscal),
                "total_investimento": float(total_investimento),
                "qtd_programas": int(qtd_programas),
                "qtd_acoes": int(len(acoes)),
                "qtd_projetos_estrategicos": int(len(acoes[acoes[COLUNA_IAG] == "1"])),
            }
        ]
    )
    _salvar(df, "cards.csv")


def _gerar_visao_geral() -> None:
    acoes = carregar_acoes().copy()
    acoes[COLUNA_PREVISAO_2027] = acoes[COLUNA_PREVISAO_2027].astype(float)
    acoes["Área Temática"] = acoes["Área Temática"].str.upper()
    df = acoes.rename(
        columns={
            "Área Temática": "area_tematica",
            "Setor de Governo": "setor_governo",
            COLUNA_PREVISAO_2027: "valor",
        }
    )[["area_tematica", "setor_governo", "valor"]]
    _salvar(df, "visao_geral.csv")


def _gerar_despesa_fiscal() -> None:
    despesa = carregar_qdd_fiscal()

    # Base com as 3 dimensões (poder, grupo, função) na mesma linha -- usada
    # pelo painel Shiny tanto para montar os 3 gráficos quanto para o
    # crossfilter entre eles (clicar numa barra de uma dimensão filtra as
    # outras duas, recalculadas a partir do mesmo subconjunto de linhas).
    detalhe = (
        despesa.merge(carregar_auxiliar_poder(), left_on="COD_UO", right_on="uo_cod")
        .merge(carregar_auxiliar_grupo_despesa(), left_on="GRUPO_DESPESA", right_on="grupo_despesa_cod")
        .merge(carregar_auxiliar_funcao(), left_on="FUNCAO", right_on="funcao_cod")
    )
    _salvar(
        detalhe.rename(columns={COLUNA_VALOR_DESPESA_FISCAL: "valor"})[
            ["uo_poder", "grupo_despesa_descricao", "funcao_descricao", "valor"]
        ],
        "despesa_fiscal_detalhe.csv",
    )


def _gerar_acao_orcamentaria() -> None:
    base = construir_base_acao()
    colunas = {
        "uo_label": "uo",
        "acao_label": "acao",
        "programa_label": "programa",
        "Finalidade da Ação": "finalidade",
        "Público-Alvo": "publico_alvo",
        "Identificador de Ação Governamental (IAG)": "iag",
        "Produto": "produto",
        "Unidade de Medida do Produto": "unidade_medida",
    }
    exportado = base.rename(columns=colunas)[list(colunas.values())].copy()
    for ano in ANOS:
        exportado[f"fisica_{ano}"] = base[f"Previsão Física {ano}"].astype(float)
        exportado[f"orcamentaria_{ano}"] = base[f"Previsão Orçamentária {ano}"].astype(float)
    _salvar(exportado, "acao_orcamentaria.csv")


def _gerar_programa() -> None:
    base = construir_base_programa()

    programas = []
    for codigo, grupo in base.groupby(COLUNA_PROGRAMA):
        primeira = grupo.iloc[0]
        ods = sorted(
            t for t in grupo["Título do Objetivo de Desenvolvimento Sustentável"].dropna().unique() if t
        )
        programas.append(
            {
                "codigo": codigo,
                "programa": primeira["programa_label"],
                "uo": primeira["uo_label"],
                "area_tematica": primeira["Área Temática"],
                "objetivo": primeira["Objetivo"],
                "ods": ";".join(ods),
            }
        )
    _salvar(pd.DataFrame(programas), "programa_programas.csv")

    indicadores = []
    for programa in programas:
        tabela = construir_tabela_indicadores(programa["codigo"]).copy()
        tabela.insert(0, "codigo", programa["codigo"])
        indicadores.append(tabela)
    _salvar(pd.concat(indicadores, ignore_index=True), "programa_indicadores.csv")


def _gerar_receita_fiscal() -> None:
    df = construir_base_receita_fiscal().rename(columns={COLUNA_VALOR_RECEITA: "valor"})
    _salvar(df, "receita_fiscal.csv")


def _gerar_despesa_orgao() -> None:
    df = construir_base_despesa_orgao().rename(columns={COLUNA_VALOR_DESPESA_ORGAO: "valor"})
    _salvar(df, "despesa_orgao.csv")


def _gerar_loa_investimentos() -> None:
    uo_opcoes = construir_lista_uo_investimentos()
    _salvar(pd.DataFrame({"uo": uo_opcoes}), "loa_investimentos_uo.csv")
    _salvar(construir_base_investimentos_receita(), "loa_investimentos_receita.csv")
    _salvar(construir_base_investimentos_despesa(), "loa_investimentos_despesa.csv")


def _gerar_qdd() -> None:
    df = construir_base_qdd().rename(columns={COLUNA_VALOR_QDD: "valor"})
    _salvar(df, "qdd.csv")


def _gerar_regionalizacao() -> None:
    df = construir_base_regionalizacao().rename(
        columns={
            "Previsão Física 2027": "fisica",
            "Previsão Orçamentária 2027": "valor",
        }
    )
    _salvar(df, "regionalizacao.csv")


def _gerar_glossario() -> None:
    _salvar(pd.DataFrame(construir_lista_termos()), "glossario.csv")


if __name__ == "__main__":
    gerar()
