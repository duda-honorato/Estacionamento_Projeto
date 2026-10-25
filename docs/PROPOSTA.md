# Proposta — Detecção de Vagas Disponíveis em Estacionamentos

Documento de proposta do Projeto Aplicado de Processamento de Imagens (2026-02), atualizado na M2 a partir da devolutiva da M1. A revisão da devolutiva e o plano de ação estão em [`revisao_m1_plano_m2.md`](revisao_m1_plano_m2.md). As instruções de instalação e de execução estão no [`README.md`](../README.md).

## 1. Identificação

| Item | Informação |
|---|---|
| Disciplina | Processamento de Imagens — 2026-02 |
| Grupo | Detecção de Vagas Disponíveis em Estacionamento |
| Integrantes | João Matheus de Oliveira Vieira, Maria Eduarda de Melo Honorato e Scheila Carolini da Silva Ceresa |
| Etapa atual | M2 — implementação parcial e avaliação |

## 2. Problema

Em estacionamentos com muitas vagas, identificar visualmente os espaços disponíveis é ineficiente, principalmente nos horários de maior movimento. Câmeras fixas já existentes podem ser usadas para indicar automaticamente quais vagas estão livres.

**Pergunta de pesquisa:** como utilizar técnicas de Processamento Digital de Imagens para identificar automaticamente vagas de estacionamento livres e ocupadas em imagens capturadas por câmeras?

**Entrada:** imagem colorida de um estacionamento, capturada por câmera fixa, e as coordenadas das vagas.
**Saída:** para cada vaga, a classe **livre (0)** ou **ocupada (1)**.

## 3. Objetivos

### 3.1 Objetivo geral

Desenvolver e avaliar uma solução em Python e OpenCV para classificar vagas de estacionamento previamente delimitadas como livres ou ocupadas.

### 3.2 Objetivos específicos

- Selecionar imagens de estacionamentos capturadas por câmeras fixas.
- Delimitar as regiões correspondentes às vagas.
- Extrair as regiões de interesse (ROI) das imagens.
- Aplicar pré-processamento, segmentação e morfologia matemática.
- Calcular características visuais (desvio-padrão, densidade de bordas, área da máscara e componentes conexos).
- Classificar as vagas por limiar.
- Comparar os resultados com rótulos de referência por meio de métricas quantitativas e análise de erros.

## 4. Escopo

### 4.1 Mudanças em relação à M1

| Aspecto | Proposta da M1 | Proposta atual (M2) | Motivo |
|---|---|---|---|
| Linguagem | Java + OpenCV | Python + OpenCV | Menor complexidade e mais rapidez para experimentar |
| Localização das vagas | Detecção automática (contornos e filtragem retangular) | Delimitação manual (`cv2.selectROI`) em uma imagem de referência | Devolutiva da M1: escopo ambicioso demais |
| Padronização das ROIs | Redimensionamento para 100×50 px | Cada ROI mantém seu tamanho original; os atributos são normalizados pela área | Evitar distorção dos recortes |
| Atributo de classificação | Desvio-padrão | Comparação entre cinco atributos; densidade de bordas adotada | Melhor desempenho experimental |
| Parâmetros | Valores de exemplo, sem base nas imagens | Limiar obtido nos dados; demais parâmetros a comparar experimentalmente | Devolutiva da M1: parâmetros arbitrários |
| Avaliação | Não definida | Rótulos manuais e métricas (acurácia, precisão, revocação, especificidade, F1) | Devolutiva da M1: faltava protocolo |

### 4.2 Dentro do escopo mínimo (M2)

- Vagas delimitadas manualmente, uma única câmera fixa.
- Classificação binária (livre/ocupada) por limiar sobre um atributo.
- Avaliação quantitativa com rótulos de referência.
- Interface gráfica para executar os testes e o pipeline e exibir as métricas.

### 4.3 Fora do escopo mínimo

- Detecção automática das vagas (pode ser investigada na M3).
- Várias câmeras ou mudança de perspectiva.
- Processamento de vídeo em tempo real.
- Classificadores com aprendizado de máquina.

## 5. Conjunto de imagens

| Item | Descrição |
|---|---|
| Fonte | Dataset PKLot — https://web.inf.ufpr.br/luizoliveira/research-interests/pklot/ |
| Câmera | Uma única câmera fixa, com vista elevada do estacionamento |
| Subconjunto do PKLot | PUCPR] |
| Quantidade | 5 imagens (`images/input/0.png` a `4.png`) |
| Resolução | 1280 × 720 pixels, 3 canais (BGR) |
| Condições | Diferentes iluminações (incluindo sombra forte) e diferentes níveis de ocupação |
| Imagem de referência | `3.png` (estacionamento vazio), usada na delimitação das vagas |
| Critério de seleção | Imagens que acreditamos que seja da mesma câmera, pelas imagens, para que as coordenadas das vagas valham para todas, com variação de iluminação (com e sem sombra) e de ocupação (fileira vazia e com 1 a 3 vagas ocupadas), incluindo uma imagem vazia para servir de referência |
| Vagas analisadas | 6 vagas de uma mesma fileira (`vaga_01` a `vaga_06`) |
| Amostras | 30 (5 imagens × 6 vagas) |
| Rótulos | Manuais (`annotations/rotulos.csv`): 7 ocupadas e 23 livres |

Os retângulos das vagas terminam logo acima da faixa de grama (y = 308), para não incluir os veículos da fileira seguinte. A exceção é a `vaga_03`, que vai até y = 322.

## 6. Pipeline

