import argparse
import csv
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .delimitador_vagas import carregar_anotacoes, extrair_regioes_interesse  # noqa: E402
from .leitor_imagens import carregar_imagem  # noqa: E402
from .pipeline import ATRIBUTOS, EXTENSOES, carregar_rotulos  # noqa: E402
from .processamento import Parametros, processar_vaga  # noqa: E402

COR_LIVRE = "#2a78d6"
COR_OCUPADA = "#eb6834"
COR_TEXTO = "#3d3d3a"
COR_GRADE = "#e4e3dd"


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def carregar_amostras(pasta: Path, anotacoes: Path, rotulos_csv: Path) -> list[dict]:
    """Recorta as ROIs de todas as imagens e junta com os rótulos."""
    vagas = carregar_anotacoes(anotacoes)
    rotulos = carregar_rotulos(rotulos_csv)

    arquivos = sorted(
        c for c in pasta.iterdir() if c.is_file() and c.suffix.lower() in EXTENSOES
    )

    amostras = []
    for caminho in arquivos:
        imagem = carregar_imagem(caminho)
        for vaga_id, roi in extrair_regioes_interesse(imagem, vagas).items():
            chave = (caminho.name, vaga_id)
            if chave not in rotulos:
                continue
            amostras.append({
                "imagem": caminho.name,
                "vaga_id": vaga_id,
                "ocupada": rotulos[chave],
                "roi": roi,
            })
    return amostras


def extrair(amostras: list[dict], parametros: Parametros) -> list[dict]:
    """Calcula as características de todas as amostras com os parâmetros dados."""
    linhas = []
    for amostra in amostras:
        resultado = processar_vaga(amostra["roi"], parametros)
        linha = {k: amostra[k] for k in ("imagem", "vaga_id", "ocupada")}
        linha.update(resultado.caracteristicas)
        linhas.append(linha)
    return linhas


# ---------------------------------------------------------------------------
# Limiar e métricas (mesma regra da interface: valor >= limiar -> ocupada)
# ---------------------------------------------------------------------------

def melhor_limiar(valores: list[float], referencias: list[int]) -> float:
    unicos = sorted(set(valores))
    candidatos = [unicos[0]] + [
        (a + b) / 2 for a, b in zip(unicos, unicos[1:])
    ] + [unicos[-1] + 1]

    melhor, melhor_acertos = candidatos[0], -1
    for limiar in candidatos:
        acertos = sum(int(v >= limiar) == r for v, r in zip(valores, referencias))
        if acertos > melhor_acertos:
            melhor, melhor_acertos = limiar, acertos
    return melhor


def metricas(referencias: list[int], previstas: list[int]) -> dict[str, float]:
    pares = list(zip(referencias, previstas))
    vp = sum(r == 1 and p == 1 for r, p in pares)
    fp = sum(r == 0 and p == 1 for r, p in pares)
    fn = sum(r == 1 and p == 0 for r, p in pares)
    vn = sum(r == 0 and p == 0 for r, p in pares)

    precisao = vp / (vp + fp) if vp + fp else 0.0
    revocacao = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * precisao * revocacao / (precisao + revocacao) if precisao + revocacao else 0.0
    return {
        "acuracia": (vp + vn) / len(pares),
        "precisao": precisao,
        "revocacao": revocacao,
        "f1": f1,
        "erros": fp + fn,
    }


