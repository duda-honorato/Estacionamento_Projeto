
import argparse
from pathlib import Path

from .delimitador_vagas import (
    carregar_anotacoes,
    salvar_resultados,
)
from .leitor_imagens import carregar_imagem


def configurar_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        description="Aplica as coordenadas das vagas às imagens do estacionamento."
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


def processar_imagens(
    diretorio_entrada: Path,
    caminho_anotacoes: Path,
    diretorio_saida: Path
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
            "Nenhuma imagem foi encontrada no diretório informado."
        )

    for caminho_imagem in arquivos_imagem:
        imagem = carregar_imagem(caminho_imagem)

        salvar_resultados(
            imagem,
            vagas,
            diretorio_saida,
            caminho_imagem.stem
        )

        print(
            f"Imagem processada: {caminho_imagem.name} "
            f"| Vagas: {len(vagas)}"
        )

    print(
        f"Processamento concluído. Total de imagens: {len(arquivos_imagem)}"
    )


def main() -> None:
    argumentos = configurar_argumentos()

    processar_imagens(
        argumentos.input,
        argumentos.annotations,
        argumentos.output
    )


if __name__ == "__main__":
    main()
