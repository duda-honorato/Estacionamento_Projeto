import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from estacionamento.delimitador_vagas import (
    carregar_anotacoes,
    extrair_regioes_interesse,
    gerar_imagem_delimitada,
    salvar_anotacoes,
    salvar_resultados,
    selecionar_vagas_manualmente,
)


@pytest.fixture
def imagem_teste() -> np.ndarray:
    """Cria uma imagem sintética 200x300 BGR com padrões para teste."""
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    img[20:100, 30:110] = (100, 150, 200)
    img[20:100, 150:230] = (50, 80, 120)
    return img


@pytest.fixture
def vagas_teste() -> list[dict]:
    return [
        {"id": "vaga_01", "x": 30, "y": 20, "largura": 80, "altura": 80},
        {"id": "vaga_02", "x": 150, "y": 20, "largura": 80, "altura": 80},
    ]


def test_salvar_e_carregar_anotacoes(tmp_path: Path, vagas_teste: list[dict]) -> None:
    caminho = tmp_path / "anotacoes.json"
    salvar_anotacoes(vagas_teste, caminho, "ref.png")

    assert caminho.is_file()

    with caminho.open("r", encoding="utf-8") as f:
        dados = json.load(f)
        assert dados["imagem_referencia"] == "ref.png"
        assert len(dados["vagas"]) == 2

    carregadas = carregar_anotacoes(caminho)
    assert carregadas == vagas_teste


def test_carregar_anotacoes_arquivo_inexistente(tmp_path: Path) -> None:
    caminho = tmp_path / "nao_existe.json"
    with pytest.raises(FileNotFoundError):
        carregar_anotacoes(caminho)


def test_extrair_regioes_interesse(imagem_teste: np.ndarray, vagas_teste: list[dict]) -> None:
    regioes = extrair_regioes_interesse(imagem_teste, vagas_teste)

    assert set(regioes.keys()) == {"vaga_01", "vaga_02"}
    assert regioes["vaga_01"].shape == (80, 80, 3)
    assert regioes["vaga_02"].shape == (80, 80, 3)
    # Verifica que o conteúdo recortado bate com a região esperada
    assert np.array_equal(regioes["vaga_01"], imagem_teste[20:100, 30:110])


def test_extrair_regioes_interesse_fora_dos_limites(imagem_teste: np.ndarray) -> None:
    # Imagem tem 200 de altura e 300 de largura
    vaga_invalida = [{"id": "vaga_fora", "x": 250, "y": 100, "largura": 80, "altura": 50}]
    with pytest.raises(ValueError, match="Coordenadas inválidas"):
        extrair_regioes_interesse(imagem_teste, vaga_invalida)


def test_extrair_regioes_interesse_coordenadas_negativas(imagem_teste: np.ndarray) -> None:
    vaga_negativa = [{"id": "vaga_neg", "x": -10, "y": 20, "largura": 50, "altura": 50}]
    with pytest.raises(ValueError, match="Coordenadas inválidas"):
        extrair_regioes_interesse(imagem_teste, vaga_negativa)


def test_extrair_regioes_interesse_dimensao_invalida(imagem_teste: np.ndarray) -> None:
    vaga_zero = [{"id": "vaga_zero", "x": 10, "y": 10, "largura": 0, "altura": 50}]
    with pytest.raises(ValueError, match="Coordenadas inválidas"):
        extrair_regioes_interesse(imagem_teste, vaga_zero)


def test_gerar_imagem_delimitada(imagem_teste: np.ndarray, vagas_teste: list[dict]) -> None:
    delimitada = gerar_imagem_delimitada(imagem_teste, vagas_teste)

    assert delimitada.shape == imagem_teste.shape
    assert delimitada.dtype == imagem_teste.dtype
    # Como foram desenhados retângulos verdes e textos, a imagem deve ser diferente da original
    assert not np.array_equal(delimitada, imagem_teste)


def test_salvar_resultados(tmp_path: Path, imagem_teste: np.ndarray, vagas_teste: list[dict]) -> None:
    pasta_saida = tmp_path / "recortes"
    salvar_resultados(imagem_teste, vagas_teste, pasta_saida, "teste_img")

    assert (pasta_saida / "teste_img_delimitada.png").is_file()
    assert (pasta_saida / "teste_img_vaga_01.png").is_file()
    assert (pasta_saida / "teste_img_vaga_02.png").is_file()


def test_selecionar_vagas_quantidade_invalida(imagem_teste: np.ndarray) -> None:
    with pytest.raises(ValueError, match="maior que zero"):
        selecionar_vagas_manualmente(imagem_teste, 0)
