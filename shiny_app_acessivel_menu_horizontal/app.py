"""Painel PPAG-LOA 2027 — versão Shiny for Python / Shinylive (acessível),
variante com menu horizontal.

Cópia de `../shiny_app_acessivel/` (mesmos dados, mesma lógica reativa,
mesmos componentes) para comparação lado a lado -- a ÚNICA diferença
entre as duas é a disposição do menu de navegação: aqui, horizontal,
logo abaixo do título (`ui.navset_pill` em vez de `ui.navset_pill_list`).
Depois da comparação, uma das duas variantes deve ser escolhida como
final e a outra removida.
"""

from pathlib import Path

from shiny import App, ui

from componentes import (
    plotly_head,
    script_barra_progresso_clique,
    script_limpar_selecao_grafico,
    script_preservar_estado_tabela,
    script_skip_link,
)
from paginas import (
    acao_orcamentaria,
    despesa_fiscal,
    despesa_orgao,
    glossario,
    links_uteis,
    loa_investimentos,
    programa,
    qdd,
    receita_fiscal,
    regionalizacao,
    sobre,
    visao_geral,
)

_PAGINAS = [
    sobre,
    visao_geral,
    acao_orcamentaria,
    programa,
    regionalizacao,
    receita_fiscal,
    despesa_fiscal,
    despesa_orgao,
    qdd,
    loa_investimentos,
    glossario,
    links_uteis,
]

app_ui = ui.page_bootstrap(
    ui.tags.head(
        plotly_head(),
        script_limpar_selecao_grafico(),
        script_barra_progresso_clique(),
        script_skip_link(),
        script_preservar_estado_tabela(),
        ui.tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
        ui.tags.link(
            rel="stylesheet",
            href=(
                "https://fonts.googleapis.com/css2?"
                "family=Lexend:wght@500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap"
            ),
        ),
        ui.tags.link(rel="stylesheet", href="estilo.css"),
    ),
    ui.tags.a("Pular para o conteúdo", href="#conteudo-principal", class_="skip-link"),
    ui.tags.header(
        ui.span("Painel PPAG-LOA 2027", class_="app-titulo"),
        ui.span("Versão acessível", class_="app-subtitulo"),
        class_="app-cabecalho",
    ),
    ui.div(
        ui.navset_pill(
            *[pagina.panel_ui() for pagina in _PAGINAS],
            id="pagina_ativa",
        ),
        id="area-navegacao",
        class_="app-conteudo",
    ),
    ui.tags.footer(
        ui.hr(),
        ui.p(
            "Construído com Shiny for Python + Shinylive.",
            class_="text-muted small text-center mb-3",
        ),
    ),
    title="Painel PPAG-LOA 2027 — Acessível",
)


def server(input, output, session):
    for pagina in _PAGINAS:
        pagina.register_server(input, output, session)


app = App(app_ui, server, static_assets={"/": Path(__file__).parent / "www"})
