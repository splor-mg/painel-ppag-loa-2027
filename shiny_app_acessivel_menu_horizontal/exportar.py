"""Exportação de tabelas (CSV/Excel), com a mesma sanitização contra
injeção de fórmula usada no site estático — ver docs/premissas.md.
"""

import io

import pandas as pd

_CARACTERES_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def _neutralizar_formula(valor):
    if isinstance(valor, str) and valor.startswith(_CARACTERES_FORMULA):
        return f"'{valor}"
    return valor


def _sanitizar(tabela: pd.DataFrame) -> pd.DataFrame:
    return tabela.map(_neutralizar_formula)


def csv_bytes(tabela: pd.DataFrame) -> bytes:
    return _sanitizar(tabela).to_csv(index=False, sep=";").encode("utf-8-sig")


def xlsx_bytes(tabela: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    _sanitizar(tabela).to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()
