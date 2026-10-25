# Processamento de Imagens — 2026-02

## Atividade de revisão da M1 e plano de ação para a M2

## 1. Finalidade da atividade

Nesta atividade, cada grupo deverá revisar cuidadosamente a devolutiva recebida na etapa M1 do Projeto Aplicado. O objetivo não é apenas informar se o grupo “gostou” ou “não gostou” da avaliação, mas verificar se:

- os critérios da rubrica foram aplicados de forma compreensível;
- as evidências consideradas correspondem ao material efetivamente entregue;
- as pontuações foram somadas corretamente;
- a nota registrada no diário corresponde ao resultado da avaliação;
- as críticas e orientações foram transformadas em ações concretas para a M2.

A atividade também marca a transição entre as etapas. Na M1, o grupo definiu e delimitou o problema, apresentou as imagens, propôs o pipeline e reuniu evidências iniciais de viabilidade. Na M2, deverá avançar para uma implementação inicial executável, com segmentação, morfologia, extração de características, experimentos e análise de resultados.

## 2. Natureza da revisão

A revisão deve ser realizada com base em evidências. Uma discordância precisa indicar exatamente:

- o critério questionado;
- a pontuação ou o nível atribuído;
- o trecho da devolutiva relacionado;
- a evidência que já estava presente na entrega da M1;
- o arquivo, seção, figura, vídeo ou endereço em que essa evidência pode ser localizada;
- a alteração solicitada pelo grupo e sua justificativa.

Não serão consideradas justificativas suficientes afirmações genéricas, como “fizemos tudo”, “a nota está baixa” ou “não concordamos”. Da mesma forma, materiais criados ou alterados depois do prazo da M1 não comprovam, por si mesmos, o que estava presente na entrega avaliada. Eles podem, entretanto, ser incorporados ao plano de correção para a M2.

Esta atividade permite identificar erros de cálculo, transcrição ou interpretação. A entrega da atividade não implica alteração automática da nota.

## 3. Organização da atividade

O grupo deverá produzir um único documento em Markdown, no repositório do projeto, com o nome sugerido:

```text
docs/revisao_m1_plano_m2.md
```

O documento deverá conter as seções apresentadas a seguir.

---

## 4. Parte A — Identificação da equipe e dos materiais conferidos

Preencham os dados abaixo.

| Item | Informação |
|---|---|
| Identificação do grupo |Detecção de Vagas Disponíveis em Estacionamento|
| Integrantes |João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|
| Repositório avaliado |https://github.com/duda-honorato/M1_Pt1|
| Commit, versão ou estado da entrega M1 |62d8ecb0a05557ef02242a8514a6f7a0fa469f4d|
| Documento de feedback consultado |grupo_04.pdf (devolutiva M1)|
| Data da conferência |19/09/2026|
| Nota informada na devolutiva |63,75 (após vídeo) / 50,00 subtotal técnico|
| Nota registrada no diário |6.40|

O grupo deve conferir o mesmo estado do repositório que foi considerado na avaliação. Se isso não puder ser determinado, a situação deverá ser registrada no documento.

## 5. Parte B — Resposta ao feedback

Leiam toda a devolutiva antes de responder aos itens separadamente. Depois, classifiquem cada observação recebida.

| Nº | Síntese da observação recebida | Classificação do grupo | Evidência ou justificativa | Ação decorrente |
|---:|---|---|---|---|
| 1 |Escopo ambicioso: detecção automática de vagas + classificação aumenta o risco| Concordamos|O README realmente propõe as duas etapas, e nenhuma foi executada ainda|Retirar a detecção automática do escopo mínimo da M2; usar delimitação manual das vagas|
| 2 |Parâmetros em pixels são exemplos arbitrários, sem base nas imagens| Concordamos|As faixas numéricas no README não citam origem experimental|Substituir todos os valores por parâmetros obtidos em experimentos com imagens reais|
| 3 |Projeto "ainda não foi iniciado" — não há experimento de viabilidade| Concordamos|O próprio README assume que o projeto não foi iniciado|Rodar baseline com poucas imagens da mesma câmera, medindo std e/ou densidade de bordas|
| 4 |Pouca caracterização e rastreabilidade das amostras de imagem| Concordamos parcialmente|Há link do Kaggle, mas sem descrição de câmera, resolução, quantidade ou seleção|Documentar câmera, resolução, quantidade e critério de seleção das imagens|
| 5 |Faltam métricas e protocolo de avaliação|Concordamos|A devolutiva M1 não define acurácia, precision/recall ou protocolo|Definir protocolo experimental mínimo na M2|
| 6 |	Repositório concentrado no README; diagramas sem nome/extensão; sem reprodução|Concordamos|Formatação precisa de revisão|Revisar acabamento e criar arquivo de proposta dedicado|
| 7 |Markdown com problemas de acabamento e falta de proposta separada|Concordamos|Formatação precisa de revisão|Revisar acabamento e criar arquivo de proposta dedicado|
| 8 |Histórico de commits concentrado em 01/09|Concordamos|	Git log mostra um único dia de atividade|Fazer commits distribuídos ao longo da M2, refletindo o progresso real|
| 9 |Situação administrativa: entrega como rascunho não enviado|Concordamos|Registro na planilha confirma "rascunho (não enviado)"|Regularizar a entrega no AVA antes da continuidade|
*Ainda nao entedemos o que nao esta regularizado no Item 9

