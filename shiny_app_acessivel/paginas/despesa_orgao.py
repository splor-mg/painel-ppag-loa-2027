import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, card_kpi, filtro_selectize, grafico_acessivel, selecao_grafico
from graficos import grafico_absoluto_vertical
from utils import formatar_bilhoes, formatar_moeda


def panel_ui():
    uos = sorted(dados.despesa_orgao["uo_label"].unique())
    return ui.nav_panel(
        "Despesa por Órgão",
        ui.div("Despesa por Órgão", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("do_uo", "Unidade Orçamentária", uos, multiplo=True),
            botao_limpar_filtros("do_limpar"),
            class_="filtros",
        ),
        ui.div(ui.output_ui("do_card"), class_="linha-cartao-unico"),
        ui.div(ui.output_ui("do_grafico"), class_="grafico-card"),
        ui.div(
            ui.div(
                ui.h5("Despesa por Ação Orçamentária", class_="lista-cartao-titulo"),
                ui.output_ui("do_lista_acao"),
                class_="lista-cartao",
            ),
            ui.div(
                ui.h5("Despesa por Fonte de Recursos", class_="lista-cartao-titulo"),
                ui.output_ui("do_lista_fonte"),
                class_="lista-cartao",
            ),
            class_="linha-cartoes",
        ),
        value="despesa_orgao",
    )


def _lista_cartao(itens: list[tuple[str, str]]):
    linhas = [
        ui.div(ui.span(label, class_="label"), ui.span(valor, class_="valor"), class_="lista-cartao-item")
        for label, valor in itens
    ]
    return ui.div(*linhas, class_="lista-cartao-corpo")


def register_server(input, output, session):
    @reactive.calc
    def base_filtrada() -> pd.DataFrame:
        df = dados.despesa_orgao
        if input.do_uo():
            df = df[df["uo_label"].isin(input.do_uo())]
        return df

    @reactive.calc
    def base_com_selecao() -> pd.DataFrame:
        # Clique numa barra do gráfico "Despesa por Grupo" filtra o card e as
        # listas, mas não o próprio gráfico (que continua mostrando todos os
        # grupos, para o usuário poder trocar de seleção).
        df = base_filtrada()
        grupo = selecao_grafico(input, "do_grafico")
        if grupo:
            df = df[df["grupo_despesa_descricao"] == grupo]
        return df

    @reactive.effect
    @reactive.event(input.do_limpar)
    def _limpar():
        ui.update_selectize("do_uo", selected=[])

    @render.ui
    def do_card():
        total = base_com_selecao()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def do_grafico():
        df = base_filtrada()
        fig = grafico_absoluto_vertical(df, "grupo_despesa_descricao", "valor", "Despesa por Grupo")
        agrupado = df.groupby("grupo_despesa_descricao", as_index=False)["valor"].sum()
        tabela = agrupado.rename(columns={"grupo_despesa_descricao": "Grupo de Despesa"})
        tabela["Valor (R$)"] = agrupado["valor"].map(formatar_moeda)
        tabela = tabela[["Grupo de Despesa", "Valor (R$)"]]
        return grafico_acessivel(fig, tabela, id="do_grafico", titulo="Despesa por Grupo", selecionavel=True)

    @render.ui
    def do_lista_acao():
        agrupado = base_com_selecao().groupby("acao_label")["valor"].sum().sort_values(ascending=False)
        itens = [(label, formatar_moeda(valor)) for label, valor in agrupado.items()]
        return _lista_cartao(itens)

    @render.ui
    def do_lista_fonte():
        agrupado = base_com_selecao().groupby("fonte_label")["valor"].sum()
        total = agrupado.sum()
        percentuais = (agrupado / total * 100).sort_values(ascending=False)
        itens = [(label, f"{valor:.1f}%") for label, valor in percentuais.items()]
        return _lista_cartao(itens)
