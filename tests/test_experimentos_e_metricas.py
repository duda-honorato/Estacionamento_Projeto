import pytest

from estacionamento.experimentos import (
    avaliar,
    melhor_limiar as melhor_limiar_exp,
    metricas as metricas_exp,
)
from interface import (
    calcular_metricas,
    contar_matriz,
    converter_limiar,
    dividir,
    melhor_limiar as melhor_limiar_interface,
    tabela,
)


def test_converter_limiar_valores_validos() -> None:
    assert converter_limiar("0.076") == 0.076
    assert converter_limiar("0,076") == 0.076
    assert converter_limiar("  0.15  ") == 0.15
    assert converter_limiar("1") == 1.0


def test_converter_limiar_vazio_retorna_none() -> None:
    assert converter_limiar("") is None
    assert converter_limiar("   ") is None


def test_dividir_zero_retorna_none() -> None:
    assert dividir(10, 0) is None
    assert dividir(10, 2) == 5.0


def test_contar_matriz_calculo_correto() -> None:
    # 1 = ocupada, 0 = livre
    referencias = [1, 1, 0, 0, 1]
    previstas = [1, 0, 0, 1, 1]

    # Par (1, 1): VP (2)
    # Par (1, 0): FN (1)
    # Par (0, 0): VN (1)
    # Par (0, 1): FP (1)
    matriz = contar_matriz(referencias, previstas)

    assert matriz["VP"] == 2
    assert matriz["FN"] == 1
    assert matriz["VN"] == 1
    assert matriz["FP"] == 1


def test_calcular_metricas_interface() -> None:
    matriz = {"VP": 6, "FP": 0, "FN": 1, "VN": 23}
    m = calcular_metricas(matriz)

    assert pytest.approx(m["Acurácia"], 0.001) == 29 / 30
    assert pytest.approx(m["Precisão"], 0.001) == 1.0
    assert pytest.approx(m["Revocação"], 0.001) == 6 / 7
    assert pytest.approx(m["Especificidade"], 0.001) == 1.0
    assert pytest.approx(m["F1"], 0.001) == 2 * (1.0 * (6 / 7)) / (1.0 + (6 / 7))


def test_calcular_metricas_sem_positivos() -> None:
    matriz = {"VP": 0, "FP": 0, "FN": 0, "VN": 10}
    m = calcular_metricas(matriz)

    assert m["Precisão"] is None
    assert m["Revocação"] is None
    assert m["F1"] is None
    assert m["Acurácia"] == 1.0


def test_melhor_limiar_exp_e_interface() -> None:
    # Livres com valores baixos, Ocupadas com valores altos
    valores = [0.01, 0.02, 0.03, 0.08, 0.09, 0.10]
    referencias = [0, 0, 0, 1, 1, 1]

    limiar_exp = melhor_limiar_exp(valores, referencias)
    assert 0.03 < limiar_exp <= 0.08

    limiar_int, acertos = melhor_limiar_interface(valores, referencias)
    assert acertos == 6
    assert 0.03 < limiar_int <= 0.08


def test_metricas_exp() -> None:
    referencias = [1, 1, 0, 0]
    previstas = [1, 1, 0, 0]

    resultado = metricas_exp(referencias, previstas)
    assert resultado["acuracia"] == 1.0
    assert resultado["f1"] == 1.0
    assert resultado["erros"] == 0


def test_avaliar_exp_com_loio() -> None:
    linhas = [
        {"imagem": "img1.png", "vaga_id": "v1", "ocupada": 0, "densidade": 0.01},
        {"imagem": "img1.png", "vaga_id": "v2", "ocupada": 1, "densidade": 0.09},
        {"imagem": "img2.png", "vaga_id": "v1", "ocupada": 0, "densidade": 0.02},
        {"imagem": "img2.png", "vaga_id": "v2", "ocupada": 1, "densidade": 0.10},
    ]

    resultado = avaliar(linhas, "densidade")

    assert resultado["acuracia"] == 1.0
    assert resultado["erros"] == 0
    assert resultado["loio_acuracia"] == 1.0
    assert resultado["media_livres"] == pytest.approx(0.015)
    assert resultado["media_ocupadas"] == pytest.approx(0.095)


def test_formatar_tabela_interface() -> None:
    texto = tabela(
        ["Coluna 1", "Coluna 2"],
        [["A", "B"], ["C", "D"]],
        "Título da Tabela"
    )

    assert "Título da Tabela" in texto
    assert "| Coluna 1 | Coluna 2 |" in texto
    assert "| A        | B        |" in texto