### 5.1 Síntese da posição do grupo

Ao final desta parte, escrevam um parágrafo respondendo:

1. Quais pontos da avaliação foram compreendidos e aceitos?
O grupo reconhece que o escopo estava ambicioso demais, que os parâmetros numéricos eram arbitrários, que não houve experimento de viabilidade e que a organização do repositório e o histórico de commits precisam melhorar. Também aceitamos que a entrega estava como rascunho e que isso precisa ser regularizado.
2. Quais pontos precisam de esclarecimento ou revisão
Precisamos conversar sobre o AVA.
3. Qual crítica terá maior impacto técnico sobre a continuidade do projeto?
a ausência de experimento de viabilidade. É ela que sustenta todo o resto — sem provar que as características escolhidas (std, densidade de bordas) separam vagas livres de ocupadas, o pipeline da M2 fica sem base empírica.

## 6. Parte C — Conferência das pontuações

Reproduzam os critérios, pesos, níveis e pontos exatamente como aparecem na ficha de avaliação recebida.

| Critério | Peso ou valor máximo | Nível atribuído | Pontuação registrada | Pontuação recalculada pelo grupo | Diferença |
|---|---:|---|---:|---:|---:|
| 1 - Problema | 15 | Adequado | 11,25 | 11,25 | 0 |
| 2 - Imagens e dados | 10 | Parcial | 5,00 | 5,00 | 0 |
| 3 - Objetivos e sucesso | 10 | Adequado | 7,50 | 7,50 | 0 |
| 4 - Pipeline | 15 | Adequado | 11,25 | 11,25 | 0 |
| 5 - Viabilidade | 15 | Insuficiente | 3,75 | 3,75 | 0 |
| 6 - Repositório | 10 | Parcial | 5,00 | 5,00 | 0 |
| 7 - Markdown | 10 | Parcial | 5,00 | 5,00 | 0 |
| 8 - Vídeo | 10 | Adequado | 10,00 | 10,00 | 0 |
| 9 - Histórico | 5 | Insuficiente (situação explicada) | 5,00 | 5,00 | 0 |
| **Total** | **100** | — | **63,75** | **63,75** | **0** |

### 6.1 Resultado da conferência aritmética

Assinalem uma opção e expliquem quando necessário:

- [X] A soma está correta e coincide com a nota da devolutiva.
- [ ] Foi identificada uma possível divergência na soma.
- [ ] Não foi possível reproduzir a soma; o grupo solicita esclarecimento sobre o cálculo.

## 7. Parte D — Conferência da nota registrada no diário

Compare a nota final conferida na Parte C com a nota registrada no diário.

| Verificação | Valor |
|---|---:|
| Nota recalculada a partir da ficha |6.4|
| Nota apresentada na devolutiva |6.4|
| Nota registrada no diário |6.4|
| Diferença identificada |0|

Assinalem uma opção:

- [X] A nota registrada no diário está correta.
- [ ] A nota registrada no diário parece diferente da nota da devolutiva.
- [ ] O grupo ainda não conseguiu consultar ou confirmar o registro.

## 8. Parte E — Diagnóstico da situação atual

Antes de elaborar o plano da M2, classifiquem a situação dos principais componentes do projeto.

