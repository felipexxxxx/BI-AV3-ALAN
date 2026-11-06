# Navegação nativa e resolução das páginas

Configuração realizada diretamente na interface do Power BI Desktop aberto, com a skill computer-use.

- Página 1 (capa) e Página 2 (análise): formato 16:9, tamanho 1280 × 720 (HD), em substituição a 1920 × 1080.
- Ambos os visuais HTML: largura 1280, altura 720, posição horizontal 0 e vertical 0. Exibição ajustada à página.
- Capa: apresentação desktop compactada para caber na altura disponível, mantendo números, identidade, animações e fonte. Backup oculto da medida anterior criado antes da alteração. JSON e medidas de negócio preservados.
- Botão nativo criado sobre a área inferior direita da capa: “Ir para Análise →”, tamanho 200 × 48, posição 1036 × 591. Ação ativada, tipo Navegação na página, destino Página 2.
- Navegação testada com o botão selecionado e Ctrl+Enter: o Power BI abriu a Página 2. No modo de edição também é possível usar Ctrl+clique, conforme a indicação do próprio Desktop.
- A análise mantém rolagem interna. Rolagem testada no visual real, permitindo acessar o gráfico, rankings, consequências por pista e tabela sem mudar a resolução da página.
- Capa conferida visualmente no custom visual real: título, anel 35,0%, 5.513 ocorrências, 574 mortes, 6.164 feridos, período, fonte, rodapé e botão visíveis.

O PBIX não foi salvo nem sobrescrito pelo agente. As alterações de páginas, visual e botão permanecem na sessão aberta do Desktop.
