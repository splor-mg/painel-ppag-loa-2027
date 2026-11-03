from shiny import ui

_LINKS = [
    (
        "Plano Plurianual de Ação Governamental - PPAG",
        "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - SEPLAG, um "
        "breve resumo do que é o PPAG e inclui os documentos do PPAG vigente e dos "
        "exercícios anteriores. Também inclui os relatórios bimestrais de monitoramento "
        "do plano, o relatório anual de avaliação, os balanços sociais e materiais de "
        "apoio (manuais, treinamentos, conceitos e formulários).",
        "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/plano-plurianual-de-acao-governamental-ppag/plano-plurianual-de-acao",
    ),
    (
        "Lei de Diretrizes Orçamentárias - LDO",
        "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - SEPLAG, um "
        "breve resumo do que é a LDO e inclui os documentos da LDO vigente e dos "
        "exercícios anteriores. Traz também alguns materiais de apoio, tais como, a base "
        "de execução histórica das receitas e as regras e diretrizes gerais para a "
        "estimativa de receita.",
        "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/lei-de-diretrizes-orcamentarias-ldo/lei-de-diretrizes-orcamentarias",
    ),
    (
        "Lei Orçamentária Anual - LOA",
        "Apresenta no site da Secretaria de Estado de Planejamento e Gestão - SEPLAG, um "
        "breve resumo do que é a LOA e inclui os documentos da LOA vigente e dos "
        "exercícios anteriores. Além disso, traz o Decreto de Programação Orçamentária, "
        "o Classificador Econômico da Despesa, o Ementário da Receita e a relação de "
        "receitas que são desvinculadas por meio da Emenda nº 93/2016 (DREM).",
        "https://www.mg.gov.br/planejamento/pagina/planejamento-e-orcamento/lei-orcamentaria-anual-loa/lei-orcamentaria-anual-loa",
    ),
    (
        "ALMG - Leis que compõem o Sistema Orçamentário",
        "Página no site da Assembleia Legislativa do Estado de Minas Gerais, que contém "
        "as leis do sistema orçamentário estadual, a saber: PMDI, PPAG, LDO e LOA. Nesta "
        "página é possível consultar o andamento, as discussões e as emendas relativo as "
        "leis em questão.",
        "https://www.almg.gov.br/atividade-parlamentar/orcamento-do-estado/inicial/",
    ),
    (
        "Portal da Transparência - MG",
        "O Portal da Transparência de MG apresenta uma série de informações e consultas "
        "sobre despesas, receitas, incluindo algumas bases em formato de dados abertos.",
        "https://www.transparencia.mg.gov.br/",
    ),
    (
        "Legislação de Finanças Públicas - Lei nº 4.320, de 17 de março de 1964",
        "A Lei Federal nº 4.320, de 17 de março de 1964, dispõe sobre as normas gerais de "
        "Direito Financeiro para a elaboração e controle dos orçamentos e balanços da "
        "União, dos Estados, dos Municípios e do Distrito Federal.",
        "https://www.planalto.gov.br/ccivil_03/leis/l4320.htm",
    ),
    (
        "Legislação de Finanças Públicas - Lei Complementar nº 101, de 04 de maio de 2000",
        "A Lei Federal Complementar nº 101, de 04 de maio de 2000, conhecida como Lei de "
        "Responsabilidade Fiscal (LRF), estabelece as normas de finanças públicas "
        "voltadas para a responsabilidade na gestão fiscal e dá outras providências.",
        "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp101.htm",
    ),
]


def panel_ui():
    cards = [
        ui.div(
            ui.h5(titulo),
            ui.p(descricao),
            ui.a("Acessar página →", href=link, target="_blank", rel="noopener noreferrer"),
            class_="link-card",
        )
        for titulo, descricao, link in _LINKS
    ]
    return ui.nav_panel(
        "Links Úteis",
        ui.div("Links Úteis", class_="titulo-pagina"),
        ui.div(*cards, class_="grade-links"),
        value="links_uteis",
    )


def register_server(input, output, session):
    pass
