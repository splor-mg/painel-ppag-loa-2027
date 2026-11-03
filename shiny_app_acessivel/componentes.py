"""Componentes de UI reaproveitados pelas páginas do painel Shiny."""

import html
from shiny import reactive, ui
from shiny.types import SilentException


def selecao_grafico(input, id: str):
    """Lê o valor de um input de seleção de gráfico (`<id>_selecionado`,
    criado por `plotly_html(..., id=id, selecionavel=True)`).

    Antes do primeiro clique, esse input nunca foi definido pelo cliente —
    chamar `input.<id>_selecionado()` direto levanta `SilentException` (API
    do Shiny para "ainda não tem valor"), o que faria QUALQUER saída que
    dependesse dele ficar em branco silenciosamente, mesmo sem nenhum
    clique ter acontecido. Aqui isso é tratado como "nada selecionado"
    (`None`), que é o comportamento desejado.
    """
    try:
        return getattr(input, f"{id}_selecionado")()
    except SilentException:
        return None


def script_limpar_selecao_grafico() -> ui.Tag:
    """Registra (uma única vez, no <head> do app) o handler que permite ao
    servidor desmarcar a seleção de um gráfico clicável a partir de um
    botão "Limpar filtros" (ver `limpar_selecao_graficos()`).

    `<id>_selecionado` é um input "ad-hoc" (só existe por causa do
    `Shiny.setInputValue` feito no clique, sem elemento de UI próprio),
    então não existe um `ui.update_*` pronto para ele -- a única forma de
    zerá-lo a partir do servidor é mandar o cliente fazer isso, daí a
    mensagem customizada.
    """
    return ui.tags.script(
        """
(function registrar() {
  if (window.Shiny && Shiny.addCustomMessageHandler) {
    Shiny.addCustomMessageHandler("limpar_selecao_grafico", function(msg) {
      (msg.ids || []).forEach(function(id) {
        Shiny.setInputValue(id + "_selecionado", null, {priority: "event"});
      });
    });
  } else {
    setTimeout(registrar, 50);
  }
})();
"""
    )


def script_skip_link() -> ui.Tag:
    """Registra (uma única vez, no <head> do app) o ajuste do link "Pular
    para o conteúdo" -- ver `app.py`.

    O wrapper `#area-navegacao` (antigo `#conteudo-principal`) engloba o
    `navset_pill_list(...)` inteiro, menu lateral (12 links) incluído, então
    mandar o foco pra ele não pula nada: o primeiro elemento focável lá
    dentro continua sendo o 1o link do menu. O conteúdo real da aba ativa
    fica em `.tab-content` (gerado pelo JS do próprio Shiny/bslib, por
    isso o polling -- não existe ainda quando este script é parseado), daí
    o id/tabindex de destino do skip link serem transferidos pra lá em vez
    de ficarem no wrapper.
    """
    return ui.tags.script(
        """
(function registrar() {
  var destino = document.querySelector('#area-navegacao .tab-content');
  if (destino) {
    destino.id = 'conteudo-principal';
    destino.tabIndex = -1;
  } else {
    setTimeout(registrar, 50);
  }
})();
"""
    )


