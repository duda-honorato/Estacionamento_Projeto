import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from estacionamento.pipeline import (
    carregar_rotulos,
    desenhar_classificacao,
    executar_pipeline,
    montar_painel,
    montar_parametros,
    salvar_imagem,
)
from estacionamento.processamento import Parametros


def test_montar_parametros_validos() -> None:
    args = argparse.Namespace(
        blur=7,
        canny_min=40,
        canny_max=120,
        clahe=True,
        sem_morfologia=False,
        kernel_fechamento=5,
        kernel_abertura=3,
        area_minima=25,
    )
    params = montar_parametros(args)

    assert params.blur == 7
    assert params.canny_min == 40
    assert params.canny_max == 120
    assert params.usar_clahe is True
    assert params.usar_morfologia is True
    assert params.area_minima_componente == 25


def test_montar_parametros_blur_par_gera_erro() -> None:
    args = argparse.Namespace(
        blur=6,  # Par: inválido para filtro gaussiano
        canny_min=50,
        canny_max=150,
        clahe=False,
        sem_morfologia=False,
        kernel_fechamento=5,
        kernel_abertura=3,
        area_minima=20,
    )
    with pytest.raises(ValueError, match="precisa ser ímpar"):
        montar_parametros(args)


def test_carregar_rotulos_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "rotulos.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["imagem", "vaga_id", "ocupada"])
        writer.writerow(["0.png", "vaga_01", "1"])
        writer.writerow(["0.png", "vaga_02", "0"])

    rotulos = carregar_rotulos(csv_path)

    assert rotulos[("0.png", "vaga_01")] == 1
    assert rotulos[("0.png", "vaga_02")] == 0


def test_carregar_rotulos_nulo() -> None:
    assert carregar_rotulos(None) == {}


def test_montar_painel() -> None:
    roi = np.full((30, 20, 3), 100, dtype=np.uint8)
    cinza = np.full((30, 20), 100, dtype=np.uint8)
    intermediarias = {"roi": roi, "cinza": cinza}

    painel = montar_painel(intermediarias, escala=2)

    assert isinstance(painel, np.ndarray)
    assert painel.ndim == 3
    assert painel.shape[2] == 3
    # A largura deve ser a soma das larguras ampliadas + separador
    assert painel.shape[1] > 20 * 2


def test_desenhar_classificacao() -> None:
    imagem = np.zeros((100, 100, 3), dtype=np.uint8)
    vagas = [
        {"id": "vaga_01", "x": 10, "y": 10, "largura": 30, "altura": 30},
        {"id": "vaga_02", "x": 50, "y": 10, "largura": 30, "altura": 30},
    ]
    previsoes = {"vaga_01": 0, "vaga_02": 1}

    classificada = desenhar_classificacao(imagem, vagas, previsoes)

    assert classificada.shape == imagem.shape
    # Não pode ser toda preta, pois retângulos e textos foram adicionados
    assert np.any(classificada > 0)


def test_salvar_imagem(tmp_path: Path) -> None:
    caminho = tmp_path / "saida.png"
    img = np.ones((50, 50, 3), dtype=np.uint8) * 200

    salvar_imagem(caminho, img)
    assert caminho.is_file()


def test_executar_pipeline_end_to_end(tmp_path: Path) -> None:
    pasta_input = tmp_path / "input"
    pasta_input.mkdir()

    # Imagem de teste
    img = np.full((120, 120, 3), 80, dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (80, 80), (240, 240, 240), -1)
    cv2.imwrite(str(pasta_input / "0.png"), img)

    # Anotações de vagas
    arquivo_vagas = tmp_path / "vagas.json"
    dados_vagas = {
        "imagem_referencia": "0.png",
        "vagas": [
            {"id": "vaga_01", "x": 10, "y": 10, "largura": 90, "altura": 90}
        ]
    }
    arquivo_vagas.write_text(json.dumps(dados_vagas), encoding="utf-8")

    # Rótulo de teste
    arquivo_rotulos = tmp_path / "rotulos.csv"
    arquivo_rotulos.write_text("imagem,vaga_id,ocupada\n0.png,vaga_01,1\n", encoding="utf-8")

    pasta_output = tmp_path / "results"

    padrao = Parametros()
    args = argparse.Namespace(
        input=pasta_input,
        annotations=arquivo_vagas,
        output=pasta_output,
        labels=arquivo_rotulos,
        blur=padrao.blur,
        canny_min=padrao.canny_min,
        canny_max=padrao.canny_max,
        clahe=False,
        sem_morfologia=False,
        kernel_fechamento=padrao.kernel_fechamento,
        kernel_abertura=padrao.kernel_abertura,
        area_minima=padrao.area_minima_componente,
        atributo="densidade_bordas",
        limiar=0.05,
    )

    executar_pipeline(args)

    assert (pasta_output / "caracteristicas.csv").is_file()
    assert (pasta_output / "parametros.json").is_file()
    assert (pasta_output / "0_classificada.png").is_file()
    assert (pasta_output / "intermediarias" / "0_vaga_01_etapas.png").is_file()

    with (pasta_output / "caracteristicas.csv").open("r", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
        assert len(linhas) == 1
        assert linhas[0]["imagem"] == "0.png"
        assert linhas[0]["vaga_id"] == "vaga_01"
        assert linhas[0]["ocupada_referencia"] == "1"
        assert "densidade_bordas" in linhas[0]
        assert "ocupada_prevista" in linhas[0]
