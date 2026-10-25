from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class Parametros:

    blur: int = 5
    canny_min: int = 50
    canny_max: int = 150
    usar_clahe: bool = False
    usar_morfologia: bool = True
    kernel_fechamento: int = 5
    kernel_abertura: int = 3
    area_minima_componente: int = 20


@dataclass
class ResultadoVaga:
    caracteristicas: dict[str, float]
    intermediarias: dict[str, np.ndarray] = field(default_factory=dict)


def preprocessar(
    roi: np.ndarray,
    parametros: Parametros
) -> tuple[np.ndarray, np.ndarray]:
  
    cinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    if parametros.usar_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        cinza = clahe.apply(cinza)

    suavizada = cv2.GaussianBlur(
        cinza,
        (parametros.blur, parametros.blur),
        0
    )

    return cinza, suavizada


def segmentar_bordas(
    suavizada: np.ndarray,
    parametros: Parametros
) -> np.ndarray:
    return cv2.Canny(
        suavizada,
        parametros.canny_min,
        parametros.canny_max
    )


def aplicar_morfologia(
    mascara: np.ndarray,
    parametros: Parametros
) -> np.ndarray:
    
    if not parametros.usar_morfologia:
        return mascara.copy()

    kernel_fechamento = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (parametros.kernel_fechamento, parametros.kernel_fechamento)
    )
    kernel_abertura = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (parametros.kernel_abertura, parametros.kernel_abertura)
    )

    fechada = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel_fechamento)
    aberta = cv2.morphologyEx(fechada, cv2.MORPH_OPEN, kernel_abertura)

    return aberta


def analisar_componentes(
    mascara: np.ndarray,
    area_minima: int
) -> tuple[int, int, np.ndarray]:
 
    quantidade, rotulos, estatisticas, _ = cv2.connectedComponentsWithStats(
        mascara,
        connectivity=8
    )

    rotulos_validos = np.zeros_like(rotulos)
    areas_validas = []

    for rotulo in range(1, quantidade):
        area = int(estatisticas[rotulo, cv2.CC_STAT_AREA])

        if area >= area_minima:
            areas_validas.append(area)
            rotulos_validos[rotulos == rotulo] = len(areas_validas)

    maior_area = max(areas_validas, default=0)

    return len(areas_validas), maior_area, rotulos_validos


def colorir_componentes(rotulos: np.ndarray) -> np.ndarray:
    """Gera uma imagem colorida com uma cor por componente (fundo preto)."""
    gerador = np.random.default_rng(0)
    cores = gerador.integers(60, 256, size=(int(rotulos.max()) + 1, 3))
    cores[0] = 0

    return cores[rotulos].astype(np.uint8)


def processar_vaga(
    roi: np.ndarray,
    parametros: Parametros
) -> ResultadoVaga:
    """Executa o fluxo completo em uma vaga e calcula as características."""
    cinza, suavizada = preprocessar(roi, parametros)
    bordas = segmentar_bordas(suavizada, parametros)
    mascara = aplicar_morfologia(bordas, parametros)

    quantidade, maior_area, rotulos = analisar_componentes(
        mascara,
        parametros.area_minima_componente
    )

    area_roi = mascara.size 

    caracteristicas = {
        "desvio_padrao": float(np.std(cinza)),
        "densidade_bordas": float(np.count_nonzero(bordas) / area_roi),
        "area_mascara": float(np.count_nonzero(mascara) / area_roi),
        "maior_componente": float(maior_area / area_roi),
        "num_componentes": float(quantidade),
    }

    intermediarias = {
        "roi": roi,
        "cinza": cinza,
        "bordas": bordas,
        "morfologia": mascara,
        "componentes": colorir_componentes(rotulos),
    }

    return ResultadoVaga(caracteristicas, intermediarias)