def script_preservar_estado_tabela() -> ui.Tag:
    """Registra (uma única vez, no <head> do app) a preservação do estado
    do toggle "Ver como tabela"/"Ocultar tabela" (ver `grafico_acessivel()`)
    entre re-renderizações.

    Cada gráfico acessível vive dentro de um `@render.ui` -- qualquer
    invalidação reativa (filtro, crossfilter) substitui o HTML inteiro do
    bloco gráfico+botão+tabela, o que por padrão: (a) fecha de novo a
    tabela se o usuário tinha aberto, e (b) solta o foco do teclado pra
    `<body>` se ele estava no botão.

    Em vez de precisar de plumbing nova em `grafico_acessivel()` ou de
    mapear ids de saída -> id de tabela, isso é resolvido só observando o
    DOM: o botão sempre aponta pra sua tabela via `aria-controls`, então
    basta guardar quais ids de tabela estão abertos (clique no botão) e
    qual botão tinha o foco, e reaplicar isso depois de cada evento
    `shiny:value` (disparado pelo Shiny quando uma saída é re-renderizada)
    -- com um duplo `requestAnimationFrame` de margem pra garantir que o
    HTML novo já foi inserido no DOM antes de tentar achar os elementos.

    `shiny:value` é disparado via `jQuery(el).trigger(evt)` (não
    `el.dispatchEvent`) -- o jQuery simula o bubbling só entre handlers
    registrados por `$(...).on(...)`, então um `document.addEventListener`
    nativo nunca vê esse evento (confirmado empiricamente: zero disparos).
    Por isso o listener do evento usa `jQuery(document).on(...)`, exposto
    globalmente pelo próprio bundle do Shiny -- os listeners de `click` e
    `focusin` continuam nativos, pois esses são eventos reais do
    navegador e bubblam normalmente.
    """
    return ui.tags.script(
        """
(function registrar() {
  if (window.Shiny && Shiny.addCustomMessageHandler && window.jQuery) {
    var tabelasAbertas = new Set();
    var botaoComFoco = null;

    function aplicarEstado(idTabela) {
      var tabela = document.getElementById(idTabela);
      if (!tabela) return;
      tabela.hidden = false;
      var botao = document.querySelector('[aria-controls="' + idTabela + '"]');
      if (botao) {
        botao.setAttribute('aria-expanded', 'true');
        botao.textContent = 'Ocultar tabela';
      }
    }

    document.addEventListener('click', function(ev) {
      var botao = ev.target.closest('.botao-ver-tabela');
      if (!botao) return;
      var idTabela = botao.getAttribute('aria-controls');
      if (!idTabela) return;
      var tabela = document.getElementById(idTabela);
      if (tabela && !tabela.hidden) {
        tabelasAbertas.add(idTabela);
      } else {
        tabelasAbertas.delete(idTabela);
      }
    });

    document.addEventListener('focusin', function(ev) {
      var botao = ev.target.closest && ev.target.closest('.botao-ver-tabela');
      botaoComFoco = botao ? botao.getAttribute('aria-controls') : botaoComFoco;
    });

    window.jQuery(document).on('shiny:value', function() {
      if (tabelasAbertas.size === 0 && !botaoComFoco) return;
      requestAnimationFrame(function() {
        requestAnimationFrame(function() {
          tabelasAbertas.forEach(aplicarEstado);
          if (botaoComFoco && document.activeElement === document.body) {
            var botao = document.querySelector('[aria-controls="' + botaoComFoco + '"]');
            if (botao) botao.focus();
          }
        });
      });
    });
  } else {
    setTimeout(registrar, 50);
  }
})();
"""
    )


async def limpar_selecao_graficos(session, *ids: str) -> None:
    """Desmarca a seleção de um ou mais gráficos clicáveis (`plotly_html(...,
    id=id, selecionavel=True)`) a partir do servidor -- chamar no efeito do
    botão "Limpar filtros" da página, junto com os `ui.update_selectize(...)`
    dos demais filtros.
    """
    await session.send_custom_message("limpar_selecao_grafico", {"ids": list(ids)})


