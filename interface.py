import csv
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

ATRIBUTOS = [
    "desvio_padrao",
    "densidade_bordas",
    "area_mascara",
    "maior_componente",
    "num_componentes",
]

PADROES = {
    "input": "images/input",
    "annotations": "annotations/vagas.json",
    "labels": "annotations/rotulos.csv",
    "output": "data/results",
    "blur": 5,
    "canny_min": 50,
    "canny_max": 150,
    "kernel_fechamento": 5,
    "kernel_abertura": 3,
    "area_minima": 20,
    "clahe": False,
    "sem_morfologia": False,
    "atributo": "densidade_bordas",
    "limiar": "0,076",
}

def montar_ambiente() -> dict[str, str]:
    """Copia as variáveis de ambiente e coloca a pasta src no PYTHONPATH."""
    ambiente = os.environ.copy()
    caminho_src = str(RAIZ / "src")
    anterior = ambiente.get("PYTHONPATH")
    ambiente["PYTHONPATH"] = (
        caminho_src if not anterior else caminho_src + os.pathsep + anterior
    )
    ambiente["PYTHONIOENCODING"] = "utf-8"
    return ambiente


def comando_testes() -> list[str]:
    return [sys.executable, "-m", "pytest", "-v", "tests"]


def converter_limiar(texto: str) -> float | None:
    """Aceita '0.06' ou '0,06'. Texto vazio = sem classificação."""
    texto = texto.strip().replace(",", ".")
    if not texto:
        return None
    return float(texto)


def comando_pipeline(opcoes: dict) -> list[str]:
    """Monta o comando do pipeline a partir das opções da tela."""
    comando = [
        sys.executable, "-m", "estacionamento.pipeline",
        "--input", opcoes["input"],
        "--annotations", opcoes["annotations"],
        "--output", opcoes["output"],
        "--blur", str(int(opcoes["blur"])),
        "--canny-min", str(int(opcoes["canny_min"])),
        "--canny-max", str(int(opcoes["canny_max"])),
        "--kernel-fechamento", str(int(opcoes["kernel_fechamento"])),
        "--kernel-abertura", str(int(opcoes["kernel_abertura"])),
        "--area-minima", str(int(opcoes["area_minima"])),
        "--atributo", opcoes["atributo"],
    ]

    if opcoes["labels"].strip():
        comando += ["--labels", opcoes["labels"]]
    if opcoes["clahe"]:
        comando.append("--clahe")
    if opcoes["sem_morfologia"]:
        comando.append("--sem-morfologia")

    limiar = converter_limiar(opcoes["limiar"])
    if limiar is not None:
        comando += ["--limiar", str(limiar)]

    return comando


