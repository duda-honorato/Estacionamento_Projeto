
import argparse
from pathlib import Path

from .delimitador_vagas import (
    salvar_anotacoes,
    salvar_resultados,
    selecionar_vagas_manualmente,
)
from .leitor_imagens import carregar_imagem


def configurar_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        description="Delimitação manual das vagas de estacionamento."
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

    analisador.add_argument(
        "--quantidade",
        required=True,
        type=int
    )

    return analisador.parse_args()


def main() -> None:
    argumentos = configurar_argumentos()

    imagem = carregar_imagem(argumentos.input)

    vagas = selecionar_vagas_manualmente(
        imagem,
        argumentos.quantidade
    )

    salvar_anotacoes(
        vagas,
        argumentos.annotations,
        argumentos.input.name
    )

    salvar_resultados(
        imagem,
        vagas,
        argumentos.output,
        argumentos.input.stem
    )

    print("Delimitação manual concluída.")
    print(f"Imagem: {argumentos.input.name}")
    print(f"Quantidade de vagas: {len(vagas)}")
    print(f"Anotações: {argumentos.annotations}")
    print(f"Resultados: {argumentos.output}")


if __name__ == "__main__":
    main()