def plotly_html(fig, id: str | None = None, selecionavel: bool = False) -> ui.HTML:
    """Converte uma figura Plotly em HTML embutível via `@render.ui`.

    Plotly.js é carregado uma única vez (CDN, incluído no <head> do app via
    `plotly_head()`); aqui só o HTML/JS específico da figura é gerado.

    `selecionavel=True` (exige `id`) liga um clique numa barra a um input
    reativo `<id>_selecionado` (lido via `input.<id>_selecionado()`),
    usado para o crossfilter entre visuais da mesma página -- clicar de
    novo na mesma barra desseleciona (`None`). Depende de `custom_data`
    com a categoria "crua" ter sido passado ao `px.bar(...)` em
    `graficos.py` (necessário pois `grafico_absoluto_vertical` quebra o
    rótulo do eixo em várias linhas, então o texto do eixo clicado não
    bate com o valor original da coluna).

    O `<div>` do próprio Plotly usa um id distinto de `id` (sufixo
    `__plot`), já que `id` é o id do `<div>` de saída do `@render.ui` que
    o envolve (`ui.output_ui(id)`) -- usar o mesmo id nos dois quebra o
    `document.getElementById` (pega o elemento errado).
    """
    post_script = None
    div_id = f"{id}__plot" if id else None
    if selecionavel and id:
        # Limitação conhecida (fora do escopo desta leva de correções):
        # o crossfilter só é acionável por clique/toque -- as barras do
        # Plotly não são elementos focáveis, então não há caminho por
        # teclado até esta seleção. Requer uma função própria (barras
        # focáveis + handler de tecla), não uma correção pontual aqui.
        post_script = f"""
var el = document.getElementById("{div_id}");
var ultimoClique = null;
el.on("plotly_click", function(dados) {{
    var ponto = dados.points[0];
    var valor = (ponto.customdata && ponto.customdata.length) ? ponto.customdata[0] : ponto.label;
    if (valor === ultimoClique) {{
        ultimoClique = null;
        Shiny.setInputValue("{id}_selecionado", null, {{priority: "event"}});
    }} else {{
        ultimoClique = valor;
        Shiny.setInputValue("{id}_selecionado", valor, {{priority: "event"}});
    }}
}});
"""
    return ui.HTML(
        fig.to_html(
            include_plotlyjs=False,
            full_html=False,
            div_id=div_id,
            post_script=post_script,
            config={"displayModeBar": False, "responsive": True},
        )
    )


def _botao_ver_tabela(id_tabela: str) -> ui.Tag:
    """Botão "Ver como tabela"/"Ocultar tabela" que alterna a visibilidade
    da `<table id="{id_tabela}">` correspondente (ver `_tabela_semantica()`
    e `script_preservar_estado_tabela()`).
    """
    return ui.tags.button(
        "Ver como tabela",
        type="button",
        class_="botao-ver-tabela",
        **{
            "aria-expanded": "false",
            "aria-controls": id_tabela,
            "onclick": (
                f"var t=document.getElementById('{id_tabela}');"
                f"var oculto=t.hidden; t.hidden=!oculto;"
                f"this.setAttribute('aria-expanded', String(oculto));"
                f"this.textContent = oculto ? 'Ocultar tabela' : 'Ver como tabela';"
            ),
        },
    )


def _tabela_semantica(df, id_tabela: str, titulo: str) -> ui.HTML:
    """Tabela semântica com os mesmos dados de `df`, alternada pelo botão
    de `_botao_ver_tabela()` -- para quem usa leitor de tela/teclado, ou só
    quer os números exatos sem passar o mouse sobre um gráfico/barra.
    """
    linhas_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(valor))}</td>" for valor in linha) + "</tr>"
        for linha in df.itertuples(index=False)
    )
    cabecalho_html = "".join(f'<th scope="col">{html.escape(str(coluna))}</th>' for coluna in df.columns)
    titulo_escapado = html.escape(titulo)
    return ui.HTML(
        f'<table id="{id_tabela}" hidden class="tabela-acessivel" aria-label="{titulo_escapado}">'
        f"<thead><tr>{cabecalho_html}</tr></thead>"
        f"<tbody>{linhas_html}</tbody>"
        f"</table>"
    )


