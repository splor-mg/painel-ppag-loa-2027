# Painel PPAG-LOA 2027 — Shiny for Python + Shinylive (acessível, menu horizontal)

Versão oficial do painel: navegação por menu horizontal (`ui.navset_pill`)
logo abaixo do título. A arquitetura (dados, lógica reativa, componentes)
é a mesma descrita em `../shiny_app_acessivel/README.md`, que mantém a
variante com menu lateral.

## Rodar localmente

Pré-requisito: ambiente Poetry da raiz do repositório instalado
(`poetry install`, a partir da raiz).

```sh
# a partir da raiz do repositorio
poetry run python gerar_dados_shiny.py   # gera/atualiza shiny_app_acessivel/data
# copiar shiny_app_acessivel/data/ pra cá (data/) se os dados mudaram -- ver docstring de gerar_dados_shiny.py
poetry run shiny run shiny_app_acessivel_menu_horizontal/app.py
```

## Publicar

O export é copiado para a **raiz** da branch `gh-pages` (preservando
`.nojekyll` e a pasta `shiny-acessivel/`):

```sh
poetry run shinylive export shiny_app_acessivel_menu_horizontal dist_shiny_acessivel_menu_horizontal
# na gh-pages: apagar index.html, app.json, edit/, shinylive/, shinylive-sw.js;
# copiar o conteudo de dist_shiny_acessivel_menu_horizontal/ para a raiz; commitar; dar push
```

Publicado em: https://splor-mg.github.io/painel-ppag-loa-2027/
(requer GitHub Pages ativado: Settings → Pages → branch `gh-pages`, pasta `/`).
