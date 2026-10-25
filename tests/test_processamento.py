import cv2
import numpy as np

from estacionamento.processamento import (
    Parametros,
    analisar_componentes,
    aplicar_morfologia,
    processar_vaga,
)


def criar_vaga_livre() -> np.ndarray:
    return np.full((60, 50, 3), 90, dtype=np.uint8)


def criar_vaga_ocupada() -> np.ndarray:
    roi = criar_vaga_livre()
    cv2.rectangle(roi, (12, 8), (38, 52), (220, 220, 220), -1)
    cv2.rectangle(roi, (16, 16), (34, 26), (30, 30, 30), -1)
    return roi


def test_vaga_livre_nao_tem_bordas() -> None:
    resultado = processar_vaga(criar_vaga_livre(), Parametros())

    assert resultado.caracteristicas["densidade_bordas"] == 0
    assert resultado.caracteristicas["area_mascara"] == 0
    assert resultado.caracteristicas["num_componentes"] == 0


def test_vaga_ocupada_tem_mais_bordas_que_livre() -> None:
    livre = processar_vaga(criar_vaga_livre(), Parametros())
    ocupada = processar_vaga(criar_vaga_ocupada(), Parametros())

    for atributo in ("desvio_padrao", "densidade_bordas", "area_mascara"):
        assert ocupada.caracteristicas[atributo] > livre.caracteristicas[atributo]


def test_caracteristicas_de_fracao_ficam_entre_0_e_1() -> None:
    resultado = processar_vaga(criar_vaga_ocupada(), Parametros())

    for atributo in ("densidade_bordas", "area_mascara", "maior_componente"):
        assert 0 <= resultado.caracteristicas[atributo] <= 1


def test_abertura_remove_ponto_isolado() -> None:
    mascara = np.zeros((30, 30), dtype=np.uint8)
    mascara[15, 15] = 255  # ruído de 1 pixel

    limpa = aplicar_morfologia(mascara, Parametros())

    assert np.count_nonzero(limpa) == 0


def test_sem_morfologia_mantem_mascara() -> None:
    mascara = np.zeros((30, 30), dtype=np.uint8)
    mascara[15, 15] = 255

    resultado = aplicar_morfologia(mascara, Parametros(usar_morfologia=False))

    assert np.array_equal(resultado, mascara)


def test_componentes_pequenos_sao_descartados() -> None:
    mascara = np.zeros((40, 40), dtype=np.uint8)
    mascara[5:15, 5:15] = 255   
    mascara[30:32, 30:32] = 255  

    quantidade, maior_area, _ = analisar_componentes(mascara, area_minima=20)

    assert quantidade == 1
    assert maior_area == 100


def test_intermediarias_tem_mesmo_tamanho_da_roi() -> None:
    roi = criar_vaga_ocupada()
    resultado = processar_vaga(roi, Parametros())

    for imagem in resultado.intermediarias.values():
        assert imagem.shape[:2] == roi.shape[:2]