def grafico_acessivel(fig, df, id: str, titulo: str, selecionavel: bool = False) -> ui.Tag:
    """Como `plotly_html()`, mas com um botão "Ver como tabela" ao lado
    que alterna a visibilidade de uma <table> semântica com os mesmos
    dados de `df`, mostrada ao lado do gráfico (não no lugar dele -- daí o
    rótulo do botão no segundo estado ser "Ocultar tabela", não "Ver como
    gráfico": o gráfico nunca é escondido) -- para quem usa leitor de
    tela/teclado, ou só quer os números exatos sem passar o mouse sobre
    as barras.

    A tabela é reconstruída a cada render (como o gráfico), então
    reflete sempre os dados atuais -- incluindo depois de um filtro ou
    de uma seleção de crossfilter.

    Limitação conhecida (mitigada, não eliminada): como todo o retorno
    desta função vive dentro de um `@render.ui`, qualquer invalidação
    reativa troca o HTML inteiro do bloco gráfico+botão+tabela. O estado
    "tabela aberta" e o foco do teclado no botão são restaurados depois
    do re-render por `script_preservar_estado_tabela()` (registrado uma
    vez no <head> do app, via observação de DOM/eventos `shiny:value` --
    não precisa de nenhuma mudança na assinatura desta função nem nos
    chamadores), mas é um remendo client-side best-effort: cobre o caso
    comum (filtro/crossfilter muda, o próprio gráfico permanece na tela),
    não garante nada se o elemento de destino some de vez (ex.: troca de
    aba) nem se o Shiny atrasar o re-render além de dois
    `requestAnimationFrame`.
    """
    id_tabela = f"{id}__tabela"
    return ui.div(
        _botao_ver_tabela(id_tabela),
        plotly_html(fig, id=id, selecionavel=selecionavel),
        _tabela_semantica(df, id_tabela, titulo),
        class_="grafico-acessivel",
    )


def script_barra_progresso_clique() -> ui.Tag:
    """Registra (uma única vez, no <head> do app) o clique nas barras de
    progresso selecionáveis (`barras_progresso(..., selecionavel=True)`).

    Equivalente ao `plotly_click` de `plotly_html()`, só que via um único
    handler delegado -- os botões ainda não existem quando este script é
    parseado (cada chamada de `barras_progresso()` vive dentro de um
    `@render.ui`), e cada página pode ter mais de uma lista de barras
    (daí o escopo "desmarcar as outras" ser só dentro do mesmo
    `[data-grafico-id]`, não a página inteira).
    """
    return ui.tags.script(
        """
(function registrar() {
  if (window.Shiny && Shiny.setInputValue) {
    document.addEventListener("click", function(ev) {
      var botao = ev.target.closest(".barra-progresso-item");
      if (!botao) return;
      var lista = botao.closest("[data-grafico-id]");
      if (!lista) return;
      var idGrafico = lista.getAttribute("data-grafico-id");
      var valor = botao.getAttribute("data-valor");
      var jaSelecionada = botao.classList.contains("selecionada");
      lista.querySelectorAll(".barra-progresso-item.selecionada").forEach(function(b) {
        b.classList.remove("selecionada");
        b.setAttribute("aria-pressed", "false");
      });
      if (jaSelecionada) {
        Shiny.setInputValue(idGrafico + "_selecionado", null, {priority: "event"});
      } else {
        botao.classList.add("selecionada");
        botao.setAttribute("aria-pressed", "true");
        Shiny.setInputValue(idGrafico + "_selecionado", valor, {priority: "event"});
      }
    });
  } else {
    setTimeout(registrar, 50);
  }
})();
"""
    )