def avaliar(linhas: list[dict], atributo: str) -> dict[str, float]:
    """Métricas com limiar ajustado em tudo e com validação LOIO."""
    valores = [l[atributo] for l in linhas]
    referencias = [l["ocupada"] for l in linhas]

    limiar = melhor_limiar(valores, referencias)
    ajustado = metricas(referencias, [int(v >= limiar) for v in valores])

    refs_loio, prevs_loio = [], []
    for imagem in sorted({l["imagem"] for l in linhas}):
        treino = [l for l in linhas if l["imagem"] != imagem]
        teste = [l for l in linhas if l["imagem"] == imagem]
        limiar_treino = melhor_limiar(
            [l[atributo] for l in treino], [l["ocupada"] for l in treino]
        )
        refs_loio += [l["ocupada"] for l in teste]
        prevs_loio += [int(l[atributo] >= limiar_treino) for l in teste]
    loio = metricas(refs_loio, prevs_loio)

    livres = [v for v, r in zip(valores, referencias) if r == 0]
    ocupadas = [v for v, r in zip(valores, referencias) if r == 1]

    return {
        "limiar": limiar,
        "acuracia": ajustado["acuracia"],
        "f1": ajustado["f1"],
        "erros": ajustado["erros"],
        "loio_acuracia": loio["acuracia"],
        "loio_f1": loio["f1"],
        "loio_erros": loio["erros"],
        "media_livres": sum(livres) / len(livres),
        "media_ocupadas": sum(ocupadas) / len(ocupadas),
    }


# ---------------------------------------------------------------------------
# Experimentos
# ---------------------------------------------------------------------------

def exp_atributos(amostras, base):
    """E1 - Comparação entre atributos com os parâmetros padrão."""
    linhas = extrair(amostras, base)
    return linhas, [{"atributo": a, **avaliar(linhas, a)} for a in ATRIBUTOS]


def exp_canny_blur(amostras, base):
    """E2 - Limiares do Canny e tamanho do blur (atributo: densidade_bordas)."""
    resultado = []
    for blur in (3, 5, 7):
        for canny_min, canny_max in ((30, 90), (50, 150), (70, 200), (100, 250)):
            parametros = replace(base, blur=blur, canny_min=canny_min, canny_max=canny_max)
            linhas = extrair(amostras, parametros)
            resultado.append({
                "blur": blur, "canny_min": canny_min, "canny_max": canny_max,
                **avaliar(linhas, "densidade_bordas"),
            })
    return resultado


def exp_clahe(amostras, base):
    """E3 - CLAHE ligado e desligado."""
    resultado = []
    for usar_clahe in (False, True):
        linhas = extrair(amostras, replace(base, usar_clahe=usar_clahe))
        for atributo in ("desvio_padrao", "densidade_bordas", "area_mascara"):
            resultado.append({
                "clahe": "sim" if usar_clahe else "não", "atributo": atributo,
                **avaliar(linhas, atributo),
            })
    return resultado


def exp_morfologia(amostras, base):
    """E4 - Sem morfologia x kernels de fechamento/abertura.

    A densidade de bordas é calculada antes da morfologia, então não muda
    aqui; por isso são avaliados os atributos que usam a máscara.
    """
    configuracoes = [("sem morfologia", replace(base, usar_morfologia=False))]
    for fechamento in (3, 5, 7):
        for abertura in (3, 5):
            configuracoes.append((
                f"fech. {fechamento}x{fechamento} + aber. {abertura}x{abertura}",
                replace(base, kernel_fechamento=fechamento, kernel_abertura=abertura),
            ))

    resultado = []
    for nome, parametros in configuracoes:
        linhas = extrair(amostras, parametros)
        for atributo in ("area_mascara", "maior_componente", "num_componentes"):
            resultado.append({"morfologia": nome, "atributo": atributo,
                              **avaliar(linhas, atributo)})
    return resultado


def exp_area_minima(amostras, base):
    """E5 - Área mínima dos componentes conexos."""
    resultado = []
    for area in (0, 10, 20, 40, 80):
        linhas = extrair(amostras, replace(base, area_minima_componente=area))
        for atributo in ("maior_componente", "num_componentes"):
            resultado.append({"area_minima": area, "atributo": atributo,
                              **avaliar(linhas, atributo)})
    return resultado


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def estilizar(eixo) -> None:
    eixo.spines[["top", "right"]].set_visible(False)
    for lado in ("left", "bottom"):
        eixo.spines[lado].set_color(COR_GRADE)
    eixo.tick_params(colors=COR_TEXTO, labelsize=9)
    eixo.grid(True, color=COR_GRADE, linewidth=0.8)
    eixo.set_axisbelow(True)


