# Categorias, foco e estabilidade da capa

- Capa: roda do mouse, gesto touch e teclas de rolagem no HTML não deslocam mais seu conteúdo em relação ao botão nativo. Não foi alterada a navegação ou a geometria do botão. A rolagem da análise continua disponível.
- Conferência no Power BI real: capa permaneceu estável após scroll; Ctrl+Enter no botão abriu a análise. Categoria de tipos também conferida no visual real.
- Tipos agrupados na apresentação em quatro famílias: Colisões e engavetamentos; Atropelamentos; Saída, capotamento e tombamento; Outros tipos. Os 18 tipos da fonte permanecem selecionáveis; selecionar o grupo equivale à união de seus tipos. Não foram criadas causas presumidas ou alterações no modelo/Gold.
- Três botões de foco: Mais ocorrências; Maior % grave/fatal; Menor % grave/fatal. Mudam a seleção dos dez trechos da tabela e o trecho da leitura executiva. Cards e demais gráficos continuam mostrando o mesmo recorte, sem filtros ocultos.
- Volume ordena por ocorrências; proporção ordena por graves/fatais divididos por ocorrências. Desempates da seleção usam volume e chave. Os cabeçalhos continuam ordenando dentro da seleção de até dez trechos.
- Não foi inventado limite mínimo de amostra. Contagens e aviso sobre instabilidade de amostras pequenas ficam visíveis. “Menor proporção” sugere comparar contextos; não declara um trecho seguro nem interpreta o percentual como risco por veículo. Trechos sem ocorrências no contexto não entram nos rankings.
- 26 verificações específicas e 91 de regressão aprovadas. Verificaram agrupamentos, união dos tipos, seleção e ordenação dos focos, KPIs invariantes, filtros, aviso interpretativo, responsividade, estabilidade da capa e resultado do anel.
- Medidas HTML Dashboard PRF e HTML Capa PRF atualizadas via MCP, com backups ocultos anteriores. Ambas Ready; JSON Gold com expressão idêntica. PBIX não salvo. Fontes anteriores em dashboard/backup-pre-refinamento.

A borda amarela informada pelo usuário é compatível com o indicador de captura do Windows.Graphics.Capture usado na conferência da janela. A documentação da Microsoft explica esse indicador: https://learn.microsoft.com/en-us/windows/apps/develop/media-authoring-processing/screen-capture . A origem específica da borda no monitor do usuário não pode ser confirmada somente pela imagem capturada da janela.

A EULA aceita com autorização do usuário foi a do Power BI Authoring MCP: https://go.microsoft.com/fwlink/?LinkId=2381247 . Trata-se do aceite necessário para habilitar o conector, distinto do indicador de captura da interface.