| Componente | Situação atual | Evidência existente | Lacuna identificada |
|---|---|---|---|
| Definição e delimitação do problema | Adequado |README descreve contexto e saída binária|Inexistente|
| Objetivo e saída esperada | Adequado |Entrada/saída definidas|Faltam métricas e protocolo|
| Conjunto inicial de imagens | Adequado |Link do Kaggle|Sem caracterização nem rastreabilidade|
| Pipeline proposto | Adequado |Etapas detalhadas|Parâmetros sem evidência experimental|
| Evidência de viabilidade |  Ausente |Nenhum experimento executado|Precisa rodar baseline|
| Fundamentação e referências | Parcial |Referências citadas|Aprofundar justificativa dos métodos|
| Organização do repositório | Parcial |README + diagramas|Separar arquivos, nomear figuras, instruções|
| Relatório técnico | Parcial |README faz esse papel|Criar relatório separado|
| Página parcial do projeto | Ausente |Ausente|Criar página do projeto|
| Registro de decisões e limitações | Parcial |README + Devolutiva|Executar as mudancas sugeridas na devolutiva|

## 9. Parte F — Plano de ação para a M2

O plano deverá separar dois tipos de trabalho:

1. **ajustes herdados da M1**, necessários para corrigir ou consolidar a proposta;
2. **novos desenvolvimentos da M2**, necessários para avançar tecnicamente o projeto.

Corrigir apenas a documentação da M1 não caracteriza, isoladamente, o desenvolvimento esperado para a M2.

### 9.1 Ajustes herdados da M1

Transformem cada crítica relevante em uma tarefa verificável.

| Prioridade | Problema identificado na M1 | Ação de correção | Responsável | Prazo | Evidência de conclusão |
|---|---|---|---|---|---|
| Essencial |Sem experimento de viabilidade|Rodar baseline com 5–10 imagens da mesma câmera (std + densidade de bordas)|Maria Eduarda de Melo Honorato|27/09/2026|Notebook + gráfico de separação livre/ocupado|
| Essencial |Escopo ambicioso|Remover detecção automática do mínimo; usar vagas delimitadas manualmente|Scheila Carolini da Silva Ceresa|27/09/2026|Seção atualizada na PROPOSTA.md|
| Essencial |Parâmetros arbitrários|Medir parâmetros nas imagens e documentar origem|João Matheus de Oliveira Vieira|27/09/2026|Tabela de parâmetros com origem experimental|
| Essencial |Entrega como rascunho|Regularizar envio no AVA|João Matheus de Oliveira Vieira|27/09/2026|Print/comprovante de envio|
| Importante |Falta de métricas|Definir acurácia e precision/recall|Maria Eduarda de Melo Honorato|27/09/2026 |Seção no protocolo experimental|
| Importante |Repositório desorganizado|Separar PROPOSTA.md, criar docs/, nomear figuras|Scheila Carolini da Silva Ceresa|27/09/2026|Estrutura de pastas no GitHub|
| Recomendável |Histórico concentrado|Fazer commits distribuídos na M2|Todos|Contínuo|Git log com múltiplos dias|

### 9.2 Novos desenvolvimentos da M2

| Entrega ou resultado da M2 | Tarefa concreta | Responsável principal | Colaboradores | Prazo | Evidência esperada | Dependências ou riscos |
|---|---|---|---|---|---|---|
| Implementação inicial executável |Script Python: recorte da vaga → cálculo de std e densidade de bordas → classificação|João Matheus de Oliveira Vieira|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Comando documentado e execução registrada |Sem risco|
| Segmentação |Aplicar limiarização/segmentação nas vagas recortadas|João Matheus de Oliveira Vieira|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Imagem de máscara/resultado e parâmetros |Sem risco|
| Morfologia matemática |Aplicar abertura/fechamento para limpar ruído|João Matheus de Oliveira Vieira|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Comparação antes/depois e justificativa |Sem risco|
| Extração de características |Calcular std, densidade de bordas, possivelmente cor média|Maria Eduarda de Melo Honorato|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Tabela, CSV ou registro dos descritores |Sem risco|
| Experimentos com parâmetros |Variar limiares e kernel morfológico|Maria Eduarda de Melo Honorato|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Configurações comparadas sob o mesmo protocolo |Sem risco|
| Testes e casos difíceis |Sombras, carros parciais, motos|João Matheus de Oliveira Vieira|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Imagens, resultados e análise de erros |Sem risco|
| Relatório técnico parcial |Atualizar relatório com métodos e resultados| |João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Texto atualizado com métodos e resultados |Sem risco|
| Página parcial |Criar página do projeto|Scheila Carolini da Silva Ceresa|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| Estado atual, comparação visual e próximos passos |Sem risco|
| Organização e reprodutibilidade |requirements.txt + instruções|Scheila Carolini da Silva Ceresa|João Matheus de Oliveira Vieira, Scheila Carolini da Silva Ceresa e Maria Eduarda de Melo Honorato|27/09/2026| README, dependências e comandos atualizados |Sem risco|