def grafico_dispersao(linhas: list[dict], limiar: float, caminho: Path) -> None:
    figura, eixo = plt.subplots(figsize=(8, 5.5), dpi=150)
    estilizar(eixo)

    for classe, cor, marcador, nome in (
        (0, COR_LIVRE, "o", "Livre"),
        (1, COR_OCUPADA, "^", "Ocupada"),
    ):
        pontos = [l for l in linhas if l["ocupada"] == classe]
        eixo.scatter(
            [p["desvio_padrao"] for p in pontos],
            [p["densidade_bordas"] for p in pontos],
            s=60, c=cor, marker=marcador, edgecolors="white", linewidths=1.5,
            label=f"{nome} (n = {len(pontos)})", zorder=3,
        )

    eixo.axhline(limiar, color=COR_TEXTO, linestyle="--", linewidth=1.2, zorder=2)
    eixo.text(
        eixo.get_xlim()[1], limiar, f"  limiar = {limiar:.3f}",
        va="bottom", ha="right", fontsize=9, color=COR_TEXTO,
    )

    for l in linhas:
        previsto = int(l["densidade_bordas"] >= limiar)
        if previsto != l["ocupada"]:
            eixo.annotate(
                f"{l['imagem']} {l['vaga_id']}\n(veículo escuro, FN)",
                (l["desvio_padrao"], l["densidade_bordas"]),
                xytext=(12, 18), textcoords="offset points", fontsize=8.5,
                color=COR_TEXTO, arrowprops={"arrowstyle": "-", "color": COR_TEXTO,
                                             "linewidth": 0.8},
            )

    eixo.set_xlabel("Desvio-padrão dos níveis de cinza", color=COR_TEXTO)
    eixo.set_ylabel("Densidade de bordas (fração de pixels)", color=COR_TEXTO)
    eixo.set_title(
        "Separação entre vagas livres e ocupadas (30 amostras, parâmetros padrão)",
        fontsize=11, color=COR_TEXTO, loc="left",
    )
    eixo.legend(frameon=False, fontsize=9, loc="upper left")
    figura.tight_layout()
    figura.savefig(caminho)
    plt.close(figura)


def grafico_atributos(linhas: list[dict], tabela: list[dict], caminho: Path) -> None:
    limiares = {t["atributo"]: t["limiar"] for t in tabela}
    figura, eixos = plt.subplots(1, len(ATRIBUTOS), figsize=(13, 4), dpi=150)

    for eixo, atributo in zip(eixos, ATRIBUTOS):
        estilizar(eixo)
        eixo.grid(False, axis="x")
        for classe, cor, marcador, x in ((0, COR_LIVRE, "o", 0), (1, COR_OCUPADA, "^", 1)):
            valores = [l[atributo] for l in linhas if l["ocupada"] == classe]
            deslocamentos = [x + ((i % 5) - 2) * 0.06 for i in range(len(valores))]
            eixo.scatter(deslocamentos, valores, s=40, c=cor, marker=marcador,
                         edgecolors="white", linewidths=1.2, zorder=3)
        eixo.axhline(limiares[atributo], color=COR_TEXTO, linestyle="--", linewidth=1)
        eixo.set_xticks([0, 1], ["Livre", "Ocupada"])
        eixo.set_xlim(-0.6, 1.6)
        eixo.set_title(atributo, fontsize=10, color=COR_TEXTO)

    figura.suptitle(
        "Valores de cada atributo por classe (linha tracejada = limiar de maior acurácia)",
        fontsize=11, color=COR_TEXTO, x=0.01, ha="left",
    )
    figura.tight_layout()
    figura.savefig(caminho)
    plt.close(figura)


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

def formatar(valor) -> str:
    if isinstance(valor, float):
        return f"{valor:.4f}" if abs(valor) < 1 else f"{valor:.3f}"
    return str(valor)


COLUNAS_LEGIVEIS = {
    "limiar": "Limiar", "acuracia": "Acurácia", "f1": "F1", "erros": "Erros",
    "loio_acuracia": "Acurácia LOIO", "loio_f1": "F1 LOIO", "loio_erros": "Erros LOIO",
    "media_livres": "Média livres", "media_ocupadas": "Média ocupadas",
}


