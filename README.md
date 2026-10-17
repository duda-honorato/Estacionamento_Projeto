# Detecção de Vagas Disponíveis em Estacionamentos por Processamento Digital de Imagens

## Integrantes

- João Matheus de Oliveira Vieira
- Maria Eduarda de Melo Honorato
- Scheila Carolini da Silva Ceresa

## Descrição do projeto

Este projeto tem como objetivo desenvolver uma solução de Processamento Digital de Imagens (PDI) capaz de identificar vagas de estacionamento livres e ocupadas a partir de imagens capturadas por câmeras.

A proposta busca utilizar técnicas tradicionais de processamento de imagens para analisar regiões correspondentes às vagas e determinar seu estado de ocupação.

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
- Aplicar técnicas de pré-processamento.
- Calcular características visuais, como desvio-padrão e densidade de bordas.
- Implementar métodos de classificação por limiar.
- Comparar os resultados obtidos com referências de ocupação.
- Avaliar os métodos por meio de métricas quantitativas e análise de erros.

## Evolução do escopo

### M1 — Proposta inicial

Na M1, foi proposta uma solução em Java e OpenCV, dividida em três fases: detecção automática das vagas, extração das regiões de interesse e classificação de ocupação.

A etapa foi dedicada à definição do problema, planejamento do pipeline e identificação das tecnologias.

### M2 — Implementação parcial e avaliação

Após a devolutiva da M1, o escopo foi ajustado para reduzir a complexidade inicial e permitir uma avaliação experimental.

As principais mudanças são:

- Substituição de Java por Python.
- Utilização da biblioteca OpenCV para Python.
- Delimitação manual das vagas no resultado mínimo.
- Comparação entre métodos baseados em desvio-padrão e densidade de bordas.
- Definição experimental dos limiares de classificação.
- Avaliação com imagens e rótulos de referência.

A detecção automática das vagas poderá ser investigada em etapas futuras.

## Conjunto de imagens

O projeto prevê utilizar o dataset PKLot, desenvolvido com imagens de estacionamentos capturadas por câmeras fixas.

Fonte: https://web.inf.ufpr.br/luizoliveira/research-interests/pklot/

O conjunto contém imagens de diferentes perspectivas e condições ambientais, além de anotações que permitem identificar as regiões das vagas e seus estados de ocupação.

Na M2, será selecionado um subconjunto de imagens de uma mesma câmera para os experimentos.

A seleção final das imagens, os identificadores, a divisão entre calibração e avaliação e as condições observadas serão documentados no relatório da M2.

A licença e as condições de redistribuição dos arquivos serão verificadas antes da inclusão de imagens originais no repositório público.

## Pipeline proposto para a M2

### Etapa 1 — Leitura das imagens

Carregar imagens do estacionamento utilizando OpenCV.

### Etapa 2 — Delimitação das vagas

Utilizar coordenadas previamente definidas para identificar as regiões correspondentes às vagas.

### Etapa 3 — Extração das regiões de interesse

Recortar as regiões de interesse e aplicar o pré-processamento necessário.

### Etapa 4 — Extração de características

Calcular características visuais de cada vaga, incluindo:

- Desvio-padrão dos níveis de intensidade.
- Densidade de bordas detectadas pelo algoritmo Canny.

### Etapa 5 — Classificação

Utilizar limiares definidos experimentalmente para classificar cada vaga:

- `0`: vaga livre.
- `1`: vaga ocupada.

### Etapa 6 — Avaliação

Comparar os resultados previstos com os rótulos de referência, utilizando métricas como acurácia, precisão, revocação e matriz de confusão.

Os experimentos também deverão apresentar casos de acerto, falha e limitações dos métodos.

## Tecnologias

- Python 3
- OpenCV
- NumPy
- pytest
- Git e GitHub
- Visual Studio Code

## Estrutura do projeto

```text
M1_Pt1/
├── data/
│   ├── annotations/
│   └── results/
├── docs/
│   ├── proposta.md
│   ├── relatorio_m2.md
│   └── AI_USAGE.md
├── images/
│   ├── input/
│   └── output/
├── src/
│   └── estacionamento/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

A estrutura será construída progressivamente conforme as funcionalidades forem implementadas.

## Instalação e execução

As instruções de instalação, configuração do ambiente virtual e execução serão adicionadas e verificadas durante o desenvolvimento da M2.

## Limitações previstas

- Dependência de vagas previamente delimitadas.
- Sensibilidade a sombras, iluminação e condições climáticas.
- Possíveis erros com veículos de cores semelhantes ao piso.
- Dificuldade com oclusões e objetos parcialmente posicionados nas vagas.
- Necessidade de recalibrar coordenadas quando houver mudança de câmera ou perspectiva.

## Vídeo da M1

https://youtu.be/5l5vSYWoiJw

## Uso de inteligência artificial

Ferramentas de IA foram utilizadas como apoio à revisão textual, organização da documentação e discussão de alternativas técnicas.

Na M2, o uso de IA para apoio ao desenvolvimento será documentado, incluindo as sugestões recebidas, as modificações realizadas e as verificações executadas pelo grupo.

As decisões, implementações e avaliações são de responsabilidade dos integrantes.