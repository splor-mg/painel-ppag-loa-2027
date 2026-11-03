"""Painel PPAG-LOA 2027 — versão Shiny for Python / Shinylive (acessível).

Ver ../docs/premissas.md e
../docs/superpowers/specs/2026-10-26-painel-shiny-acessivel-design.md.
Menu lateral, paleta/tipografia próprias, toggle "Ver como tabela" em
cada gráfico, foco visível e skip link.

Existe também `../shiny_app_acessivel_menu_horizontal/` -- cópia idêntica
desta, só com o menu disposto horizontalmente em vez de lateral, para
comparação lado a lado (ver docstring de lá).
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
        ui.span("Versão acessível — menu lateral", class_="app-subtitulo"),
        class_="app-cabecalho",
    ),
    ui.div(
        ui.navset_pill_list(
            *[pagina.panel_ui() for pagina in _PAGINAS],
            id="pagina_ativa",
            well=False,
            widths=(2, 10),
        ),
        id="area-navegacao",
        class_="app-conteudo",
    ),
    ui.tags.footer(
        ui.hr(),
        ui.p(
            "Construído com Shiny for Python + Shinylive — versão acessível com menu lateral, "
            "comparada com a ",
            ui.a(
                "versão com menu horizontal",
                href="https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny-acessivel-menu-horizontal/",
                target="_blank",
                rel="noopener noreferrer",
            ),
            ".",
            class_="text-muted small text-center mb-3",
        ),
    ),
    title="Painel PPAG-LOA 2027 — Acessível (menu lateral)",
)


def server(input, output, session):
    for pagina in _PAGINAS:
        pagina.register_server(input, output, session)


app = App(app_ui, server, static_assets={"/": Path(__file__).parent / "www"})