def salvar_tabela(linhas: list[dict], caminho_csv: Path) -> str:
    with caminho_csv.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    colunas = list(linhas[0].keys())
    cabecalho = [COLUNAS_LEGIVEIS.get(c, c) for c in colunas]
    texto = "| " + " | ".join(cabecalho) + " |\n"
    texto += "|" + "|".join("---" for _ in colunas) + "|\n"
    for linha in linhas:
        texto += "| " + " | ".join(formatar(linha[c]) for c in colunas) + " |\n"
    return texto


def configurar_argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(description="Experimentos de parâmetros da M2.")
    analisador.add_argument("--input", required=True, type=Path)
    analisador.add_argument("--annotations", required=True, type=Path)
    analisador.add_argument("--labels", required=True, type=Path)
    analisador.add_argument("--output", required=True, type=Path)
    analisador.add_argument("--limiar", type=float, default=0.076,
                            help="Limiar da densidade de bordas desenhado na dispersão.")

    # Configuração base (os experimentos variam um parâmetro de cada vez a partir dela)
    padrao = Parametros()
    analisador.add_argument("--blur", type=int, default=padrao.blur)
    analisador.add_argument("--canny-min", type=int, default=padrao.canny_min)
    analisador.add_argument("--canny-max", type=int, default=padrao.canny_max)
    analisador.add_argument("--clahe", action="store_true")
    analisador.add_argument("--sem-morfologia", action="store_true")
    analisador.add_argument("--kernel-fechamento", type=int, default=padrao.kernel_fechamento)
    analisador.add_argument("--kernel-abertura", type=int, default=padrao.kernel_abertura)
    analisador.add_argument("--area-minima", type=int, default=padrao.area_minima_componente)
    return analisador.parse_args()


def montar_base(argumentos: argparse.Namespace) -> Parametros:
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


def main() -> None:
    argumentos = configurar_argumentos()
    pasta = argumentos.output
    pasta.mkdir(parents=True, exist_ok=True)

    amostras = carregar_amostras(argumentos.input, argumentos.annotations, argumentos.labels)
    base = montar_base(argumentos)
    print(f"Amostras rotuladas: {len(amostras)}")
    print(f"Configuração base: {base}")

    linhas_base, e1 = exp_atributos(amostras, base)
    experimentos = [
        ("exp1_atributos", "E1 - Comparação entre atributos (parâmetros padrão)", e1),
        ("exp2_canny_blur", "E2 - Canny e blur (atributo: densidade_bordas)",
         exp_canny_blur(amostras, base)),
        ("exp3_clahe", "E3 - CLAHE", exp_clahe(amostras, base)),
        ("exp4_morfologia", "E4 - Morfologia (atributos calculados sobre a máscara)",
         exp_morfologia(amostras, base)),
        ("exp5_area_minima", "E5 - Área mínima dos componentes",
         exp_area_minima(amostras, base)),
    ]

    relatorio = "# Resultados dos experimentos\n\n"
    relatorio += (
        f"Amostras: {len(amostras)} "
        f"(ocupadas: {sum(a['ocupada'] for a in amostras)}). "
        "Regra: atributo >= limiar -> ocupada.\n\n"
        "- **Limiar / Acurácia / F1 / Erros**: limiar de maior acurácia ajustado nas "
        "mesmas amostras (otimista).\n"
        "- **LOIO**: limiar escolhido em 4 imagens e aplicado na 5ª, repetido para "
        "cada imagem.\n\n"
    )
    for nome, titulo, tabela in experimentos:
        relatorio += f"## {titulo}\n\n" + salvar_tabela(tabela, pasta / f"{nome}.csv") + "\n"
        print(f"{titulo}: {len(tabela)} configurações")

    (pasta / "resultados_experimentos.md").write_text(relatorio, encoding="utf-8")

    grafico_dispersao(linhas_base, argumentos.limiar, pasta / "dispersao_caracteristicas.png")
    grafico_atributos(linhas_base, e1, pasta / "separacao_atributos.png")

    print(f"Concluído. Resultados em: {pasta}")


if __name__ == "__main__":
    main()
