import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, filtro_selectize, grafico_acessivel, registrar_filtros_cruzados
from graficos import grafico_por_ano
from utils import formatar_moeda

_ANOS = [2027, 2028, 2029, 2030]


def panel_ui():
    uos = sorted(dados.acao_orcamentaria["uo"].unique())
    acoes = sorted(dados.acao_orcamentaria["acao"].unique())
    return ui.nav_panel(
        "Ação Orçamentária",
        ui.div("Ação Orçamentária", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("ac_uo", "Unidade Orçamentária", uos, "Selecione..."),
            filtro_selectize("ac_acao", "Ação Orçamentária", acoes, "Selecione..."),
            botao_limpar_filtros("ac_limpar"),
            class_="filtros",
        ),
        ui.output_ui("ac_conteudo"),
        value="acao_orcamentaria",
    )


def register_server(input, output, session):
    registrar_filtros_cruzados(
        input,
        dados.acao_orcamentaria,
        [
            ("ac_uo", "uo", "Selecione..."),
            ("ac_acao", "acao", "Selecione..."),
        ],
    )

    @reactive.calc
    def linha_selecionada() -> pd.Series | None:
        if not input.ac_acao():
            return None
        df = dados.acao_orcamentaria
        filtrado = df
        if input.ac_uo():
            filtrado = filtrado[filtrado["uo"] == input.ac_uo()]
        filtrado = filtrado[filtrado["acao"] == input.ac_acao()]
        if filtrado.empty:
            return None
        return filtrado.sort_values(["uo", "acao"]).iloc[0]

    @reactive.effect
    @reactive.event(input.ac_limpar)
    def _limpar():
        ui.update_selectize("ac_uo", selected="")
        ui.update_selectize("ac_acao", selected="")

    @render.ui
    def ac_conteudo():
        linha = linha_selecionada()
        if linha is None:
            return ui.div(
                "Selecione uma ação orçamentária no filtro",
                class_="mensagem-selecao",
            )

        valores_fisica = [float(linha[f"fisica_{ano}"]) for ano in _ANOS]
        fig_fisica = grafico_por_ano(
            _ANOS, valores_fisica, "Previsão Física", lambda v: f"{v:,.0f}".replace(",", ".")
        )
        valores_orcamentaria = [float(linha[f"orcamentaria_{ano}"]) for ano in _ANOS]
        fig_orcamentaria = grafico_por_ano(_ANOS, valores_orcamentaria, "Previsão Orçamentária", formatar_moeda)
        tabela_fisica = pd.DataFrame(
            {"Ano": _ANOS, "Previsão Física": [f"{v:,.0f}".replace(",", ".") for v in valores_fisica]}
        )
        tabela_orcamentaria = pd.DataFrame(
            {"Ano": _ANOS, "Previsão Orçamentária": [formatar_moeda(v) for v in valores_orcamentaria]}
        )

        return ui.TagList(
            ui.div(
                ui.div("Ação Orçamentária", class_="rotulo"),
                ui.div(linha["acao"], class_="valor"),
                class_="acao-card acao-card--destaque",
            ),
            ui.div(
                ui.div(
                    ui.div("Unidade Orçamentária", class_="rotulo"),
                    ui.div(linha["uo"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Programa", class_="rotulo"),
                    ui.div(linha["programa"], class_="valor"),
                    class_="acao-card",
                ),
                style="display:grid;grid-template-columns:3fr 7fr;gap:1rem;",
            ),
            ui.div(
                ui.div(
                    ui.div("Finalidade da Ação", class_="rotulo"),
                    ui.div(linha["finalidade"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Público-Alvo", class_="rotulo"),
                    ui.div(linha["publico_alvo"], class_="valor"),
                    class_="acao-card",
                ),
                style="display:grid;grid-template-columns:7fr 3fr;gap:1rem;",
            ),
            ui.div(
                ui.div(
                    ui.div("Identificador de Ação Governamental (IAG)", class_="rotulo"),
                    ui.div(linha["iag"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Produto", class_="rotulo"),
                    ui.div(linha["produto"], class_="valor"),
                    class_="acao-card",
                ),
                ui.div(
                    ui.div("Unidade de Medida (Produto)", class_="rotulo"),
                    ui.div(linha["unidade_medida"], class_="valor"),
                    class_="acao-card",
                ),
                style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;",
            ),
            ui.div(
                ui.div(
                    grafico_acessivel(fig_fisica, tabela_fisica, id="ac_grafico_fisica", titulo="Previsão Física"),
                    class_="grafico-card",
                ),
                ui.div(
                    grafico_acessivel(
                        fig_orcamentaria, tabela_orcamentaria, id="ac_grafico_orcamentaria", titulo="Previsão Orçamentária"
                    ),
                    class_="grafico-card",
                ),
                class_="grade-graficos",
            ),
        )
