import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import (
    botao_limpar_filtros,
    botoes_exportar,
    card_kpi,
    estilo_moeda,
    filtro_selectize,
    grafico_acessivel,
    limpar_selecao_graficos,
    selecao_grafico,
)
from exportar import csv_bytes, xlsx_bytes
from graficos import grafico_absoluto_horizontal
from utils import formatar_bilhoes, formatar_moeda

_NOME_ARQUIVO = "receita_fiscal_uo_fonte"


def panel_ui():
    uos = sorted(dados.receita_fiscal["UO"].unique())
    fontes = sorted(dados.receita_fiscal["fonte_de_recursos"].unique())
    return ui.nav_panel(
        "Receita Fiscal",
        ui.div("Receita Fiscal", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("rf_uo", "Unidade Orçamentária", uos, multiplo=True),
            filtro_selectize("rf_fonte", "Fonte de Recursos", fontes, multiplo=True),
            botao_limpar_filtros("rf_limpar"),
            class_="filtros",
        ),
        ui.div(ui.output_ui("rf_card"), class_="linha-cartao-unico"),
        ui.div(ui.output_ui("rf_grafico"), class_="grafico-card"),
        ui.div(
            botoes_exportar("rf_csv", "rf_xlsx"),
            ui.output_data_frame("rf_tabela"),
            class_="tabela-card",
        ),
        value="receita_fiscal",
    )


def register_server(input, output, session):
    @reactive.calc
    def linhas_filtradas() -> pd.DataFrame:
        df = dados.receita_fiscal
        if input.rf_uo():
            df = df[df["UO"].isin(input.rf_uo())]
        if input.rf_fonte():
            df = df[df["fonte_de_recursos"].isin(input.rf_fonte())]
        return df

    @reactive.calc
    def linhas_com_selecao() -> pd.DataFrame:
        # Clique numa barra do gráfico de categoria econômica filtra o card
        # e a tabela, mas não o próprio gráfico (que continua mostrando
        # todas as categorias, para o usuário poder trocar de seleção).
        df = linhas_filtradas()
        categoria = selecao_grafico(input, "rf_grafico")
        if categoria:
            df = df[df["categoria_receita_desc"] == categoria]
        return df

    @reactive.calc
    def tabela_uo_fonte() -> pd.DataFrame:
        agrupado = linhas_com_selecao().groupby(["UO", "fonte_de_recursos"])["valor"].sum().reset_index()
        agrupado = agrupado.sort_values("valor", ascending=False)
        return pd.DataFrame(
            {
                "UO": agrupado["UO"],
                "Fonte de Recursos": agrupado["fonte_de_recursos"],
                "LOA 2027 (R$)": agrupado["valor"].map(formatar_moeda),
            }
        )

    @reactive.effect
    @reactive.event(input.rf_limpar)
    async def _limpar():
        ui.update_selectize("rf_uo", selected=[])
        ui.update_selectize("rf_fonte", selected=[])
        await limpar_selecao_graficos(session, "rf_grafico")

    @render.ui
    def rf_card():
        total = linhas_com_selecao()["valor"].sum()
        return card_kpi("Receita Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def rf_grafico():
        df = linhas_filtradas()
        fig = grafico_absoluto_horizontal(
            df, "categoria_receita_desc", "valor", "Receitas por Categoria Econômica"
        )
        agrupado = df.groupby("categoria_receita_desc", as_index=False)["valor"].sum()
        tabela = agrupado.rename(columns={"categoria_receita_desc": "Categoria Econômica"})
        tabela["Valor (R$)"] = agrupado["valor"].map(formatar_moeda)
        tabela = tabela[["Categoria Econômica", "Valor (R$)"]]
        return grafico_acessivel(
            fig, tabela, id="rf_grafico", titulo="Receitas por Categoria Econômica", selecionavel=True
        )

    @render.data_frame
    def rf_tabela():
        df = tabela_uo_fonte()
        return render.DataGrid(
            df, width="100%", height="420px", summary=False, styles=estilo_moeda(df, "LOA 2027 (R$)")
        )

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv", label="Exportar CSV")
    def rf_csv():
        yield csv_bytes(tabela_uo_fonte())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx", label="Exportar Excel")
    def rf_xlsx():
        yield xlsx_bytes(tabela_uo_fonte())
