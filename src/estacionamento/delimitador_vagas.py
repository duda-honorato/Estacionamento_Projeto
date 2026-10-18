
import json
from pathlib import Path

import cv2
import numpy as np


def selecionar_vagas_manualmente(
    imagem: np.ndarray,
    quantidade_vagas: int
) -> list[dict]:
    if quantidade_vagas <= 0:
        raise ValueError(
            "A quantidade de vagas deve ser maior que zero."
        )

    imagem_exibicao = imagem.copy()
    vagas_selecionadas = []

    for numero_vaga in range(1, quantidade_vagas + 1):
        titulo_janela = (
            f"Selecione a vaga {numero_vaga} de {quantidade_vagas}"
        )

        coordenadas = cv2.selectROI(
            titulo_janela,
            imagem_exibicao,
            showCrosshair=True,
            fromCenter=False
        )

        cv2.destroyWindow(titulo_janela)

        coordenada_x, coordenada_y, largura, altura = (
            int(valor) for valor in coordenadas
        )

        if largura <= 0 or altura <= 0:
            raise ValueError(
                f"A seleção da vaga {numero_vaga} foi cancelada ou é inválida."
            )

        vaga = {
            "id": f"vaga_{numero_vaga:02d}",
            "x": coordenada_x,
            "y": coordenada_y,
            "largura": largura,
            "altura": altura
        }

        vagas_selecionadas.append(vaga)

        ponto_inicial = (coordenada_x, coordenada_y)
        ponto_final = (
            coordenada_x + largura,
            coordenada_y + altura
        )

        cv2.rectangle(
            imagem_exibicao,
            ponto_inicial,
            ponto_final,
            (0, 255, 0),
            2
        )

        cv2.putText(
            imagem_exibicao,
            vaga["id"],
            (coordenada_x, max(20, coordenada_y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    cv2.destroyAllWindows()

    return vagas_selecionadas


def salvar_anotacoes(
    vagas_selecionadas: list[dict],
    caminho_anotacoes: str | Path,
    nome_imagem_referencia: str
) -> None:
    caminho_arquivo = Path(caminho_anotacoes)

    caminho_arquivo.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    anotacoes = {
        "imagem_referencia": nome_imagem_referencia,
        "vagas": vagas_selecionadas
    }

    with caminho_arquivo.open(
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            anotacoes,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def carregar_anotacoes(
    caminho_anotacoes: str | Path
) -> list[dict]:
    caminho_arquivo = Path(caminho_anotacoes)

    if not caminho_arquivo.is_file():
        raise FileNotFoundError(
            f"Arquivo de anotações não encontrado: {caminho_arquivo}"
        )

    with caminho_arquivo.open(
        "r",
        encoding="utf-8"
    ) as arquivo:
        anotacoes = json.load(arquivo)

    return anotacoes["vagas"]


def gerar_imagem_delimitada(
    imagem: np.ndarray,
    vagas: list[dict]
) -> np.ndarray:
    imagem_resultado = imagem.copy()

    for vaga in vagas:
        coordenada_x = vaga["x"]
        coordenada_y = vaga["y"]
        largura = vaga["largura"]
        altura = vaga["altura"]

        cv2.rectangle(
            imagem_resultado,
            (coordenada_x, coordenada_y),
            (
                coordenada_x + largura,
                coordenada_y + altura
            ),
            (0, 255, 0),
            2
        )

        cv2.putText(
            imagem_resultado,
            vaga["id"],
            (
                coordenada_x,
                max(20, coordenada_y - 8)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    return imagem_resultado


def extrair_regioes_interesse(
    imagem: np.ndarray,
    vagas: list[dict]
) -> dict[str, np.ndarray]:
    regioes_interesse = {}

    altura_imagem, largura_imagem = imagem.shape[:2]

    for vaga in vagas:
        coordenada_x = vaga["x"]
        coordenada_y = vaga["y"]
        largura = vaga["largura"]
        altura = vaga["altura"]

        if (
            coordenada_x < 0
            or coordenada_y < 0
            or largura <= 0
            or altura <= 0
            or coordenada_x + largura > largura_imagem
            or coordenada_y + altura > altura_imagem
        ):
            raise ValueError(
                f"Coordenadas inválidas para {vaga['id']}."
            )

        regiao_interesse = imagem[
            coordenada_y:coordenada_y + altura,
            coordenada_x:coordenada_x + largura
        ].copy()

        regioes_interesse[vaga["id"]] = regiao_interesse

    return regioes_interesse


def salvar_resultados(
    imagem: np.ndarray,
    vagas: list[dict],
    diretorio_saida: str | Path,
    nome_imagem: str
) -> None:
    pasta_saida = Path(diretorio_saida)

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True
    )

    imagem_delimitada = gerar_imagem_delimitada(
        imagem,
        vagas
    )

    caminho_imagem_delimitada = (
        pasta_saida / f"{nome_imagem}_delimitada.png"
    )

    if not cv2.imwrite(
        str(caminho_imagem_delimitada),
        imagem_delimitada
    ):
        raise OSError(
            f"Não foi possível salvar: {caminho_imagem_delimitada}"
        )

    regioes_interesse = extrair_regioes_interesse(
        imagem,
        vagas
    )

    for identificador_vaga, regiao_interesse in regioes_interesse.items():
        caminho_recorte = (
            pasta_saida / f"{nome_imagem}_{identificador_vaga}.png"
        )

        if not cv2.imwrite(
            str(caminho_recorte),
            regiao_interesse
        ):
            raise OSError(
                f"Não foi possível salvar: {caminho_recorte}"
            )
