# Acabamento e capa PRF

## Criado e alterado

- Atualizada via MCP **HTML Dashboard PRF**; criada **HTML Capa PRF**. Ambas em estado **Ready**. Os nomes e a identidade seguem o tema PRF já adotado, em vez dos nomes logísticos do exemplo.
- Backup oculto integral anterior ao acabamento: **HTML Dashboard PRF Backup Acabamento 2026-11-06T02-58-29-609Z**. A capa não existia, portanto não havia uma versão anterior para copiar. Código anterior também em `dashboard/backup-pre-acabamento`.
- Estrada local decorativa, separada do header e dos controles, com `aria-hidden` e `pointer-events: none`. Veículos CSS com duas passagens e parada, sem loops infinitos.
- Ticker numerado dos quatro tipos de acidente mais frequentes no recorte. Recalcula pelos sete filtros, pausa no hover/foco, ajusta deslocamento ao espaço disponível e retorna à posição inicial. Produtos/vendas não existem na base.
- Barras e linhas entram uma vez por renderização; hover discreto em cards e gráficos. Somente a pequena variação desfavorável pulsa, por dois ciclos. Reduced-motion desliga movimentos.
- Variações nos seis cards, com mês de referência explícito. Contagens usam variação relativa; proporções usam pontos percentuais. Em acidentes, vítimas e proporção grave/fatal, aumento recebe sinal desfavorável vermelho e redução verde. Concentração top 5 fica neutra, pois seu crescimento não confirma piora. Ausência de mês anterior ou denominador válido não produz percentual inventado.
- A comparação usa o mês interno selecionado ou o último mês com registros, contra o mês civil imediatamente anterior, mantendo os outros filtros. Não recupera dados excluídos por filtros externos. O valor principal do card continua sendo o total/proporção do recorte inteiro, e a legenda mensal identifica a referência da variação.
- Tooltip HTML sem atributos title redundantes, limitado pela janela e pelo contêiner, posicionado acima do alvo quando há espaço. Fecha na saída, perda de foco e teclado. Em espaços pequenos pode cobrir parte do gráfico; o host real ainda precisa de conferência.
- Capa Dark com identidade Observatório viário · Ceará, frase de entrada, período, fonte/carga em BRT, ocorrências, mortes e feridos. Sem OTIF e lead time fictícios.
- Anel representa proporção grave/fatal do contexto, sem meta. Número e anel usam o mesmo progresso em requestAnimationFrame, de zero ao valor final formatado em pt-BR, sem modificar o KPI. Reduced-motion mostra imediatamente o valor final. Animação finita de 1,1 segundo; pode repetir se o Power BI recriar o visual.
- Tendência mensal e diferença em pontos percentuais entre o último mês com ocorrências e seu mês anterior. Meses sem denominador não geram proporção. Área inferior direita reservada para o botão nativo; não há botão HTML fingindo navegação.

## Preservado

Fonte única das duas medidas: **[JSON Gold Dashboard PRF]**. Sua expressão foi comparada antes/depois e permaneceu idêntica. Nenhuma medida de negócio, consulta ou relacionamento foi alterado. Filtros, temas, cálculos, mediana, leituras executivas, qualidade, tooltips, tabela e ordenação foram preservados e passaram pela regressão.

O arquivo BI.pbix não foi salvo nem sobrescrito. SHA-256 em disco: `5a7b56aa296c206012b2961f8fe9ed2a478cadfe03cf2b61d8c7fcb21f9d1212`. As alterações permanecem na sessão do Desktop.

## Validação

- 117 verificações de regressão e 149 da evolução anterior aprovadas após o acabamento; mais 38 específicas de acabamento/capa aprovadas. Total: **304 verificações**, sem erros JavaScript não tratados e sem requisições remotas.
- Análise nos temas Light/Dark; capa Dark; larguras desktop até 320 px sem transbordamento horizontal.
- Filtros e ticker combinados; tabela/aria-sort/teclado; tooltips e Escape; reduced-motion; anel/número sincronizados; estado vazio e JSON inválido; espaço do botão sem sobrepor a fonte.
- DAX nativo: 5.513 ocorrências, 1.931 graves/fatais e proporção 0,3502630146925449 (35,0% formatado). Novembro/2025: 67 ocorrências e 44,7761% graves/fatais; dezembro/2025: 68 e 36,7647%. Diferença: -8,0114 p.p., exibida na capa como -8,0 p.p.; crescimento das ocorrências: +1,5%.
- Saídas HTML executadas pelo DAX. A capa recebe 707 ocorrências no payload externo de 2025/BR-116 e comunica vazio sem percentual fictício.
- Evidências em `validacao_acabamento.md`, `validacao_html.md`, `validacao_evolucao_html.md`, `acabamento_light.png`, `acabamento_dark.png`, `capa_desktop.png` e `capa_mobile.png`.
- Avaliação visual de 1 a 5: decisão 4 (prioridade territorial explícita); hierarquia 4 (resumo antes da exploração); adequação analítica 4 (proporção separada de contagem, sem meta falsa); identidade 4 (tokens e dois temas coerentes); densidade 4 (capa sintética e análise detalhada); interação 4 (filtros e ordenação preservados); acessibilidade 4 (teclado, estados por texto, contraste e movimento reduzido). Nenhum eixo abaixo de 3.

## Limitações e instalação na página

A validação visual foi feita em Edge/Chromium. O MCP usado edita o modelo semântico; não cria páginas, insere custom visuals nem configura navegação nativa. Falta validar a execução no **HTML Content Regular/Normal**, com scripts permitidos. Lite/Secure é incompatível com estas medidas.

Usar **[HTML Capa PRF]** em Values no visual da capa e **[HTML Dashboard PRF]** em Values no visual da análise, sem Context/Granularity. Na versão 2.x, template de corpo `{{content}}`, linha `{{row}}`, renderização HTML, Raw HTML desligado e reconstrução ao atualizar dados.

Inserir manualmente um botão nativo **Ir para Análise** sobre a área reservada, com ação de navegação para a página da análise. No Desktop, conferir a altura disponível, rolagem vertical, filtros externos, tooltips, scripts e a navegação. Cada medida transmite aproximadamente 1,3 milhão de caracteres no contexto geral; o desempenho dentro do custom visual ainda precisa ser medido.

A referência visual do projeto Teste Logística não foi encontrada nos arquivos disponíveis; não foi possível declarar comparação direta com ela. A consistência foi avaliada contra a versão PRF anterior. Esta entrega não inclui relatório acadêmico nem slides.