Os diagramas estão em [`Diagrama_Pipeline.jpg`](../Diagrama_Pipeline.jpg) (visão geral) e [`Diagrama_Arquitetura.md`](../Diagrama_Arquitetura.md) (detalhado por etapa e por módulo).

| Etapa | Descrição | Módulo |
|---|---|---|
| 1. Delimitação das vagas | Seleção manual dos retângulos na imagem de referência | `anotar_vagas.py`, `delimitador_vagas.py` |
| 2. Rotulagem de referência | Cada recorte é rotulado pelo teclado (0 = livre, 1 = ocupada) | `rotular_vagas.py` |
| 3. Extração das ROIs | Recorte das vagas a partir das coordenadas do JSON | `delimitador_vagas.py` |
| 4. Pré-processamento | Tons de cinza → CLAHE (opcional) → suavização gaussiana | `processamento.py` |
| 5. Segmentação e morfologia | Canny → fechamento → abertura → componentes conexos | `processamento.py` |
| 6. Características | `desvio_padrao`, `densidade_bordas`, `area_mascara`, `maior_componente`, `num_componentes` | `processamento.py` |
| 7. Classificação | Ocupada se atributo ≥ limiar | `pipeline.py` |
| 8. Avaliação | Matriz de confusão e métricas | `interface.py` |

## 7. Parâmetros e origem

| Parâmetro | Valor atual | Origem |
|---|---|---|
| Atributo de classificação | `densidade_bordas` | Maior acurácia e F1 na comparação entre os cinco atributos |
| Limiar | 0,076 | Ponto médio entre a maior densidade das vagas livres (≈ 0,070) e a menor das ocupadas detectáveis (≈ 0,082) |
| Suavização gaussiana | 5 × 5 | Valor inicial; será comparado com outros tamanhos (ver Seção 8) |
| Canny (mín./máx.) | 50 / 150 | Valor inicial (razão 1:3, usual para o Canny); será comparado experimentalmente |
| Fechamento | elipse 5 × 5 | Valor inicial; será comparado experimentalmente |
| Abertura | elipse 3 × 3 | Valor inicial; será comparado experimentalmente |
| Área mínima de componente | 20 px | Valor inicial; será comparado experimentalmente |
| CLAHE | desligado | Opção avaliada como variação do pré-processamento |

## 8. Protocolo experimental

| Elemento | Definição |
|---|---|
| Pergunta | O desvio-padrão e a densidade de bordas separam vagas livres de ocupadas? Qual limiar separa melhor? |
| Amostra | 5 imagens de uma mesma câmera do PKLot, 6 vagas delimitadas manualmente (30 amostras) |
| Método principal | Recorte da vaga, pré-processamento, Canny, morfologia, extração de características e classificação por limiar |
| Configurações comparadas | Atributos de classificação; limiares do Canny; tamanhos dos kernels morfológicos; com e sem morfologia; com e sem CLAHE |
| Métricas | Acurácia, precisão, revocação, especificidade e F1 (classe positiva = ocupada) |
| Registro dos resultados | `data/results/caracteristicas.csv`, `parametros.json`, `metricas.txt`, imagens classificadas e painéis das etapas intermediárias |
| Análise de erros | Lista das vagas classificadas incorretamente, com o valor do atributo e a provável causa |

### 8.1 Definição das métricas

Com VP = verdadeiro positivo, FP = falso positivo, FN = falso negativo e VN = verdadeiro negativo:

| Métrica | Fórmula | O que indica |
|---|---|---|
| Acurácia | (VP + VN) / (VP + FP + FN + VN) | Fração de vagas classificadas corretamente |
| Precisão | VP / (VP + FP) | Das vagas apontadas como ocupadas, quantas realmente estão |
| Revocação | VP / (VP + FN) | Das vagas ocupadas, quantas foram detectadas |
| Especificidade | VN / (VN + FP) | Das vagas livres, quantas foram reconhecidas como livres |
| F1 | 2 · Precisão · Revocação / (Precisão + Revocação) | Equilíbrio entre precisão e revocação |

## 9. Riscos e limitações

- Dependência de vagas previamente delimitadas; mudar a câmera ou a perspectiva exige recalibrar as coordenadas.
- Sensibilidade a sombras, à iluminação e às condições climáticas.
- Veículos escuros ou com cor parecida com a do piso geram poucas bordas e podem ser classificados como livres.
- Oclusões e veículos parcialmente posicionados nas vagas.
- Conjunto pequeno (30 amostras, 7 ocupadas) e sem divisão entre calibração e avaliação; os limiares são ajustados nas mesmas imagens avaliadas, então os resultados são otimistas.

## 10. Próximos passos (M3)

- Ampliar o conjunto de imagens e separar calibração e avaliação.
- Investigar a detecção automática das vagas.
- Avaliar a combinação de atributos.

## 11. Referências

- DE ALMEIDA, P. R. L.; OLIVEIRA, L. S.; BRITTO JR., A. S.; SILVA JR., E. J.; KOERICH, A. L. PKLot – A robust dataset for parking lot classification. *Expert Systems with Applications*, v. 42, n. 11, p. 4937–4949, 2015.
- CANNY, J. A computational approach to edge detection. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, v. PAMI-8, n. 6, p. 679–698, 1986.
- GONZALEZ, R. C.; WOODS, R. E. *Processamento digital de imagens*. 3. ed. São Paulo: Pearson Prentice Hall, 2010.
- ZUIDERVELD, K. Contrast limited adaptive histogram equalization. In: HECKBERT, P. (ed.). *Graphics Gems IV*. San Diego: Academic Press, 1994. p. 474–485.
- OPENCV. *OpenCV documentation*. Disponível em: https://docs.opencv.org/. Acesso em: out. 2026.
