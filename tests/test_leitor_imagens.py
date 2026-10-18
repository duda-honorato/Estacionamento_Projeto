
from pathlib import Path

import cv2
import numpy as np
import pytest

from estacionamento.leitor_imagens import (
    carregar_imagem,
    obter_dimensoes_imagem,
)


def test_carregar_imagem_valida(tmp_path: Path) -> None:
    caminho_imagem = tmp_path / "imagem_valida.png"

    imagem_original = np.zeros(
        (100, 200, 3),
        dtype=np.uint8
    )

    imagem_salva = cv2.imwrite(
        str(caminho_imagem),
        imagem_original
    )

    assert imagem_salva is True

    imagem_carregada = carregar_imagem(caminho_imagem)

    assert isinstance(imagem_carregada, np.ndarray)
    assert imagem_carregada.shape == (100, 200, 3)
    assert np.array_equal(imagem_carregada, imagem_original)


def test_carregar_imagem_inexistente(tmp_path: Path) -> None:
    caminho_imagem = tmp_path / "imagem_inexistente.png"

    with pytest.raises(FileNotFoundError):
        carregar_imagem(caminho_imagem)


def test_carregar_arquivo_invalido(tmp_path: Path) -> None:
    caminho_arquivo = tmp_path / "arquivo_invalido.png"

    caminho_arquivo.write_text(
        "Este arquivo não contém uma imagem válida.",
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        carregar_imagem(caminho_arquivo)


def test_obter_dimensoes_imagem_colorida() -> None:
    imagem = np.zeros(
        (1080, 1920, 3),
        dtype=np.uint8
    )

    largura, altura, quantidade_canais = obter_dimensoes_imagem(
        imagem
    )

    assert largura == 1920
    assert altura == 1080
    assert quantidade_canais == 3


def test_obter_dimensoes_imagem_invalida() -> None:
    imagem_invalida = np.zeros(
        (100, 200),
        dtype=np.uint8
    )

    with pytest.raises(ValueError):
        obter_dimensoes_imagem(imagem_invalida)


def test_obter_dimensoes_imagem_nula() -> None:
    with pytest.raises(ValueError):
        obter_dimensoes_imagem(None)
