from shiny import ui


def panel_ui():
    return ui.nav_panel(
        "Sobre o Painel",
        ui.div("Sobre o Painel", class_="titulo-pagina"),
        ui.markdown(
            "**O que é a ferramenta:** Consiste num painel criado pela Subsecretaria de "
            "Planeamento e Orçamento (SPLOR) que agrega informações relativas ao PPAG "
            "2024-2027 (com revisão para 2027) e à Lei Orçamentária Anual (LOA) de 2027."
        ),
        ui.markdown(
            "**Finalidade:** O seu objetivo principal é proporcionar aos cidadãos uma "
            "forma mais visual, dinâmica e prática de aceder e interagir com os dados "
            "do orçamento do Estado de Minas Gerais, através da utilização de tabelas, "
            "mapas e gráficos."
        ),
        ui.markdown("**Componentes do Sistema de Planeamento e Orçamento:**"),
        ui.div(
            ui.div(
                ui.h5("PMDI"),
                ui.p(
                    "Plano Mineiro de Desenvolvimento Integrado: planeamento estratégico "
                    "de longo prazo focado em criar condições para o desenvolvimento "
                    "sustentável do estado."
                ),
                class_="bloco",
            ),
            ui.div(
                ui.h5("PPAG"),
                ui.p(
                    "Plano Plurianual de Ação Governamental: estipula as metas, ações e "
                    "programas da administração estadual com uma duração de quatro anos."
                ),
                class_="bloco",
            ),
            ui.div(
                ui.h5("LDO"),
                ui.p(
                    "Lei de Diretrizes Orçamentárias: funciona como uma ponte de ligação "
                    "entre o PPAG e a LOA, regulando a elaboração do orçamento e fixando "
                    "as prioridades para o ano seguinte."
                ),
                class_="bloco",
            ),
            ui.div(
                ui.h5("LOA"),
                ui.p(
                    "Lei Orçamentária Anual: tem como função prever as receitas e "
                    "estabelecer os limites de despesas para o próximo ano financeiro."
                ),
                class_="bloco",
            ),
            class_="grade-blocos",
        ),
        ui.hr(),
        ui.markdown(
            "Esta é a versão com **menu lateral** do painel, construída para comparar com a "
            "versão com "
            "[menu horizontal](https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny-acessivel-menu-horizontal/). "
            "Mesmos dados, mesmas regras de negócio, mesmos filtros e exportações — a "
            "diferença é só a disposição do menu de navegação."
        ),
        value="sobre",
    )


def register_server(input, output, session):
    pass
