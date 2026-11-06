# Sparklines nos cards PRF

Atualizada somente a apresentação da medida **HTML Dashboard PRF**, via MCP. Estado final **Ready**. Backup oculto: **HTML Dashboard PRF Backup Sparklines 2026-11-06T03-04-20-550Z**; expressão integral anterior confirmada. A expressão do JSON Gold permanece idêntica. A capa e as medidas de negócio não foram alteradas. O PBIX não foi salvo.

Os seis indicadores existentes receberam séries mensais próprias: ocorrências, proporção grave/fatal, mortes, feridos, proporção em plena noite e concentração nos cinco principais trechos. Não foram criados pedidos, OTIF, custos, lead time ou emissões, ausentes na base PRF.

Todos os cards usam os mesmos últimos 12 meses disponíveis no contexto do gráfico mensal. A seleção interna de um mês mostra somente esse mês. Os demais filtros são aplicados antes da agregação mensal; filtros externos continuam limitando o próprio Gold recebido. Contagens sem ocorrências são zero; proporções sem denominador são ausentes, com interrupção da linha, sem preenchimento artificial. A concentração top 5 é recalculada por mês com a regra existente. Um único período válido recebe somente o ponto, sem inventar uma trajetória.

Apresentação: SVG local, 80% da largura útil, 26 px de altura, linha azul-petróleo de 1,7 px, curvas cúbicas sem extrapolar os valores, preenchimento de opacidade máxima 12% até zero, somente o último ponto destacado. Sem eixos, grade, rótulos, legenda, novas animações ou tooltips. Cores dos badges preservadas.

Títulos, valores principais e textos auxiliares mantiveram suas posições relativas ao topo dos cards, verificadas contra a prévia anterior. O sparkline fica entre o auxiliar e o badge. Larguras, grade, alinhamentos e identidade preservados. A altura total aumentou cerca de 22 px para incluir o gráfico sem sobreposição; houve redução de espaços inferiores, preservando a fonte e o destaque do valor principal.

## Validação

- 57 verificações específicas e 117 de regressão aprovadas; nenhum erro JavaScript.
- Comparação antes/depois sem filtros, com município, mês, tipo/rodovia e contexto vazio: textos, números e badges idênticos; largura e posições dos textos principais preservadas.
- Séries mensais reconciliadas com os registros do Gold, cada indicador com sua própria agregação. Jan–dez/2025 no contexto geral; seleção mensal respeitada.
- Sparklines sem sobreposição, largura entre 75% e 85%, altura 26 px e último ponto único; temas Light/Dark inspecionados visualmente.
- Responsividade até 320 px sem transbordamento horizontal. Filtros e funcionalidades existentes passaram pela regressão.
- Consulta DAX final executada: 5.513 ocorrências, 1.931 graves/fatais; HTML retornado com 1.311.868 caracteres.
- Revisão visual (1–5): narrativa 4, hierarquia 4, adequação analítica 4, identidade 4, densidade 4, interação/integridade 4, acessibilidade/adaptação 4. As minisséries acrescentam contexto sem competir com os valores; os gráficos maiores continuam disponíveis para leitura temporal detalhada.

Evidências: `validacao_sparklines.md`, `validacao_html.md`, `sparklines_light.png`, `sparklines_dark.png`. Código anterior em `dashboard/backup-pre-sparklines`.

Validação visual realizada no navegador Edge. A execução no visual **HTML Content Regular/Normal** do Power BI ainda precisa de conferência, com **[HTML Dashboard PRF]** em Values. O conector MCP utilizado opera o modelo semântico.
