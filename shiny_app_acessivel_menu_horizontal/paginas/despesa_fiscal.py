from shiny import reactive, render, ui

import dados_app as dados
from componentes import card_kpi, grafico_acessivel, selecao_grafico
from graficos import grafico_absoluto_vertical, grafico_percentual_horizontal
from utils import formatar_bilhoes, formatar_moeda


def panel_ui():
    return ui.nav_panel(
        "Despesa Fiscal",
        ui.div("Despesa Fiscal", class_="titulo-pagina"),
        ui.div(ui.output_ui("df_card"), class_="linha-cartao-unico"),
        ui.div(ui.output_ui("df_grafico_poder"), class_="grafico-card"),
        ui.div(
            ui.div(ui.output_ui("df_grafico_grupo"), class_="grafico-card"),
            ui.div(ui.output_ui("df_grafico_funcao"), class_="grafico-card"),
            class_="grade-graficos",
        ),
        value="despesa_fiscal",
    )


def register_server(input, output, session):
    def _base_excluindo(dimensao_excluida: str | None):
        # Base com as 3 dimensões (poder, grupo, função) na mesma linha --
        # cada gráfico filtra pelas seleções feitas nos OUTROS dois (não na
        # sua própria), para continuar mostrando todas as suas categorias.
        df = dados.despesa_fiscal_detalhe
        poder = selecao_grafico(input, "df_grafico_poder")
        grupo = selecao_grafico(input, "df_grafico_grupo")
        funcao = selecao_grafico(input, "df_grafico_funcao")
        if dimensao_excluida != "poder" and poder:
            df = df[df["uo_poder"] == poder]
        if dimensao_excluida != "grupo" and grupo:
            df = df[df["grupo_despesa_descricao"] == grupo]
        if dimensao_excluida != "funcao" and funcao:
            df = df[df["funcao_descricao"] == funcao]
        return df

    @reactive.calc
    def base_para_card():
        return _base_excluindo(None)

    @reactive.calc
    def base_para_poder():
        return _base_excluindo("poder")

    @reactive.calc
    def base_para_grupo():
        return _base_excluindo("grupo")

    @reactive.calc
    def base_para_funcao():
        return _base_excluindo("funcao")

    @render.ui
    def df_card():
        total = base_para_card()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def df_grafico_poder():
        df = base_para_poder()
        fig = grafico_absoluto_vertical(
            df, "uo_poder", "valor", "Despesa por Poder e Reserva de Contingência"
        )
        agrupado = df.groupby("uo_poder", as_index=False)["valor"].sum()
        tabela = agrupado.rename(columns={"uo_poder": "Poder"})
        tabela["Valor (R$)"] = agrupado["valor"].map(formatar_moeda)
        tabela = tabela[["Poder", "Valor (R$)"]]
        return grafico_acessivel(
            fig, tabela, id="df_grafico_poder", titulo="Despesa por Poder e Reserva de Contingência", selecionavel=True
        )

    @render.ui
    def df_grafico_grupo():
        df = base_para_grupo()
        fig = grafico_percentual_horizontal(df, "grupo_despesa_descricao", "valor", "Despesa por Grupo")
        agrupado = df.groupby("grupo_despesa_descricao", as_index=False)["valor"].sum()
        tabela = agrupado.rename(columns={"grupo_despesa_descricao": "Grupo de Despesa"})
        tabela["Valor (R$)"] = agrupado["valor"].map(formatar_moeda)
        tabela = tabela[["Grupo de Despesa", "Valor (R$)"]]
        return grafico_acessivel(fig, tabela, id="df_grafico_grupo", titulo="Despesa por Grupo", selecionavel=True)

    @render.ui
    def df_grafico_funcao():
        df = base_para_funcao()
        fig = grafico_percentual_horizontal(df, "funcao_descricao", "valor", "Despesa por Função")
        agrupado = df.groupby("funcao_descricao", as_index=False)["valor"].sum()
        tabela = agrupado.rename(columns={"funcao_descricao": "Função"})
        tabela["Valor (R$)"] = agrupado["valor"].map(formatar_moeda)
        tabela = tabela[["Função", "Valor (R$)"]]
        return grafico_acessivel(fig, tabela, id="df_grafico_funcao", titulo="Despesa por Função", selecionavel=True)
