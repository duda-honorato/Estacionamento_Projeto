# Detecção de Vagas Disponíveis em Estacionamentos por Processamento Digital de Imagens

## Integrantes

- João Matheus de Oliveira Vieira
- Maria Eduarda de Melo Honorato
- Scheila Carolini da Silva Ceresa

## Descrição do projeto

Este projeto tem como objetivo desenvolver uma solução de Processamento Digital de Imagens (PDI) capaz de identificar vagas de estacionamento livres e ocupadas a partir de imagens capturadas por câmeras.

A proposta utiliza técnicas tradicionais de processamento de imagens para analisar as regiões correspondentes às vagas e determinar seu estado de ocupação.

O projeto é desenvolvido de forma incremental ao longo das etapas M1, M2 e M3 da disciplina de Processamento de Imagens.

## Problema investigado

Em estacionamentos com grande quantidade de vagas, a identificação visual de espaços disponíveis pode ser ineficiente, especialmente em horários de maior movimentação.

Diante disso, o projeto investiga a seguinte questão:

**Como utilizar técnicas de Processamento Digital de Imagens para identificar automaticamente vagas de estacionamento livres e ocupadas em imagens capturadas por câmeras?**

## Objetivo geral

Desenvolver e avaliar uma solução em Python e OpenCV para classificar vagas de estacionamento previamente delimitadas como livres ou ocupadas.

## Objetivos específicos

- Selecionar imagens de estacionamentos capturadas por câmeras fixas.
- Identificar e delimitar as regiões correspondentes às vagas.
- Extrair as regiões de interesse (ROI) das imagens.
- Aplicar técnicas de pré-processamento, segmentação e morfologia matemática.
- Calcular características visuais, como desvio-padrão e densidade de bordas.
- Implementar a classificação por limiar.
- Comparar os resultados obtidos com rótulos de referência.
- Avaliar os métodos por meio de métricas quantitativas e análise de erros.

## Evolução do escopo

### M1 — Proposta inicial

Na M1, foi proposta uma solução em Java e OpenCV, dividida em três fases: detecção automática das vagas, extração das regiões de interesse e classificação de ocupação.

A etapa foi dedicada à definição do problema, ao planejamento do pipeline e à identificação das tecnologias.

### M2 — Implementação parcial e avaliação

Após a devolutiva da M1, o escopo foi ajustado para reduzir a complexidade inicial e permitir uma avaliação experimental.

As principais mudanças foram:

- Substituição de Java por Python.
- Utilização da biblioteca OpenCV para Python.
- Delimitação manual das vagas.
- Comparação entre atributos baseados em intensidade (desvio-padrão), bordas (Canny), morfologia e componentes conexos.
- Definição experimental dos limiares de classificação.
- Avaliação com imagens e rótulos de referência.
- Interface gráfica para executar os testes e o pipeline e exibir as métricas.

A detecção automática das vagas poderá ser investigada em etapas futuras.

## Conjunto de imagens

O projeto utiliza imagens de estacionamento capturadas por câmera fixa. A referência adotada é o dataset PKLot:

Fonte: https://web.inf.ufpr.br/luizoliveira/research-interests/pklot/

O subconjunto atual possui **5 imagens de uma mesma câmera** (`images/input/0.png` a `4.png`), com diferentes condições de iluminação e de ocupação.

Foram delimitadas **6 vagas** de uma mesma fileira, gerando **30 amostras** (5 imagens × 6 vagas), rotuladas manualmente: **7 ocupadas e 23 livres**.

A licença e as condições de redistribuição dos arquivos devem ser verificadas antes da inclusão de imagens originais no repositório público.

## Pipeline

### Etapa 1 — Delimitação das vagas

As vagas são marcadas manualmente sobre uma imagem de referência (`3.png`, estacionamento vazio) com `cv2.selectROI`. As coordenadas ficam em `annotations/vagas.json` (`x`, `y`, `largura`, `altura`).

Os retângulos terminam logo acima da faixa de grama (y = 308) para não incluir os veículos da fileira seguinte, que aumentavam artificialmente as bordas e o desvio-padrão das vagas livres. A exceção é a `vaga_03`, que vai até y = 322 e ainda inclui parte da grama e da fileira de baixo.

### Etapa 2 — Rotulagem de referência

Cada recorte é exibido ampliado e rotulado pelo teclado (`0` = livre, `1` = ocupada). O resultado é salvo em `annotations/rotulos.csv` (`imagem`, `vaga_id`, `ocupada`).

### Etapa 3 — Extração das regiões de interesse

Para cada imagem da pasta de entrada, as ROIs das vagas são recortadas a partir das coordenadas do JSON.

### Etapa 4 — Pré-processamento

- Conversão para tons de cinza.
- CLAHE (equalização adaptativa de histograma), opcional.
- Suavização gaussiana (kernel padrão 5×5).

### Etapa 5 — Segmentação e morfologia

- Detecção de bordas com Canny (limiares padrão 50 e 150).
- Fechamento (elemento elíptico 5×5), para unir bordas próximas.
- Abertura (elemento elíptico 3×3), para remover ruído isolado.
- Análise de componentes conexos (vizinhança 8), descartando componentes com menos de 20 pixels.

### Etapa 6 — Extração de características

| Atributo | Descrição |
|---|---|
| `desvio_padrao` | Desvio-padrão dos níveis de cinza da ROI |
| `densidade_bordas` | Fração de pixels de borda (Canny) na ROI |
| `area_mascara` | Fração de pixels ativos após a morfologia |
| `maior_componente` | Área do maior componente conexo / área da ROI |
| `num_componentes` | Quantidade de componentes conexos válidos |

