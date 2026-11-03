import pandas as pd
from shiny import reactive, render, ui

import dados_app as dados
from componentes import (
    botao_limpar_filtros,
    botoes_exportar,
    estilo_moeda,
    filtro_selectize,
    registrar_filtros_cruzados,
)
from exportar import csv_bytes, xlsx_bytes
from utils import formatar_moeda

_NOME_ARQUIVO = "qdd"
_FILTROS = [
    ("qdd_uo", "uo_label", "Unidade Orçamentária"),
    ("qdd_programa", "programa_label", "Programa"),
    ("qdd_acao", "acao_label", "Ação Orçamentária"),
    ("qdd_grupo", "grupo_label", "Grupo de Despesa"),
    ("qdd_iag", "iag_label", "IAG"),
    ("qdd_fonte", "fonte_label", "Fonte de Recursos"),
    ("qdd_ipu", "ipu_label", "IPU"),
    ("qdd_elemento", "elemento_label", "Elemento de Despesa"),
]
_COLUNAS_SAIDA = {
    "uo_label": "Unidade Orçamentária",
    "programa_label": "Programa",
    "acao_label": "Ação Orçamentária",
    "grupo_label": "Grupo de Despesa",
    "iag_label": "IAG",
    "fonte_label": "Fonte de Recursos",
    "ipu_label": "IPU",
    "elemento_label": "Elemento de Despesa",
}


def panel_ui():
    campos = []
    for id_input, coluna, rotulo in _FILTROS:
        opcoes = sorted(dados.qdd[coluna].unique())
        campos.append(filtro_selectize(id_input, rotulo, opcoes, multiplo=True))
    campos.append(botao_limpar_filtros("qdd_limpar"))

    return ui.nav_panel(
        "QDD",
        ui.div("QDD", class_="titulo-pagina"),
        ui.p("Quadro de Detalhamento da Despesa", class_="text-muted"),
        ui.div(*campos, class_="filtros"),
        ui.div(
            botoes_exportar("qdd_csv", "qdd_xlsx"),
            ui.output_data_frame("qdd_tabela"),
            class_="tabela-card",
        ),
        value="qdd",
    )


def register_server(input, output, session):
    registrar_filtros_cruzados(
        input, dados.qdd, [(id_input, coluna, "Todas") for id_input, coluna, _ in _FILTROS], multiplo=True
    )

    @reactive.calc
    def base_filtrada() -> pd.DataFrame:
        df = dados.qdd
        for id_input, coluna, _ in _FILTROS:
            valor = getattr(input, id_input)()
            if valor:
                df = df[df[coluna].isin(valor)]
        return df

    @reactive.calc
    def tabela() -> pd.DataFrame:
        colunas_dimensao = list(_COLUNAS_SAIDA.keys())
        agrupado = base_filtrada().groupby(colunas_dimensao)["valor"].sum().reset_index()
        agrupado = agrupado.sort_values("valor", ascending=False)
        saida = agrupado.rename(columns=_COLUNAS_SAIDA)
        saida["LOA 2027 (R$)"] = agrupado["valor"].map(formatar_moeda)
        return saida[list(_COLUNAS_SAIDA.values()) + ["LOA 2027 (R$)"]]

    @reactive.effect
    @reactive.event(input.qdd_limpar)
    def _limpar():
        for id_input, _, _ in _FILTROS:
            ui.update_selectize(id_input, selected=[])

    @render.data_frame
    def qdd_tabela():
        df = tabela()
        return render.DataGrid(
            df, width="100%", height="520px", summary=False, styles=estilo_moeda(df, "LOA 2027 (R$)")
        )

    @render.download_button(filename=f"{_NOME_ARQUIVO}.csv")
    def qdd_csv():
        yield csv_bytes(tabela())

    @render.download_button(filename=f"{_NOME_ARQUIVO}.xlsx")
    def qdd_xlsx():
        yield xlsx_bytes(tabela())
