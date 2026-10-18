
import argparse
from pathlib import Path

from .leitor_imagens import carregar_imagem, obter_dimensoes_imagem


def configurar_argumentos() -> argparse.Namespace:
    analisador_argumentos = argparse.ArgumentParser(
        description="Leitura e validação de imagens de estacionamentos."
    )

    analisador_argumentos.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Caminho da imagem que será carregada."
    )

    return analisador_argumentos.parse_args()


def main() -> None:
    argumentos = configurar_argumentos()

    caminho_imagem = argumentos.input

    imagem_carregada = carregar_imagem(caminho_imagem)

    largura_imagem, altura_imagem, quantidade_canais = obter_dimensoes_imagem(
        imagem_carregada
    )

    print("Imagem carregada com sucesso.")
    print(f"Arquivo: {caminho_imagem.name}")
    print(f"Largura: {largura_imagem} pixels")
    print(f"Altura: {altura_imagem} pixels")
    print(f"Quantidade de canais: {quantidade_canais}")


if __name__ == "__main__":
    main()