def executar(comando: list[str], imprimir) -> int:
    """Executa o comando na raiz do projeto, enviando cada linha para imprimir()."""
    imprimir("$ " + " ".join(comando[1:]) + "\n")

    processo = subprocess.Popen(
        comando,
        cwd=RAIZ,
        env=montar_ambiente(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    for linha in processo.stdout:
        imprimir(linha)

    return processo.wait()


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def contar_matriz(referencias: list[int], previstas: list[int]) -> dict[str, int]:
    """Conta VP, FP, FN e VN. Classe positiva = ocupada (1)."""
    pares = list(zip(referencias, previstas))
    return {
        "VP": sum(r == 1 and p == 1 for r, p in pares),
        "FP": sum(r == 0 and p == 1 for r, p in pares),
        "FN": sum(r == 1 and p == 0 for r, p in pares),
        "VN": sum(r == 0 and p == 0 for r, p in pares),
    }


def dividir(numerador: int, denominador: int) -> float | None:
    return numerador / denominador if denominador else None


def calcular_metricas(matriz: dict[str, int]) -> dict[str, float | None]:
    vp, fp, fn, vn = matriz["VP"], matriz["FP"], matriz["FN"], matriz["VN"]
    precisao = dividir(vp, vp + fp)
    revocacao = dividir(vp, vp + fn)
    if precisao is None or revocacao is None or precisao + revocacao == 0:
        f1 = None
    else:
        f1 = 2 * precisao * revocacao / (precisao + revocacao)
    return {
        "Acurácia": dividir(vp + vn, vp + fp + fn + vn),
        "Precisão": precisao,
        "Revocação": revocacao,
        "Especificidade": dividir(vn, vn + fp),
        "F1": f1,
    }


def formatar(valor: float | None) -> str:
    return "n/d" if valor is None else f"{valor:.3f}"


def tabela(cabecalho: list[str], linhas: list[list], titulo: str) -> str:
    """Monta uma tabela em texto com colunas alinhadas."""
    textos = [[str(c) for c in cabecalho]] + [[str(c) for c in l] for l in linhas]
    larguras = [max(len(l[i]) for l in textos) for i in range(len(cabecalho))]

    def linha_texto(celulas: list[str]) -> str:
        return "| " + " | ".join(c.ljust(w) for c, w in zip(celulas, larguras)) + " |"

    separador = "|-" + "-|-".join("-" * w for w in larguras) + "-|"
    corpo = [linha_texto(textos[0]), separador] + [linha_texto(l) for l in textos[1:]]
    return f"\n{titulo}\n" + "\n".join(corpo) + "\n"


def melhor_limiar(valores: list[float], referencias: list[int]) -> tuple[float, int]:
    """Testa limiares no meio de valores vizinhos e devolve o de maior acurácia."""
    unicos = sorted(set(valores))
    candidatos = [unicos[0]] + [
        (a + b) / 2 for a, b in zip(unicos, unicos[1:])
    ] + [unicos[-1] + 1]

    melhor = (candidatos[0], -1)
    for limiar in candidatos:
        acertos = sum(int(v >= limiar) == r for v, r in zip(valores, referencias))
        if acertos > melhor[1]:
            melhor = (limiar, acertos)
    return melhor


def resumir_resultados(pasta_saida: Path) -> str:
    """Lê o CSV do pipeline e monta as tabelas de métricas (também salva em metricas.txt)."""
    caminho_csv = pasta_saida / "caracteristicas.csv"
    if not caminho_csv.is_file():
        return ""

    with caminho_csv.open("r", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    configuracao = {}
    caminho_json = pasta_saida / "parametros.json"
    if caminho_json.is_file():
        with caminho_json.open("r", encoding="utf-8") as arquivo:
            configuracao = json.load(arquivo)

    resumo = f"\nVagas analisadas: {len(linhas)}\n"

    rotuladas = [l for l in linhas if l.get("ocupada_referencia", "") != ""]
    if not rotuladas:
        resumo += "Sem rótulos de referência: métricas não calculadas.\n"
        return resumo

    referencias = [int(l["ocupada_referencia"]) for l in rotuladas]
    resumo += (
        f"Rotuladas: {len(rotuladas)} "
        f"(ocupadas: {sum(referencias)} | livres: {len(referencias) - sum(referencias)})\n"
    )

    # ---- classificação com o limiar escolhido na tela ----
    comparaveis = [l for l in rotuladas if l.get("ocupada_prevista", "") != ""]
    if comparaveis:
        refs = [int(l["ocupada_referencia"]) for l in comparaveis]
        prevs = [int(l["ocupada_prevista"]) for l in comparaveis]
        matriz = contar_matriz(refs, prevs)

        resumo += (
            f"\nClassificação: {configuracao.get('atributo', '?')} >= "
            f"{configuracao.get('limiar', '?')}  ->  ocupada\n"
        )

        resumo += tabela(
            ["", "Prevista ocupada", "Prevista livre"],
            [
                ["Real ocupada", f"VP = {matriz['VP']}", f"FN = {matriz['FN']}"],
                ["Real livre", f"FP = {matriz['FP']}", f"VN = {matriz['VN']}"],
            ],
            "Tabela 1 - Matriz de confusão",
        )

        resumo += tabela(
            ["Métrica", "Valor"],
            [[nome, formatar(valor)] for nome, valor in calcular_metricas(matriz).items()],
            "Tabela 2 - Métricas (classe positiva = ocupada)",
        )

        por_imagem = {}
        for linha, r, p in zip(comparaveis, refs, prevs):
            acertos, total = por_imagem.get(linha["imagem"], (0, 0))
            por_imagem[linha["imagem"]] = (acertos + (r == p), total + 1)
        resumo += tabela(
            ["Imagem", "Acertos", "Acurácia"],
            [[img, f"{a}/{t}", f"{a / t:.0%}"] for img, (a, t) in sorted(por_imagem.items())],
            "Tabela 3 - Acertos por imagem",
        )

        erros = [
            [l["imagem"], l["vaga_id"],
             "FP (livre -> ocupada)" if p == 1 else "FN (ocupada -> livre)",
             l.get(configuracao.get("atributo", ""), "")]
            for l, r, p in zip(comparaveis, refs, prevs) if r != p
        ]
        if erros:
            resumo += tabela(
                ["Imagem", "Vaga", "Tipo de erro", "Valor do atributo"],
                erros,
                "Tabela 4 - Erros de classificação",
            )
        else:
            resumo += "\nTabela 4 - Erros de classificação: nenhum erro.\n"
    else:
        resumo += "\nLimiar vazio: Tabelas 1 a 4 não geradas (informe um limiar).\n"

    # ---- comparação entre atributos ----
    comparacao = []
    for atributo in ATRIBUTOS:
        if atributo not in rotuladas[0]:
            continue
        valores = [float(l[atributo]) for l in rotuladas]
        limiar, _ = melhor_limiar(valores, referencias)
        prevs = [int(v >= limiar) for v in valores]
        metricas = calcular_metricas(contar_matriz(referencias, prevs))
        comparacao.append(
            [atributo, f"{limiar:.4f}"] + [formatar(v) for v in metricas.values()]
        )
    resumo += tabela(
        ["Atributo", "Melhor limiar", "Acurácia", "Precisão", "Revocação",
         "Especif.", "F1"],
        comparacao,
        "Tabela 5 - Comparação entre atributos (limiar de maior acurácia)",
    )
    resumo += (
        "Obs.: na Tabela 5 o limiar foi ajustado nas mesmas imagens avaliadas,\n"
        "então os valores são otimistas (sem divisão calibração/avaliação).\n"
    )

    try:
        (pasta_saida / "metricas.txt").write_text(resumo, encoding="utf-8")
        resumo += f"\nTabelas salvas em: {pasta_saida / 'metricas.txt'}\n"
    except OSError as erro:
        resumo += f"\nNão foi possível salvar metricas.txt: {erro}\n"

    return resumo


def abrir_pasta(caminho: Path) -> None:
    caminho.mkdir(parents=True, exist_ok=True)
    if sys.platform.startswith("win"):
        os.startfile(caminho)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(caminho)])
    else:
        subprocess.Popen(["xdg-open", str(caminho)])


# ---------------------------------------------------------------------------
# Janela
# ---------------------------------------------------------------------------

def iniciar_interface() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    janela = tk.Tk()
    janela.title("Detecção de Vagas - M2")
    janela.geometry("860x680")
    janela.minsize(720, 560)

    mensagens: queue.Queue[str] = queue.Queue()
    botoes: list[ttk.Button] = []

    # ---- variáveis ligadas aos campos ----
    variaveis = {
        "input": tk.StringVar(value=PADROES["input"]),
        "annotations": tk.StringVar(value=PADROES["annotations"]),
        "labels": tk.StringVar(value=PADROES["labels"]),
        "output": tk.StringVar(value=PADROES["output"]),
        "blur": tk.IntVar(value=PADROES["blur"]),
        "canny_min": tk.IntVar(value=PADROES["canny_min"]),
        "canny_max": tk.IntVar(value=PADROES["canny_max"]),
        "kernel_fechamento": tk.IntVar(value=PADROES["kernel_fechamento"]),
        "kernel_abertura": tk.IntVar(value=PADROES["kernel_abertura"]),
        "area_minima": tk.IntVar(value=PADROES["area_minima"]),
        "clahe": tk.BooleanVar(value=PADROES["clahe"]),
        "sem_morfologia": tk.BooleanVar(value=PADROES["sem_morfologia"]),
        "atributo": tk.StringVar(value=PADROES["atributo"]),
        "limiar": tk.StringVar(value=PADROES["limiar"]),
    }

    # ---- arquivos ----
    quadro_arquivos = ttk.LabelFrame(janela, text="Arquivos", padding=8)
    quadro_arquivos.pack(fill="x", padx=10, pady=(10, 5))
    quadro_arquivos.columnconfigure(1, weight=1)

    def escolher(chave: str, tipo: str) -> None:
        if tipo == "pasta":
            escolhido = filedialog.askdirectory(initialdir=RAIZ)
        else:
            escolhido = filedialog.askopenfilename(initialdir=RAIZ)
        if escolhido:
            caminho = Path(escolhido)
            try:
                caminho = caminho.relative_to(RAIZ)
            except ValueError:
                pass
            variaveis[chave].set(str(caminho))

    campos_arquivo = [
        ("Pasta de imagens", "input", "pasta"),
        ("Vagas (JSON)", "annotations", "arquivo"),
        ("Rótulos (CSV, opcional)", "labels", "arquivo"),
        ("Pasta de resultados", "output", "pasta"),
    ]
    for linha, (rotulo, chave, tipo) in enumerate(campos_arquivo):
        ttk.Label(quadro_arquivos, text=rotulo).grid(row=linha, column=0, sticky="w", pady=2)
        ttk.Entry(quadro_arquivos, textvariable=variaveis[chave]).grid(
            row=linha, column=1, sticky="ew", padx=6
        )
        ttk.Button(
            quadro_arquivos, text="...", width=3,
            command=lambda c=chave, t=tipo: escolher(c, t)
        ).grid(row=linha, column=2)

    # ---- parâmetros ----
    quadro_parametros = ttk.LabelFrame(janela, text="Parâmetros", padding=8)
    quadro_parametros.pack(fill="x", padx=10, pady=5)

    campos_numericos = [
        ("Blur (ímpar)", "blur", 1, 31, 2),
        ("Canny mín.", "canny_min", 0, 255, 5),
        ("Canny máx.", "canny_max", 0, 255, 5),
        ("Kernel fechamento", "kernel_fechamento", 1, 31, 2),
        ("Kernel abertura", "kernel_abertura", 1, 31, 2),
        ("Área mínima (px)", "area_minima", 0, 1000, 5),
    ]
    for indice, (rotulo, chave, minimo, maximo, passo) in enumerate(campos_numericos):
        linha, coluna = divmod(indice, 3)
        ttk.Label(quadro_parametros, text=rotulo).grid(
            row=linha, column=coluna * 2, sticky="w", padx=(0, 4), pady=2
        )
        ttk.Spinbox(
            quadro_parametros, from_=minimo, to=maximo, increment=passo,
            textvariable=variaveis[chave], width=6
        ).grid(row=linha, column=coluna * 2 + 1, sticky="w", padx=(0, 16))

    ttk.Checkbutton(
        quadro_parametros, text="Usar CLAHE", variable=variaveis["clahe"]
    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 2))
    ttk.Checkbutton(
        quadro_parametros, text="Desligar morfologia", variable=variaveis["sem_morfologia"]
    ).grid(row=2, column=2, columnspan=2, sticky="w", pady=(6, 2))

    ttk.Label(quadro_parametros, text="Atributo").grid(row=3, column=0, sticky="w", pady=2)
    ttk.Combobox(
        quadro_parametros, values=ATRIBUTOS, textvariable=variaveis["atributo"],
        state="readonly", width=18
    ).grid(row=3, column=1, columnspan=2, sticky="w")
    ttk.Label(quadro_parametros, text="Limiar (vazio = não classificar)").grid(
        row=3, column=3, columnspan=2, sticky="e", padx=(0, 4)
    )
    ttk.Entry(quadro_parametros, textvariable=variaveis["limiar"], width=8).grid(
        row=3, column=5, sticky="w"
    )

    # ---- botões ----
    quadro_botoes = ttk.Frame(janela, padding=(10, 5))
    quadro_botoes.pack(fill="x")

    # ---- log ----
    log = ScrolledText(janela, height=18, font=("Consolas", 10), state="disabled")
    log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def escrever(texto: str) -> None:
        log.configure(state="normal")
        log.insert("end", texto)
        log.see("end")
        log.configure(state="disabled")

    def atualizar_log() -> None:
        while not mensagens.empty():
            escrever(mensagens.get_nowait())
        janela.after(100, atualizar_log)

    def travar(travado: bool) -> None:
        for botao in botoes:
            botao.configure(state="disabled" if travado else "normal")

    def em_segundo_plano(tarefa) -> None:
        """Roda a tarefa sem congelar a janela."""
        travar(True)

        def alvo() -> None:
            try:
                tarefa()
            except Exception as erro:  # mostra qualquer erro no log
                mensagens.put(f"\nERRO: {erro}\n")
            finally:
                janela.after(0, lambda: travar(False))

        threading.Thread(target=alvo, daemon=True).start()

    def ler_opcoes() -> dict | None:
        try:
            opcoes = {chave: variavel.get() for chave, variavel in variaveis.items()}
            converter_limiar(opcoes["limiar"])
        except (tk.TclError, ValueError):
            messagebox.showerror("Valor inválido", "Confira os parâmetros numéricos e o limiar.")
            return None
        if int(opcoes["blur"]) % 2 == 0:
            messagebox.showerror("Valor inválido", "O blur precisa ser ímpar (3, 5, 7...).")
            return None
        return opcoes

    def rodar_testes() -> None:
        def tarefa() -> None:
            mensagens.put("\n=== Testes ===\n")
            codigo = executar(comando_testes(), mensagens.put)
            if codigo == 0:
                mensagens.put("Todos os testes passaram.\n")
            else:
                mensagens.put(
                    "Algum teste falhou (veja acima). Se apareceu "
                    "'No module named pytest', rode: py -m pip install pytest\n"
                )
        em_segundo_plano(tarefa)

    def rodar_pipeline() -> None:
        opcoes = ler_opcoes()
        if opcoes is None:
            return

        def tarefa() -> None:
            mensagens.put("\n=== Pipeline (todas as imagens da pasta) ===\n")
            codigo = executar(comando_pipeline(opcoes), mensagens.put)
            if codigo == 0:
                mensagens.put(resumir_resultados(RAIZ / opcoes["output"]))
            else:
                mensagens.put("O pipeline terminou com erro (veja acima).\n")
        em_segundo_plano(tarefa)

    def rodar_tudo() -> None:
        opcoes = ler_opcoes()
        if opcoes is None:
            return

        def tarefa() -> None:
            mensagens.put("\n=== Testes ===\n")
            if executar(comando_testes(), mensagens.put) != 0:
                mensagens.put("Testes falharam; o pipeline não foi executado.\n")
                return
            mensagens.put("\n=== Pipeline (todas as imagens da pasta) ===\n")
            if executar(comando_pipeline(opcoes), mensagens.put) == 0:
                mensagens.put(resumir_resultados(RAIZ / opcoes["output"]))
        em_segundo_plano(tarefa)

    def abrir_resultados() -> None:
        try:
            abrir_pasta(RAIZ / variaveis["output"].get())
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def limpar_log() -> None:
        log.configure(state="normal")
        log.delete("1.0", "end")
        log.configure(state="disabled")

    for texto, acao in [
        ("Rodar testes", rodar_testes),
        ("Processar todas as imagens", rodar_pipeline),
        ("Testes + processar", rodar_tudo),
    ]:
        botao = ttk.Button(quadro_botoes, text=texto, command=acao)
        botao.pack(side="left", padx=(0, 6))
        botoes.append(botao)

    ttk.Button(quadro_botoes, text="Limpar log", command=limpar_log).pack(side="right")
    ttk.Button(quadro_botoes, text="Abrir resultados", command=abrir_resultados).pack(
        side="right", padx=6
    )

    escrever(f"Projeto: {RAIZ}\nPython: {sys.executable}\n")
    atualizar_log()
    janela.mainloop()


if __name__ == "__main__":
    iniciar_interface()
