import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np

from .delimitador_vagas import carregar_anotacoes, extrair_regioes_interesse
from .leitor_imagens import carregar_imagem
from .processamento import Parametros, processar_vaga

ATRIBUTOS = [
    "desvio_padrao",
    "densidade_bordas",
    "area_mascara",
    "maior_componente",
    "num_componentes",
]

EXTENSOES = {".png", ".jpg", ".jpeg"}


def configurar_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        description="Extrai características das vagas (segmentação, morfologia e componentes)."
    )

    analisador.add_argument("--input", required=True, type=Path,
                            help="Pasta com as imagens do estacionamento.")
    analisador.add_argument("--annotations", required=True, type=Path,
                            help="JSON com as coordenadas das vagas.")
    analisador.add_argument("--output", required=True, type=Path,
                            help="Pasta onde os resultados serão salvos.")
    analisador.add_argument("--labels", type=Path,
                            help="CSV de rótulos (imagem, vaga_id, ocupada). Opcional.")

    padrao = Parametros()
    analisador.add_argument("--blur", type=int, default=padrao.blur)
    analisador.add_argument("--canny-min", type=int, default=padrao.canny_min)
    analisador.add_argument("--canny-max", type=int, default=padrao.canny_max)
    analisador.add_argument("--clahe", action="store_true",
                            help="Aplica CLAHE antes da suavização.")
    analisador.add_argument("--sem-morfologia", action="store_true",
                            help="Desliga fechamento/abertura.")
    analisador.add_argument("--kernel-fechamento", type=int,
                            default=padrao.kernel_fechamento)
    analisador.add_argument("--kernel-abertura", type=int,
                            default=padrao.kernel_abertura)
    analisador.add_argument("--area-minima", type=int,
                            default=padrao.area_minima_componente)

    analisador.add_argument("--atributo", choices=ATRIBUTOS,
                            default="area_mascara",
                            help="Atributo usado na classificação por limiar.")
    analisador.add_argument("--limiar", type=float,
                            help="Se informado, vaga com atributo >= limiar é OCUPADA (1).")

    return analisador.parse_args()


def montar_parametros(argumentos: argparse.Namespace) -> Parametros:
    if argumentos.blur % 2 == 0:
        raise ValueError("--blur precisa ser ímpar.")

    return Parametros(
        blur=argumentos.blur,
        canny_min=argumentos.canny_min,
        canny_max=argumentos.canny_max,
        usar_clahe=argumentos.clahe,
        usar_morfologia=not argumentos.sem_morfologia,
        kernel_fechamento=argumentos.kernel_fechamento,
        kernel_abertura=argumentos.kernel_abertura,
        area_minima_componente=argumentos.area_minima,
    )


def carregar_rotulos(caminho: Path | None) -> dict[tuple[str, str], int]:
    if caminho is None:
        return {}

    with caminho.open("r", encoding="utf-8") as arquivo:
        return {
            (linha["imagem"], linha["vaga_id"]): int(linha["ocupada"])
            for linha in csv.DictReader(arquivo)
        }


def montar_painel(intermediarias: dict[str, np.ndarray], escala: int = 4) -> np.ndarray:
    """Coloca as etapas lado a lado, ampliadas e com título."""
    blocos = []

    for nome, imagem in intermediarias.items():
        if imagem.ndim == 2:
            imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)

        ampliada = cv2.resize(
            imagem,
            None,
            fx=escala,
            fy=escala,
            interpolation=cv2.INTER_NEAREST
        )

        titulo = np.full((24, ampliada.shape[1], 3), 255, dtype=np.uint8)
        cv2.putText(titulo, nome, (4, 17), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 0), 1, cv2.LINE_AA)

        separador = np.full((ampliada.shape[0] + 24, 6, 3), 255, dtype=np.uint8)
        blocos.append(np.vstack([titulo, ampliada]))
        blocos.append(separador)

    return np.hstack(blocos[:-1])


