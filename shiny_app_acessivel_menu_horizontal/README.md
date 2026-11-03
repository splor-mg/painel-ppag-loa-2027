# Painel PPAG-LOA 2027 — versão Shiny for Python + Shinylive (acessível, menu horizontal)

Cópia de `../shiny_app_acessivel/` (mesmos dados, mesma lógica reativa,
mesmos componentes) criada **só** para comparar a disposição do menu de
navegação lado a lado: aqui ele fica horizontal, logo abaixo do título
(`ui.navset_pill`), em vez de lateral (`ui.navset_pill_list`) — essa é a
única diferença entre os dois painéis. Depois da comparação, uma das duas
variantes deve virar a final e a outra ser removida; até lá, veja
`../shiny_app_acessivel/README.md` para o resto da arquitetura (idêntica).

## Rodar localmente

Pré-requisito: ambiente Poetry da raiz do repositório instalado
(`poetry install`, a partir da raiz).

```sh
# a partir da raiz do repositorio
poetry run python gerar_dados_shiny.py   # gera/atualiza shiny_app_acessivel/data
# copiar shiny_app_acessivel/data/ pra cá (data/) se os dados mudaram -- ver docstring de gerar_dados_shiny.py
poetry run shiny run shiny_app_acessivel_menu_horizontal/app.py
poetry run shinylive export shiny_app_acessivel_menu_horizontal dist_shiny_acessivel_menu_horizontal
python -m http.server --directory dist_shiny_acessivel_menu_horizontal --bind localhost 8008
```

## Publicar

O `dist_shiny_acessivel_menu_horizontal/` gerado é copiado para a branch
`gh-pages`, na pasta `shiny-acessivel-menu-horizontal/` (sem mexer no
resto do site):

```sh
poetry run shinylive export shiny_app_acessivel_menu_horizontal dist_shiny_acessivel_menu_horizontal
# copiar o conteudo de dist_shiny_acessivel_menu_horizontal/ para gh-pages:/shiny-acessivel-menu-horizontal/, commitar, dar push
```

Publicado em:
https://vivigoncalvesportonascimento.github.io/painel-ppag-loa-2027/shiny-acessivel-menu-horizontal/