def barras_progresso(percentual_df, coluna_categoria: str, id: str, selecionavel: bool = False) -> ui.HTML:
    """Lista de barras de progresso (estilo "loading bar") -- alternativa
    visual às barras horizontais do Plotly (`graficos.grafico_percentual_horizontal`),
    usada na Visão Geral.

    `percentual_df` tem 2 colunas, `coluna_categoria` e "percentual" (ver
    `graficos.percentuais_por_categoria()`), já ordenado da maior pra
    menor; o preenchimento de cada barra é a largura literal do
    percentual (não escalado pelo maior valor, como fazia o eixo do
    Plotly).

    `selecionavel=True` (exige `id`) torna cada linha um `<button>` real
    -- ao contrário das barras do Plotly, que não são focáveis (ver
    limitação anotada em `plotly_html()`), estas são navegáveis e
    ativáveis por teclado de graça, por serem botões de verdade. O
    clique liga ao mesmo input reativo `<id>_selecionado` usado pelo
    crossfilter entre os gráficos da página (clique de novo na mesma
    barra desseleciona) -- tratado por `script_barra_progresso_clique()`
    (registrado uma vez no <head> do app), que também alterna a classe
    `selecionada`/`aria-pressed` do botão clicado. Isso não dá pra fazer
    reativamente a partir do Python porque esta mesma lista não se
    re-renderiza quando a PRÓPRIA seleção muda -- só quando a seleção do
    OUTRO gráfico da página invalida sua base de dados (mesmo
    comportamento do crossfilter via Plotly).
    """
    tag = "button" if selecionavel and id else "div"
    tipo_attr = ' type="button"' if tag == "button" else ""
    linhas_html = []
    for categoria, percentual in zip(percentual_df[coluna_categoria], percentual_df["percentual"]):
        categoria_escapada = html.escape(str(categoria))
        largura = max(0.0, min(100.0, float(percentual)))
        texto_percentual = f"{percentual:.2f}%".replace(".", ",")
        dados_attr = f' data-valor="{categoria_escapada}" aria-pressed="false"' if tag == "button" else ""
        linhas_html.append(
            f'<{tag}{tipo_attr} class="barra-progresso-item"{dados_attr}>'
            f'<span class="barra-progresso-rotulo">{categoria_escapada}</span>'
            f'<span class="barra-progresso-linha">'
            f'<span class="barra-progresso-trilha">'
            f'<span class="barra-progresso-preenchimento" style="width: {largura:.4f}%"></span>'
            f"</span>"
            f'<span class="barra-progresso-valor">{texto_percentual}</span>'
            f"</span>"
            f"</{tag}>"
        )
    id_attr = f' data-grafico-id="{id}"' if tag == "button" else ""
    return ui.HTML(f'<div class="barra-progresso-lista"{id_attr}>' + "".join(linhas_html) + "</div>")


def barras_progresso_acessivel(
    percentual_df, coluna_categoria: str, tabela_df, id: str, titulo: str, selecionavel: bool = False
) -> ui.Tag:
    """Como `grafico_acessivel()`, mas com `barras_progresso()` no lugar
    do gráfico Plotly (ver sua docstring para o detalhe do clique e do
    crossfilter). `tabela_df` é o que aparece na tabela alternável (pode
    trazer colunas diferentes de `percentual_df`, ex. valores em R$ em
    vez de percentual).
    """
    id_tabela = f"{id}__tabela"
    return ui.div(
        _botao_ver_tabela(id_tabela),
        ui.h3(titulo, class_="lista-cartao-titulo"),
        barras_progresso(percentual_df, coluna_categoria, id=id, selecionavel=selecionavel),
        _tabela_semantica(tabela_df, id_tabela, titulo),
        class_="grafico-acessivel",
    )


def plotly_head() -> ui.Tag:
    return ui.tags.script(src="https://cdn.plot.ly/plotly-2.35.2.min.js")


def escolhas_filtro(opcoes: list[str], placeholder_vazio: str = "Todas") -> dict[str, str]:
    """Monta o dict de `choices` de um `input_selectize`, com rótulo de texto
    na opção em branco (senão ela não aparece na lista de opções).
    """
    return {"": placeholder_vazio, **{o: o for o in opcoes}}


def filtro_selectize(
    id: str, label: str, opcoes: list[str], placeholder_vazio: str = "Todas", multiplo: bool = False
) -> ui.Tag:
    """Select com busca (`input_selectize` já busca nativamente, mas precisa
    de `placeholder` explícito para mostrar "Pesquisar" na caixa, como no
    site estático).

    `multiplo=True` permite selecionar mais de uma opção de uma vez --
    `input.<id>()` passa a devolver uma tupla (vazia quando nada está
    selecionado) em vez de uma string única, então todo código que lê
    esse filtro precisa comparar com `.isin(...)` em vez de `==`. Sem
    sentido ter uma opção em branco na lista nesse modo (não há "nada"
    pra selecionar explicitamente -- basta não marcar nenhuma).
    """
    return ui.input_selectize(
        id,
        label,
        choices={o: o for o in opcoes} if multiplo else escolhas_filtro(opcoes, placeholder_vazio),
        selected=[] if multiplo else "",
        multiple=multiplo,
        options={"placeholder": "Pesquisar"},
    )


