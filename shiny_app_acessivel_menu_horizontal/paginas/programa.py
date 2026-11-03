import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, botoes_exportar, filtro_selectize, registrar_filtros_cruzados
from exportar import csv_bytes, xlsx_bytes

_NOME_ARQUIVO = "indicadores_programa"
_COLUNAS_TABELA = [
    "Indicador",
    "Periodicidade",
    "Unidade de Medida",
    "Índice de Referência",
    "2027",
    "2028",
    "2029",
    "2030",
]


def panel_ui():
    uos = sorted(dados.programa_programas["uo"].unique())
    nomes = sorted(dados.programa_programas["programa"].unique())
    return ui.nav_panel(
        "Programa",
        ui.div("Programa", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("pr_uo", "Unidade Orçamentária", uos, "Selecione..."),
            filtro_selectize("pr_programa", "Programa", nomes, "Selecione..."),
            botao_limpar_filtros("pr_limpar"),
            class_="filtros",
        ),
        ui.output_ui("pr_conteudo"),
        value="programa",
    )


def register_server(input, output, session):
    registrar_filtros_cruzados(
        input,
        dados.programa_programas,
        [
            ("pr_uo", "uo", "Selecione..."),
            ("pr_programa", "programa", "Selecione..."),
        ],
    )

    @reactive.calc
    def programa_selecionado() -> pd.Series | None:
        if not input.pr_programa():
            return None
        df = dados.programa_programas
        filtrado = df
        if input.pr_uo():
            filtrado = filtrado[filtrado["uo"] == input.pr_uo()]
        filtrado = filtrado[filtrado["programa"] == input.pr_programa()]
        if filtrado.empty:
            return None
        return filtrado.sort_values(["uo", "programa"]).iloc[0]

    @reactive.calc
    def tabela_indicadores() -> pd.DataFrame:
        linha = programa_selecionado()
        if linha is None:
            return dados.programa_indicadores[_COLUNAS_TABELA].iloc[0:0]
        codigo = linha["codigo"]
        df = dados.programa_indicadores
        return df[df["codigo"] == codigo][_COLUNAS_TABELA]

    @reactive.effect
    @reactive.event(input.pr_limpar)
    def _limpar():
        ui.update_selectize("pr_uo", selected="")
        ui.update_selectize("pr_programa", selected="")

    @render.ui
    def pr_conteudo():
        linha = programa_selecionado()
        if linha is None:
            return ui.div("Selecione um programa no filtro", class_="mensagem-selecao")

        ods = linha["ods"]
        if not ods:
            valor_ods = ui.p("—")
        else:
            valor_ods = ui.tags.ul(*[ui.tags.li(o) for o in ods], class_="lista-simples")

        return ui.TagList(
            ui.div(
                ui.div("Programa", class_="rotulo"),
                ui.div(linha["programa"], class_="valor"),
                class_="acao-card acao-card--destaque",
            ),
            ui.div(
                ui.div(
                    ui.div("Unidade Orçamentária", class_="rotulo"),
                    ui.div(linha["uo"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Área Temática", class_="rotulo"),
                    ui.div(linha["area_tematica"], class_="valor"),
                    class_="acao-card",
                ),
                style="display:grid;grid-template-columns:3fr 7fr;gap:1rem;",
            ),
            ui.div(
                ui.div(
                    ui.div("Objetivo", class_="rotulo"),
                    ui.div(linha["objetivo"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Objetivo de Desenvolvimento Sustentável - ODS", class_="rotulo"),
                    ui.div(valor_ods, class_="valor"),
                    class_="acao-card",
                ),
                style="display:grid;grid-template-columns:7fr 3fr;gap:1rem;",
            ),
            ui.h5("Indicadores", class_="mt-3"),
            ui.div(
                botoes_exportar("pr_csv", "pr_xlsx"),
                ui.output_data_frame("pr_tabela"),
                class_="tabela-card",
            ),
        )

    @render.data_frame
    def pr_tabela():
        return render.DataGrid(tabela_indicadores(), width="100%", height="320px", summary=False)

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def pr_csv():
        yield csv_bytes(tabela_indicadores())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def pr_xlsx():
        yield xlsx_bytes(tabela_indicadores())
