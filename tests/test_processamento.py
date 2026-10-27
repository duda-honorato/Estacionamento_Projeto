import cv2
import numpy as np

from estacionamento.processamento import (
    Parametros,
    analisar_componentes,
    aplicar_morfologia,
    colorir_componentes,
    preprocessar,
    processar_vaga,
    segmentar_bordas,
)


def criar_vaga_livre() -> np.ndarray:
    """Simula uma vaga vazia com asfalto plano (homogêneo)."""
    return np.full((60, 50, 3), 90, dtype=np.uint8)


def criar_vaga_ocupada() -> np.ndarray:
    """Simula uma vaga com um carro (contraste acentuado e múltiplas bordas)."""
    roi = criar_vaga_livre()
    cv2.rectangle(roi, (12, 8), (38, 52), (220, 220, 220), -1)
    cv2.rectangle(roi, (16, 16), (34, 26), (30, 30, 30), -1)
    return roi


def test_preprocessar_converte_cinza_e_suaviza() -> None:
    roi = criar_vaga_ocupada()
    parametros = Parametros(blur=5, usar_clahe=False)

    cinza, suavizada = preprocessar(roi, parametros)

    assert cinza.ndim == 2
    assert cinza.shape == roi.shape[:2]
    assert suavizada.shape == roi.shape[:2]
    assert cinza.dtype == np.uint8
    assert suavizada.dtype == np.uint8


def test_preprocessar_com_clahe() -> None:
    roi = criar_vaga_ocupada()
    p_sem = Parametros(usar_clahe=False)
    p_com = Parametros(usar_clahe=True)

    cinza_sem, _ = preprocessar(roi, p_sem)
    cinza_com, _ = preprocessar(roi, p_com)

    # CLAHE altera a distribuição dos níveis de cinza
    assert not np.array_equal(cinza_sem, cinza_com)


def test_segmentar_bordas_retorna_mascara_binaria() -> None:
    roi = criar_vaga_ocupada()
    _, suavizada = preprocessar(roi, Parametros())
    bordas = segmentar_bordas(suavizada, Parametros())

    assert bordas.shape == roi.shape[:2]
    assert bordas.dtype == np.uint8
    valores_unicos = set(np.unique(bordas))
    assert valores_unicos.issubset({0, 255})
    assert 255 in valores_unicos  # Deve conter bordas detectadas


def test_vaga_livre_nao_tem_bordas() -> None:
    resultado = processar_vaga(criar_vaga_livre(), Parametros())

    assert resultado.caracteristicas["densidade_bordas"] == 0.0
    assert resultado.caracteristicas["area_mascara"] == 0.0
    assert resultado.caracteristicas["num_componentes"] == 0.0
    assert resultado.caracteristicas["desvio_padrao"] == 0.0


def test_vaga_ocupada_tem_mais_bordas_que_livre() -> None:
    livre = processar_vaga(criar_vaga_livre(), Parametros())
    ocupada = processar_vaga(criar_vaga_ocupada(), Parametros())

    for atributo in ("desvio_padrao", "densidade_bordas", "area_mascara"):
        assert ocupada.caracteristicas[atributo] > livre.caracteristicas[atributo]


def test_caracteristicas_de_fracao_ficam_entre_0_e_1() -> None:
    resultado = processar_vaga(criar_vaga_ocupada(), Parametros())

    for atributo in ("densidade_bordas", "area_mascara", "maior_componente"):
        assert 0.0 <= resultado.caracteristicas[atributo] <= 1.0


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


def test_fechamento_conecta_linhas_proximas() -> None:
    mascara = np.zeros((40, 40), dtype=np.uint8)
    # Duas linhas paralelas separadas por 2 pixels
    mascara[10:30, 15] = 255
    mascara[10:30, 18] = 255

    # Fechamento com kernel 5x5 deve unir as duas linhas
    processada = aplicar_morfologia(mascara, Parametros(kernel_fechamento=5, kernel_abertura=1))
    # Na região intermediária entre colunas 15 e 18 deve haver pixels preenchidos
    assert np.any(processada[15:25, 16:18] == 255)


def test_componentes_pequenos_sao_descartados() -> None:
    mascara = np.zeros((40, 40), dtype=np.uint8)
    mascara[5:15, 5:15] = 255     # Área = 100 px (válido)
    mascara[30:32, 30:32] = 255   # Área = 4 px (pequeno, deve ser descartado)

    quantidade, maior_area, rotulos = analisar_componentes(mascara, area_minima=20)

    assert quantidade == 1
    assert maior_area == 100
    assert rotulos[30, 30] == 0  # O componente pequeno foi zerado
    assert rotulos[10, 10] > 0   # O componente grande permanece rotulado


def test_colorir_componentes_fundo_preto() -> None:
    rotulos = np.zeros((20, 20), dtype=np.int32)
    rotulos[5:15, 5:15] = 1

    colorida = colorir_componentes(rotulos)

    assert colorida.shape == (20, 20, 3)
    assert colorida.dtype == np.uint8
    # Fundo (rotulo 0) deve ser preto
    assert np.all(colorida[0, 0] == [0, 0, 0])
    # Componente 1 deve ter cor visível (não preta)
    assert np.any(colorida[10, 10] > 0)


def test_intermediarias_tem_mesmo_tamanho_da_roi() -> None:
    roi = criar_vaga_ocupada()
    resultado = processar_vaga(roi, Parametros())

    chaves_esperadas = {"roi", "cinza", "bordas", "morfologia", "componentes"}
    assert set(resultado.intermediarias.keys()) == chaves_esperadas

    for chave, imagem in resultado.intermediarias.items():
        assert imagem.shape[:2] == roi.shape[:2], f"Dimensão incorreta em {chave}"
