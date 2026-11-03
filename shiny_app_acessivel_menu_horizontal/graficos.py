"""Construtores de gráficos Plotly reaproveitados por várias páginas."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import formatar_bi_arredondado, formatar_moeda, quebrar_rotulo

_COR_MARCA = "#0047AB"
_FONTE = "system-ui, -apple-system, Segoe UI, Arial, sans-serif"


def grafico_percentual_horizontal(
    df: pd.DataFrame, coluna_categoria: str, coluna_valor: str, titulo: str
) -> "px.Figure":
    """Barras horizontais com o % do total de `coluna_valor`, por `coluna_categoria`.

    Altura calculada pela quantidade de categorias, para caber rótulos
    maiores; o card visível (CSS) que a envolve controla a rolagem.
    """
    categorias = df[coluna_categoria].str.strip()
    agrupado = df.groupby(categorias)[coluna_valor].sum()
    percentual = (agrupado / agrupado.sum() * 100).sort_values(ascending=True)

    percentual_df = percentual.reset_index()
    percentual_df.columns = [coluna_categoria, "percentual"]

    altura = max(340, 32 * len(percentual_df) + 90)

    fig = px.bar(
        percentual_df,
        x="percentual",
        y=coluna_categoria,
        orientation="h",
        title=f"<b>{titulo}</b>",
        text=percentual_df["percentual"].map(lambda v: f"{v:.1f}%"),
        labels={"percentual": "% do total", coluna_categoria: ""},
        color_discrete_sequence=["#0047AB"],
        custom_data=[coluna_categoria],
    )
    maior_percentual = percentual_df["percentual"].max()

    fig.update_traces(textfont_size=15, textposition="outside", cliponaxis=False)
    fig.update_layout(
        showlegend=False,
        height=altura,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=40, t=40, b=10),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        xaxis=dict(gridcolor="#eef1f4", range=[0, maior_percentual * 1.18]),
    )
    return fig


def percentuais_por_categoria(
    df: pd.DataFrame, coluna_categoria: str, coluna_valor: str
) -> pd.DataFrame:
    """Participação percentual de cada categoria no total de `coluna_valor`,
    ordenada da maior pra menor -- mesma agregação de
    `grafico_percentual_horizontal()`, mas sem montar a figura Plotly
    (usada pelas barras de progresso da Visão Geral, ver
    `componentes.barras_progresso()`).
    """
    categorias = df[coluna_categoria].str.strip()
    agrupado = df.groupby(categorias)[coluna_valor].sum()
    percentual = (agrupado / agrupado.sum() * 100).sort_values(ascending=False)
    resultado = percentual.reset_index()
    resultado.columns = [coluna_categoria, "percentual"]
    return resultado


def grafico_absoluto_vertical(
    df: pd.DataFrame, coluna_categoria: str, coluna_valor: str, titulo: str
) -> "px.Figure":
    """Colunas verticais com a soma absoluta de `coluna_valor`, por `coluna_categoria`.

    Rótulo no formato "N bi" (arredondado), ordenado da maior para a menor.
    """
    agrupado = df.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
    agrupado = agrupado.sort_values(coluna_valor, ascending=False)
    agrupado["_rotulo_original"] = agrupado[coluna_categoria]
    agrupado[coluna_categoria] = agrupado[coluna_categoria].map(quebrar_rotulo)

    fig = px.bar(
        agrupado,
        x=coluna_categoria,
        y=coluna_valor,
        title=f"<b>{titulo}</b>",
        text=agrupado[coluna_valor].map(formatar_bi_arredondado),
        labels={coluna_valor: "Valor (R$)", coluna_categoria: ""},
        color_discrete_sequence=["#0047AB"],
        custom_data=["_rotulo_original"],
    )
    valor_max = agrupado[coluna_valor].max()

    fig.update_traces(textfont_size=13, textposition="outside", cliponaxis=False)
    fig.update_layout(
        showlegend=False,
        height=340,
        font=dict(family="system-ui, -apple-system, Segoe UI, Arial, sans-serif", color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=70),
        xaxis=dict(tickfont=dict(size=10), tickangle=0, automargin=True),
        yaxis=dict(gridcolor="#eef1f4", range=[0, valor_max * 1.18]),
    )
    return fig


def grafico_absoluto_horizontal(
    df: pd.DataFrame, coluna_categoria: str, coluna_valor: str, titulo: str
) -> "px.Figure":
    """Barras horizontais com a soma absoluta de `coluna_valor`, por `coluna_categoria`."""
    agrupado = df.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
    agrupado = agrupado.sort_values(coluna_valor, ascending=True)

    fig = px.bar(
        agrupado,
        x=coluna_valor,
        y=coluna_categoria,
        orientation="h",
        title=f"<b>{titulo}</b>",
        text=agrupado[coluna_valor].map(formatar_bi_arredondado),
        labels={coluna_valor: "Valor (R$)", coluna_categoria: ""},
        color_discrete_sequence=[_COR_MARCA],
        custom_data=[coluna_categoria],
    )
    valor_min = min(0, agrupado[coluna_valor].min())
    valor_max = agrupado[coluna_valor].max()
    margem = (valor_max - valor_min) * 0.15

    fig.update_traces(textfont_size=15, textposition="outside", cliponaxis=False)
    fig.update_layout(
        showlegend=False,
        height=280,
        font=dict(family=_FONTE, color="#1f2933"),
        title=dict(font=dict(size=16, color="#1f2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=40, t=40, b=10),
        yaxis=dict(tickfont=dict(size=12), automargin=True),
        xaxis=dict(gridcolor="#eef1f4", range=[valor_min - margem, valor_max + margem]),
    )
    return fig


def grafico_por_ano(anos: list[int], valores: list[float], titulo: str, formatar) -> "go.Figure":
    """Barras verticais, uma por ano (Ação Orçamentária: Previsão Física/
    Orçamentária 2027-2030)."""
    textos = [formatar(v) for v in valores]
    valor_max = max(valores) if valores else 0

    fig = go.Figure(
        go.Bar(
            x=[str(ano) for ano in anos],
            y=valores,
            text=textos,
            textposition="outside",
            marker=dict(color=_COR_MARCA),
            cliponaxis=False,
        )
    )
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", font=dict(size=16, color="#1f2933")),
        showlegend=False,
        height=340,
        font=dict(family=_FONTE, color="#1f2933"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=40),
        xaxis=dict(type="category", tickfont=dict(size=12)),
        yaxis=dict(gridcolor="#eef1f4", range=[0, valor_max * 1.2 if valor_max else 1]),
    )
    return fig