### Etapa 7 — Classificação

A vaga é classificada como **ocupada (1)** quando o atributo escolhido é maior ou igual ao limiar; caso contrário, é **livre (0)**.

O atributo padrão é `densidade_bordas`, com limiar **0,076**. Esse valor é o ponto médio entre a maior densidade observada em vagas livres (≈ 0,070) e a menor observada em vagas ocupadas corretamente detectáveis (≈ 0,082).

### Etapa 8 — Avaliação

As previsões são comparadas com os rótulos de referência. A interface calcula a matriz de confusão, a acurácia, a precisão, a revocação, a especificidade e o F1 (classe positiva = ocupada), lista os erros e compara todos os atributos.

## Resultados preliminares (M2)

Configuração: `densidade_bordas >= 0,076`, parâmetros padrão.

-- Incluir os testes depois

## Tecnologias

- Python 3
- OpenCV
- NumPy
- Tkinter (interface gráfica)
- pytest
- Git e GitHub
- Visual Studio Code

## Estrutura do projeto

```text
Estacionamento_Projeto/
├── annotations/
│   ├── vagas.json            # coordenadas das vagas
│   └── rotulos.csv           # rótulos de referência (0 = livre, 1 = ocupada)
├── images/
│   ├── input/                # imagens do estacionamento
│   └── output/               # imagens delimitadas e recortes das vagas
├── data/
│   └── results/              # gerada pelo pipeline
├── src/
│   └── estacionamento/
│       ├── leitor_imagens.py     # leitura e validação de imagens
│       ├── delimitador_vagas.py  # seleção, salvamento e recorte das vagas
│       ├── anotar_vagas.py       # script: delimitação manual
│       ├── processar_vagas.py    # script: gera imagens delimitadas e recortes
│       ├── rotular_vagas.py      # script: rotulagem manual
│       ├── processamento.py      # pré-processamento, Canny, morfologia, componentes
│       ├── pipeline.py           # extração de características e classificação
│       └── __main__.py           # leitura de uma imagem (teste inicial)
├── tests/
│   ├── test_leitor_imagens.py
│   └── test_processamento.py
├── interface.py              # interface gráfica (testes, pipeline e métricas)
├── requirements.txt
└── README.md
```

## Instalação

Na raiz do projeto (Windows):

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

## Execução

### Pela interface (recomendado)

```bash
py interface.py
```

Na janela:

- **Rodar testes**: executa os testes com pytest.
- **Processar todas as imagens**: roda o pipeline com os parâmetros da tela.
- **Testes + processar**: roda os testes e, se passarem, o pipeline.
- **Abrir resultados**: abre a pasta `data/results`.

Ao final, o log mostra as tabelas de métricas (matriz de confusão, métricas, acertos por imagem, erros e comparação entre atributos). As tabelas também são salvas em `data/results/metricas.txt`.

### Pela linha de comando

Antes, configure o `PYTHONPATH`:

```bash
set PYTHONPATH=src          # cmd
$env:PYTHONPATH="src"       # PowerShell
```

Delimitar as vagas manualmente:

```bash
py -m estacionamento.anotar_vagas --input images/input/3.png --annotations annotations/vagas.json --output images/output --quantidade 6
```

Gerar as imagens delimitadas e os recortes:

```bash
py -m estacionamento.processar_vagas --input images/input --annotations annotations/vagas.json --output images/output
```

Rotular as vagas:

```bash
py -m estacionamento.rotular_vagas --input images/input --annotations annotations/vagas.json --output annotations/rotulos.csv
```

Executar o pipeline com classificação:

```bash
py -m estacionamento.pipeline --input images/input --annotations annotations/vagas.json --labels annotations/rotulos.csv --output data/results --limiar 0.076
```

Opções do pipeline: `--atributo`, `--blur`, `--canny-min`, `--canny-max`, `--clahe`, `--sem-morfologia`, `--kernel-fechamento`, `--kernel-abertura` e `--area-minima`.

Executar os testes:

```bash
py -m pytest -v tests
```

### Saídas do pipeline (`data/results/`)

- `caracteristicas.csv`: atributos de cada vaga, rótulo de referência e classe prevista.
- `parametros.json`: parâmetros, atributo, limiar e imagens usados na execução.
- `<imagem>_classificada.png`: imagem com as vagas em verde (livre) ou vermelho (ocupada).
- `intermediarias/<imagem>_<vaga>_etapas.png`: painel com as etapas (ROI, cinza, bordas, morfologia, componentes).
- `metricas.txt`: tabelas de métricas (gerado pela interface).

## Limitações

- Dependência de vagas previamente delimitadas.
- Necessidade de recalibrar as coordenadas quando houver mudança de câmera ou perspectiva.
- Sensibilidade a sombras, iluminação e condições climáticas.
- Erros com veículos escuros ou de cor semelhante ao piso (poucas bordas).
- Dificuldade com oclusões e veículos parcialmente posicionados nas vagas.
- Conjunto pequeno (30 amostras) e sem divisão entre calibração e avaliação.

## Vídeo da M1

https://youtu.be/5l5vSYWoiJw

## Uso de inteligência artificial

Ferramentas de IA foram utilizadas como apoio à revisão textual, à organização da documentação e à discussão de alternativas técnicas.

Na M2, a IA também foi usada como apoio no desenvolvimento, incluindo a sugestão de ajuste das coordenadas das vagas, a definição do limiar pelo ponto médio entre classes e a implementação das tabelas de métricas na interface. As sugestões foram verificadas pelo grupo com a execução do pipeline e dos testes.

As decisões, implementações e avaliações são de responsabilidade dos integrantes.