### 9.3 Protocolo experimental mínimo

| Elemento | Definição do grupo |
|---|---|
| Pergunta do experimento |Std e densidade de bordas separam vagas livres de ocupadas? Qual limiar melhor separa?|
| Imagens ou amostra utilizadas |5–10 imagens da mesma câmera (PKLot), com 4–6 vagas delimitadas manualmente|
| Método principal |Recorte da vaga + desvio-padrão dos pixels + densidade de bordas (Canny)|
| Configurações ou parâmetros comparados |Diferentes limiares de Canny e tamanhos de kernel morfológico|
| Resultado esperado |Separação visual entre vagas livres e ocupadas|
| Métrica ou critério de comparação |Acurácia, precision, recall|
| Forma de registrar os resultados |Tabela + gráfico de dispersão no relatório|
| Limitações já previstas |Sombras, iluminação variável, carros parciais, oclusão|

### 9.4 Distribuição das responsabilidades

| Integrante | Responsabilidades principais | Artefatos ou partes sob sua responsabilidade | Como o trabalho será validado pelo grupo |
|---|---|---|---|
|João Matheus de Oliveira Vieira|implementação do baseline|Notebook de extração de características|Revisão em grupo + execução por outro integrante|
|João Matheus de Oliveira Vieira|dataset e documentação|Seleção de imagens + PROPOSTA.md|Revisão em grupo|
|Maria Eduarda de Melo Honorato|experimentos e análise|Tabelas + gráficos|Revisão em grupo|
|Scheila Carolini da Silva Ceresa|relatório e reprodutibilidade|Relatório + requirements.txt|Revisão em grupo|

## 10. Parte G — Compromisso da equipe

> Declaramos que revisamos a devolutiva da M1, conferimos as pontuações e a nota registrada no diário, identificamos as correções necessárias e definimos um plano de ação para a M2. As discordâncias apresentadas neste documento estão acompanhadas de evidências localizáveis na entrega avaliada. Os integrantes conhecem as tarefas, os prazos e os resultados esperados para a próxima etapa.

Integrantes: Scheila Carolini da Silva Ceresa, João Matheus de Oliveira Vieira e Maria Eduarda de Melo Honorato.
Data: 20/09/2026.

## 11. Checklist antes da entrega

Antes de entregar, o grupo deverá verificar se:

- [X] identificou corretamente a equipe e a entrega avaliada;
- [X] respondeu a todas as observações relevantes do feedback;
- [X] diferenciou concordância, concordância parcial e discordância;
- [X] apresentou evidências para qualquer solicitação de revisão;
- [X] refez as somas da ficha de avaliação;
- [X] comparou a nota calculada, a nota da devolutiva e a nota do diário;
- [X] separou correções da M1 e novos desenvolvimentos da M2;
- [X] definiu tarefas, responsáveis, prazos e evidências de conclusão;
- [X] incluiu segmentação, morfologia, características e experimentação no plano da M2;
- [X] definiu um protocolo experimental mínimo;
- [X] registrou dependências, riscos e limitações;
- [X] confirmou que todos os integrantes compreendem o plano.

## 12. Critérios de verificação da atividade

Esta atividade será verificada considerando:

| Critério | Evidência esperada |
|---|---|
| Conferência da avaliação | Reprodução dos critérios, níveis, pontuações e cálculos. |
| Qualidade da resposta | Concordâncias e discordâncias justificadas com evidências. |
| Conferência do diário | Comparação explícita entre os três valores de nota. |
| Diagnóstico | Identificação realista de lacunas e prioridades. |
| Plano da M2 | Tarefas executáveis, responsáveis, prazos e resultados verificáveis. |
| Coerência técnica | Relação clara entre problema, segmentação, morfologia, características e experimentos. |
| Compromisso coletivo | Responsabilidades identificáveis e compreensão compartilhada do projeto. |

O preenchimento superficial das tabelas não atende à finalidade da atividade. O documento deverá permitir acompanhar, nas próximas revisões, o que foi concluído, o que permanece pendente e quais evidências foram produzidas.
