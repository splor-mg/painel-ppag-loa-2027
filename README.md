# painel-ppag-loa-2027

Painel PPAG-LOA 2027 (Shiny for Python + Shinylive).

- **Painel publicado:** https://splor-mg.github.io/painel-ppag-loa-2027/
- Código: [shiny_app_acessivel_menu_horizontal/](shiny_app_acessivel_menu_horizontal/) (versão oficial, menu horizontal)
- Variante com menu lateral: [shiny_app_acessivel/](shiny_app_acessivel/) (publicada em `/shiny-acessivel/`)
- Dados: `data/`, `auxiliares/`, `etl/`; geração dos dados do painel em `gerar_dados_shiny.py`.

Para rodar localmente: `poetry install` e depois
`poetry run shiny run shiny_app_acessivel_menu_horizontal/app.py`.
