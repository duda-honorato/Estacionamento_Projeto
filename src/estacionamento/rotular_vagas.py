
import argparse
import csv
from pathlib import Path

import cv2

from .delimitador_vagas import (
    carregar_anotacoes,
    extrair_regioes_interesse,
)
from .leitor_imagens import carregar_imagem


def configurar_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        description="Rotulagem manual das vagas de estacionamento."
    )

    analisador.add_argument(
        "--input",
        required=True,
        type=Path
    )

    analisador.add_argument(
        "--annotations",
        required=True,
        type=Path
    )

    analisador.add_argument(
        "--output",
        required=True,
        type=Path
    )

    return analisador.parse_args()


def solicitar_rotulo_vaga(
    imagem_recorte,
    nome_imagem: str,
    identificador_vaga: str
) -> int:
    titulo_janela = f"{nome_imagem} - {identificador_vaga}"

    altura_recorte, largura_recorte = imagem_recorte.shape[:2]

    fator_ampliacao = min(
        6,
        max(1, 360 // max(largura_recorte, altura_recorte))
    )

    imagem_ampliada = cv2.resize(
        imagem_recorte,
        (
            largura_recorte * fator_ampliacao,
            altura_recorte * fator_ampliacao
        ),
        interpolation=cv2.INTER_NEAREST
    )

    cv2.namedWindow(
        titulo_janela,
        cv2.WINDOW_NORMAL
    )

    try:
        while True:
            cv2.imshow(
                titulo_janela,
                imagem_ampliada
            )

            print(
                f"Imagem: {nome_imagem} | Vaga: {identificador_vaga}"
            )
            print("Pressione 0 para LIVRE ou 1 para OCUPADA.")

            tecla_pressionada = cv2.waitKey(0) & 0xFF

            if tecla_pressionada == ord("0"):
                return 0

            if tecla_pressionada == ord("1"):
                return 1

            print("Tecla inválida. Utilize 0 ou 1.")

    finally:
        cv2.destroyWindow(titulo_janela)


def rotular_imagens(
    diretorio_entrada: Path,
    caminho_anotacoes: Path,
    caminho_saida: Path
) -> None:
    if not diretorio_entrada.is_dir():
        raise NotADirectoryError(
            f"Diretório de imagens não encontrado: {diretorio_entrada}"
        )

    vagas = carregar_anotacoes(caminho_anotacoes)

    arquivos_imagem = sorted(
        caminho_imagem
        for caminho_imagem in diretorio_entrada.iterdir()
        if caminho_imagem.is_file()
        and caminho_imagem.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )

    if not arquivos_imagem:
        raise ValueError(
            "Nenhuma imagem foi encontrada para rotulagem."
        )

    registros_rotulagem = []

    for caminho_imagem in arquivos_imagem:
        imagem = carregar_imagem(caminho_imagem)

        regioes_interesse = extrair_regioes_interesse(
            imagem,
            vagas
        )

        for identificador_vaga, imagem_recorte in regioes_interesse.items():
            rotulo_ocupacao = solicitar_rotulo_vaga(
                imagem_recorte,
                caminho_imagem.name,
                identificador_vaga
            )

            registro = {
                "imagem": caminho_imagem.name,
                "vaga_id": identificador_vaga,
                "ocupada": rotulo_ocupacao
            }

            registros_rotulagem.append(registro)

            print(
                f"Registrado: {caminho_imagem.name} | "
                f"{identificador_vaga} | "
                f"ocupada={rotulo_ocupacao}"
            )

    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with caminho_saida.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo_saida:
        escritor_csv = csv.DictWriter(
            arquivo_saida,
            fieldnames=["imagem", "vaga_id", "ocupada"]
        )

        escritor_csv.writeheader()
        escritor_csv.writerows(registros_rotulagem)

    print("Rotulagem concluída.")
    print(f"Quantidade de registros: {len(registros_rotulagem)}")
    print(f"Arquivo gerado: {caminho_saida}")


def main() -> None:
    argumentos = configurar_argumentos()

    rotular_imagens(
        argumentos.input,
        argumentos.annotations,
        argumentos.output
    )


if __name__ == "__main__":
    main()
