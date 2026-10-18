
from pathlib import Path

import cv2
import numpy as np


def carregar_imagem(caminho_imagem: str | Path) -> np.ndarray:
    arquivo_imagem = Path(caminho_imagem)

    if not arquivo_imagem.is_file():
        raise FileNotFoundError(
            f"O arquivo de imagem não foi encontrado: {arquivo_imagem}"
        )

    imagem_carregada = cv2.imread(
        str(arquivo_imagem),
        cv2.IMREAD_COLOR
    )

    if imagem_carregada is None:
        raise ValueError(
            f"Não foi possível carregar a imagem: {arquivo_imagem}"
        )

    return imagem_carregada


def obter_dimensoes_imagem(imagem: np.ndarray) -> tuple[int, int, int]:
    if imagem is None or imagem.ndim != 3:
        raise ValueError(
            "A imagem deve possuir três dimensões: altura, largura e canais."
        )

    altura_imagem, largura_imagem, quantidade_canais = imagem.shape

    return largura_imagem, altura_imagem, quantidade_canais
