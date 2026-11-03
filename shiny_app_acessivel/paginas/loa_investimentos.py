import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import botao_limpar_filtros, botoes_exportar, card_kpi, estilo_moeda, filtro_selectize
from exportar import csv_bytes, xlsx_bytes
from utils import formatar_bilhoes, formatar_moeda

_NOME_ARQUIVO = "loa_investimentos"


def panel_ui():
    return ui.nav_panel(
        "LOA Investimentos",
        ui.div("LOA Investimentos", class_="titulo-pagina"),
        ui.div(
            filtro_selectize("li_uo", "Unidade Orçamentária", dados.loa_investimentos_uo, multiplo=True),
            botao_limpar_filtros("li_limpar"),
            class_="filtros",
        ),
        ui.div(
            ui.output_ui("li_card_receita"),
            ui.output_ui("li_card_despesa"),
            class_="linha-cartoes",
        ),
        ui.div(
            botoes_exportar("li_csv", "li_xlsx"),
            ui.output_data_frame("li_tabela"),
            class_="tabela-card",
        ),
        value="loa_investimentos",
    )


def register_server(input, output, session):
    @reactive.calc
    def receita_filtrada() -> pd.DataFrame:
        df = dados.loa_investimentos_receita
        if input.li_uo():
            df = df[df["uo_label"].isin(input.li_uo())]
        return df

    @reactive.calc
    def despesa_filtrada() -> pd.DataFrame:
        df = dados.loa_investimentos_despesa
        if input.li_uo():
            df = df[df["uo_label"].isin(input.li_uo())]
        return df

    @reactive.calc
    def agrupado() -> pd.DataFrame:
        base = despesa_filtrada().groupby(["uo_label", "uo_sigla", "acao_label"])["valor"].sum().reset_index()
        return base.sort_values("valor", ascending=False).reset_index(drop=True)

    @reactive.calc
    def tabela() -> pd.DataFrame:
        base = agrupado()
        return pd.DataFrame(
            {
                "Unidade Orçamentária": base["uo_sigla"],
                "Ação Orçamentária": base["acao_label"],
                "LOA 2027 (R$)": base["valor"].map(formatar_moeda),
            }
        )

    @reactive.calc
    def linha_selecionada() -> pd.Series | None:
        selecao = li_tabela.cell_selection()
        if not selecao or not selecao["rows"]:
            return None
        base = agrupado()
        idx = selecao["rows"][0]
        if idx < 0 or idx >= len(base):
            return None
        return base.iloc[idx]

    @reactive.calc
    def receita_com_selecao() -> pd.DataFrame:
        linha = linha_selecionada()
        df = receita_filtrada()
        if linha is not None:
            df = df[df["uo_label"] == linha["uo_label"]]
        return df

    @reactive.calc
    def despesa_com_selecao() -> pd.DataFrame:
        linha = linha_selecionada()
        df = despesa_filtrada()
        if linha is not None:
            df = df[(df["uo_sigla"] == linha["uo_sigla"]) & (df["acao_label"] == linha["acao_label"])]
        return df

    @reactive.effect
    @reactive.event(input.li_limpar)
    async def _limpar():
        ui.update_selectize("li_uo", selected=[])
        # Chamado direto aqui (não só no efeito abaixo) porque, se a UO já
        # estava em branco, `input.li_uo()` não muda de valor e o efeito que
        # observa essa mudança não dispara.
        await li_tabela.update_cell_selection(None)

    @reactive.effect
    async def _limpar_selecao_ao_mudar_uo():
        # Ao trocar a UO, a ordem/linhas da tabela mudam -- limpa a seleção
        # de linha para não apontar para um índice que agora é outra linha.
        input.li_uo()
        await li_tabela.update_cell_selection(None)

    @render.ui
    def li_card_receita():
        total = receita_com_selecao()["valor"].sum()
        return card_kpi("Receita Total (R$) - 2027", formatar_bilhoes(total))

    @render.ui
    def li_card_despesa():
        total = despesa_com_selecao()["valor"].sum()
        return card_kpi("Despesa Total (R$) - 2027", formatar_bilhoes(total))

    @render.data_frame
    def li_tabela():
        df = tabela()
        return render.DataGrid(
            df,
            width="100%",
            height="420px",
            summary=False,
            selection_mode="row",
            styles=estilo_moeda(df, "LOA 2027 (R$)"),
        )

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def li_csv():
        yield csv_bytes(tabela())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def li_xlsx():
        yield xlsx_bytes(tabela())