def registrar_filtros_cruzados(
    input, df, filtros: list[tuple[str, str, str]], multiplo: bool = False
) -> None:
    """Registra o efeito "crossfilter" entre os filtros de uma página:
    selecionar uma opção em qualquer um deles restringe as opções
    disponíveis nos demais — e vice-versa, não importa por qual filtro o
    usuário começa (ex.: selecionar a UO 1271 faz a Ação Orçamentária só
    oferecer as ações daquela UO; selecionar antes a ação 1004 faz a UO só
    oferecer a UO 1511, dona daquela ação).

    `filtros` é uma lista de tuplas (id_do_input, nome_da_coluna,
    placeholder_quando_vazio), uma por filtro da página.

    `multiplo=True` trata cada filtro da lista como multi-seleção
    (`filtro_selectize(..., multiplo=True)`): a comparação vira
    `.isin(...)` em vez de `==`, e uma seleção que continue válida
    depois do crossfilter é preservada -- só as opções que deixaram de
    existir saem da seleção, em vez de a seleção inteira ser zerada.
    """

    @reactive.effect
    def _crossfilter():
        selecionados = {id_input: getattr(input, id_input)() for id_input, _, _ in filtros}
        for id_input, coluna, placeholder in filtros:
            subconjunto = df
            for outro_id, outra_coluna, _ in filtros:
                if outro_id == id_input:
                    continue
                valor = selecionados[outro_id]
                if valor:
                    if multiplo:
                        subconjunto = subconjunto[subconjunto[outra_coluna].isin(valor)]
                    else:
                        subconjunto = subconjunto[subconjunto[outra_coluna] == valor]
            validos = sorted(v for v in subconjunto[coluna].dropna().unique() if v != "")
            atual = selecionados[id_input]
            if multiplo:
                novo_selecionado = [v for v in atual if v in validos]
                novas_escolhas = {o: o for o in validos}
            else:
                novo_selecionado = atual if atual in validos else ""
                novas_escolhas = escolhas_filtro(validos, placeholder)
            ui.update_selectize(id_input, choices=novas_escolhas, selected=novo_selecionado)


def estilo_moeda(df, *colunas: str) -> list[dict]:
    """Alinha à direita e deixa em negrito as colunas de valor monetário
    (R$) de uma tabela `render.DataGrid`, no mesmo padrão do site estático
    (onde a última coluna — ou as duas últimas, na Regionalização — de
    valor numérico é alinhada à direita).
    """
    indices = [df.columns.get_loc(c) for c in colunas if c in df.columns]
    if not indices:
        return []
    return [{"cols": indices, "style": {"text-align": "right", "font-weight": "600"}}]


def botoes_exportar(id_csv: str, id_xlsx: str) -> ui.Tag:
    return ui.div(
        ui.download_button(id_csv, "Exportar CSV", class_="botao-exportar"),
        ui.download_button(id_xlsx, "Exportar Excel", class_="botao-exportar"),
        class_="tabela-exportar",
    )


def botao_limpar_filtros(id: str) -> ui.Tag:
    """Botão "Limpar filtros" com o mesmo visual do site estático
    (`.botao-secundario`): borda sutil, fundo branco, texto em negrito.
    """
    return ui.input_action_button(id, "Limpar filtros", class_="botao-limpar-filtros")


def card_kpi(
    titulo: str, valor: str, icone: str | None = "coins", compacto: bool = False
) -> ui.Tag:
    """Card de KPI com borda de destaque à esquerda (azul institucional)
    e número grande, no padrão aprovado na maquete "Painel Lateral" --
    sem o fundo azul sólido da versão original, para melhor contraste em
    qualquer combinação de cores dentro do card.
    """
    classes = "card-kpi" + (" card-kpi--compacto" if compacto else "")
    return ui.div(
        ui.span(valor, class_="valor"),
        ui.span(titulo, class_="titulo"),
        class_=classes,
    )
