import csv
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
    "limiar": "",
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


def resumir_resultados(pasta_saida: Path) -> str:
    """Resumo rápido do CSV: total de vagas e, se houver, acertos do limiar."""
    caminho_csv = pasta_saida / "caracteristicas.csv"
    if not caminho_csv.is_file():
        return ""

    with caminho_csv.open("r", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    resumo = f"Vagas analisadas: {len(linhas)}\n"

    comparaveis = [
        linha for linha in linhas
        if linha.get("ocupada_prevista", "") != ""
        and linha.get("ocupada_referencia", "") != ""
    ]
    if comparaveis:
        acertos = sum(
            linha["ocupada_prevista"] == linha["ocupada_referencia"]
            for linha in comparaveis
        )
        resumo += (
            f"Acertos em relação aos rótulos: {acertos}/{len(comparaveis)} "
            f"({acertos / len(comparaveis):.0%}) - avaliação preliminar\n"
        )

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
