# Etapa intermediária — JSON Gold da PRF

Medida: `JSON Gold Dashboard PRF`, em `fAcidentes`, pasta `06 Apresentacao/JSON Gold`.

O JSON completo foi executado e analisado com um parser. O contrato contém `meta`, `kpis`, `seriesMensais`, `rankings`, `localidades`, `trechos`, `condicoes`, `tipos`, `causas`, `gravidades` e `baseInterativa`.

- 5.513 ocorrências, 5.513 IDs únicos, sem truncamento.
- 1.261.107 caracteres na fotografia sem filtros, após compactação dos campos categóricos com dicionários internos.
- 60 meses na série temporal; 41 localidades, 90 trechos, 1.043 combinações de condições da via.
- Todas as referências da base interativa aos dicionários são válidas.
- Contagens, feridos, mortes, gravidade, plena noite e alertas reconciliam com as medidas nativas.
- Séries mensais reconciliadas com os registros granulares.
- Contextos externos testados: geral; ano 2025 + BR-116 (707 ocorrências); janeiro/2025 + Fortaleza (26); recorte sem registros (zero, participações nulas).
- Nenhuma alteração das 47 medidas de negócio durante a criação do contrato.

O primeiro payload sem compactação excedeu o limite de texto DAX. O contrato foi compactado com dicionários, sem amostrar ou remover ocorrências. Uma formatação de inteiros com separador decimal sem fração também foi corrigida antes de finalizar o contrato.

Os índices numéricos dos dicionários são locais a cada payload; filtros persistem por atributos de negócio. Filtros internos seguros: mês, município, tipo de acidente, rodovia e fase do dia. Eles permitem recalcular todos os componentes a partir dos dados do mesmo JSON.

Não existem transportadora, modal logístico, custo, OTIF ou lead time. O HTML será adaptado a ocorrência, gravidade, vítimas, municípios, rodovias e condições da via. Atualização em UTC corresponde à carga do modelo; será exibida em America/Sao_Paulo.

Contrato congelado ao iniciar a etapa HTML. Nessa etapa, não alterar medidas de negócio, relacionamentos, modelo ou JSON Gold.

O PBIX original não contém visual customizado e o MCP disponível trabalha no modelo semântico. A medida HTML será destinada ao **HTML Content, edição Regular/Normal 2.x**. A renderização será validada em navegador com os mesmos dados extraídos da medida; a inserção e validação no visual real ficarão explicitamente identificadas se não forem possíveis pela conexão MCP.