def desenhar_classificacao(
    imagem: np.ndarray,
    vagas: list[dict],
    previsoes: dict[str, int]
) -> np.ndarray:
    """Retângulo verde = livre, vermelho = ocupada."""
    resultado = imagem.copy()

    for vaga in vagas:
        ocupada = previsoes[vaga["id"]]
        cor = (0, 0, 255) if ocupada else (0, 200, 0)
        x, y, w, h = vaga["x"], vaga["y"], vaga["largura"], vaga["altura"]

        cv2.rectangle(resultado, (x, y), (x + w, y + h), cor, 2)
        cv2.putText(resultado, "ocupada" if ocupada else "livre",
                    (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.45, cor, 2)

    return resultado


def salvar_imagem(caminho: Path, imagem: np.ndarray) -> None:
    if not cv2.imwrite(str(caminho), imagem):
        raise OSError(f"Não foi possível salvar: {caminho}")


def executar_pipeline(argumentos: argparse.Namespace) -> None:
    parametros = montar_parametros(argumentos)
    vagas = carregar_anotacoes(argumentos.annotations)
    rotulos = carregar_rotulos(argumentos.labels)

    if not argumentos.input.is_dir():
        raise NotADirectoryError(f"Pasta de imagens não encontrada: {argumentos.input}")

    arquivos = sorted(
        caminho for caminho in argumentos.input.iterdir()
        if caminho.is_file() and caminho.suffix.lower() in EXTENSOES
    )

    if not arquivos:
        raise ValueError("Nenhuma imagem encontrada na pasta informada.")

    pasta_saida = argumentos.output
    pasta_intermediarias = pasta_saida / "intermediarias"
    pasta_intermediarias.mkdir(parents=True, exist_ok=True)

    linhas = []

    for caminho_imagem in arquivos:
        imagem = carregar_imagem(caminho_imagem)
        regioes = extrair_regioes_interesse(imagem, vagas)
        previsoes = {}

        for vaga_id, roi in regioes.items():
            resultado = processar_vaga(roi, parametros)

            linha = {"imagem": caminho_imagem.name, "vaga_id": vaga_id}

            if rotulos:
                linha["ocupada_referencia"] = rotulos.get(
                    (caminho_imagem.name, vaga_id), ""
                )

            linha.update(
                {nome: round(valor, 4)
                 for nome, valor in resultado.caracteristicas.items()}
            )

            if argumentos.limiar is not None:
                valor = resultado.caracteristicas[argumentos.atributo]
                previsoes[vaga_id] = int(valor >= argumentos.limiar)
                linha["ocupada_prevista"] = previsoes[vaga_id]

            linhas.append(linha)

            salvar_imagem(
                pasta_intermediarias / f"{caminho_imagem.stem}_{vaga_id}_etapas.png",
                montar_painel(resultado.intermediarias)
            )

        if previsoes:
            salvar_imagem(
                pasta_saida / f"{caminho_imagem.stem}_classificada.png",
                desenhar_classificacao(imagem, vagas, previsoes)
            )

        print(f"Imagem processada: {caminho_imagem.name} | Vagas: {len(regioes)}")

    caminho_csv = pasta_saida / "caracteristicas.csv"
    with caminho_csv.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    configuracao = {
        "parametros": asdict(parametros),
        "atributo": argumentos.atributo,
        "limiar": argumentos.limiar,
        "imagens": [caminho.name for caminho in arquivos],
        "anotacoes": str(argumentos.annotations),
    }
    with (pasta_saida / "parametros.json").open("w", encoding="utf-8") as arquivo:
        json.dump(configuracao, arquivo, ensure_ascii=False, indent=4)

    print(f"Concluído. {len(linhas)} vagas analisadas. Resultados em: {pasta_saida}")


def main() -> None:
    executar_pipeline(configurar_argumentos())


if __name__ == "__main__":
    main()
