"""
Se vcs mudarem sem querer um parâmetro no código ou na interface, esse teste quebra. O professor nos orientou:
N adicionar funcionalidades de interface que não contribuam para a avaliação.
"""

import json
from dataclasses import asdict
from pathlib import Path

from estacionamento.pipeline import ATRIBUTOS
from estacionamento.processamento import Parametros

CAMINHO = Path(__file__).resolve().parent.parent / "config" / "baseline_congelado.json"


def carregar():
    with CAMINHO.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def test_parametros_padrao_iguais_ao_baseline_congelado():
    assert asdict(Parametros()) == carregar()["parametros"]


def test_atributo_do_baseline_existe():
    assert carregar()["classificador"]["atributo"] in ATRIBUTOS


def test_limiar_padrao_da_interface_igual_ao_baseline():
    from interface import PADROES
    limiar = float(PADROES["limiar"].replace(",", "."))
    assert limiar == carregar()["classificador"]["limiar_m2"]
