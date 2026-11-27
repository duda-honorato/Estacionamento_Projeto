ENTRADA
A[Imagem PNG]

FASE 1: DETECÇÃO E DELIMITAÇÃO DAS VAGAS
        A --> B[Pré-processamento]
        B --> C[Detecção de Contornos]
        C --> D[Filtragem Retangular]
        D --> E[Organização Espacial]
        E --> F[Mapa de Vagas<br/>HashMap{ID → Rect}]

FASE 2: EXTRAÇÃO E PRÉ-PROCESSAMENTO
        F --> G[Recorte ROI]
        G --> H[Redimensionamento]
        H --> I[Equalização de Histograma]
        I --> J[Imagens Padronizadas<br/>100x50 px]

FASE 3: CLASSIFICAÇÃO
        J --> K[Extração de Características]
        K --> L[Cálculo Desvio Padrão]
        L --> M[Aplicação Limiar]
        M --> N{Classificação}

SAÍDA
        N -->|Desvio ≤ Limiar| O[Livre = 0]
        N -->|Desvio > Limiar| P[ Ocupada = 1]
        O --> R[Status Consolidado<br/>HashMap{ID → Boolean}]
        P --> R [Status Consolidado<br/>HashMap{ID → Boolean}]
