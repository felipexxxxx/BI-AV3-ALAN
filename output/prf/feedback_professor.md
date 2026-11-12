# Evolução a partir do feedback do professor

## Interações

- Período: árvore ano → mês, com checkboxes de anos completos ou meses individuais, seleção múltipla e busca por palavras (ex.: jan 2025).
- Rodovia/trecho: árvore BR → trechos de 10 km, com busca e seleção múltipla. Selecionar uma BR inclui seus trechos disponíveis; é possível refinar nos filhos.
- Município, tipo, fase, causa e pista: pesquisa sem diferenciar acentos/caixa e seleção múltipla.
- União (OU) dentro de cada filtro; interseção (E) entre filtros. Sem escolha significa todos, sempre limitado ao Gold recebido dos filtros externos.
- Clique normal no gráfico substitui a seleção daquela dimensão. Ctrl+clique adiciona/remove; Ctrl+Enter e Ctrl+Espaço também combinam meses. Rankings usam a mesma lógica de seleção múltipla.
- O gráfico mensal preserva os meses do contexto de referência para permitir novas seleções por clique. Meses selecionados têm destaque/aria-pressed; cards, análises, mediana e sparklines usam os meses selecionados. Os valores exibidos nos meses fora da seleção continuam sendo os do contexto sem o filtro interno de mês. Não confundir o total das barras de referência com o total dos cards filtrados.
- Badges mensais continuam comparando o mês selecionado, ou o último mês da seleção, com seu mês civil anterior disponível no Gold, mantendo os demais filtros. O período está escrito no badge; não é variação entre totais de conjuntos arbitrários de meses.
- Clicar no nome do trecho na tabela afunila o painel inteiro. Foram mantidos top 10 e ordenação; não adicionamos uma interface semelhante a planilha, para evitar duplicar filtros e confundir o usuário.
- Limpar tudo e limpar somente o filtro, fechar com Escape, foco e estados vazios preservados.

## Decisão: evidência → comparação → ação → confirmação

O painel “Onde agir e por quê” identifica o trecho com mais ocorrências graves/fatais no contexto, com desempate por volume e chave. Mostra volume, mortes, tipo com mais graves/fatais, causa mais frequente e uma ação de vistoria relacionada ao tipo observado.

A comparação noite/dia mantém trecho, período e demais filtros, retirando explicitamente **apenas fase do dia** para evitar comparar uma fase com um denominador impossível. Exibe graves/total, percentual e diferença em pontos percentuais; ausência de ocorrências em uma das fases impede a comparação. Não usa volume de veículos nem estima risco por viagem.

Exemplo conferido no DAX nativo, BR-116, km 0 a menos de 10, 2021–2025:

| Fase | Acidentes | Graves/fatais | Proporção |
|---|---:|---:|---:|
| Pleno dia | 515 | 103 | 20,0% |
| Plena noite | 264 | 97 | 36,7% |

Há mais acidentes diurnos em quantidade, mas maior proporção de consequências graves à noite: diferença de 16,7 p.p. A evidência apoia priorizar investigação e vistoria das condições noturnas; não demonstra que a noite ou buracos tenham causado os acidentes.

As ações diferem por tipo: pedestre → travessias/acessos/visibilidade; animal → pontos de entrada/presença; traseira → aproximações/filas/sinalização/distância; transversal/lateral → acessos/cruzamentos/conflitos. São encaminhamentos de investigação, não prescrições de obra ou alegações causais. Registros cuja causa menciona defeito de via/pavimento são quantificados separadamente, sem transformar essa menção em causa geral de todos os acidentes. Na ausência dessa menção, o texto proíbe atribuir o padrão a buracos.

## Preservação e testes

- Atualizada somente **HTML Dashboard PRF**; backup oculto anterior criado pelo MCP. Gold com expressão idêntica; modelo, relações, medidas de negócio, capa e botão nativo preservados.
- 91 verificações da nova versão passaram: hierarquias, dois anos, vários meses, pesquisa, Ctrl, teclado, múltiplos municípios, filtros combinados, contagens/vítimas/proporções, tabela, decisão, vazio, limpeza, ordenação, temas, popups e larguras de 320 a 1280 px. Sem erros JavaScript ou requisições remotas.
- Seleção de 2024 + 2025: 2.281 ocorrências, reconciliada com os totais anuais da fonte.
- Verificação no custom visual real do Power BI: abertura do filtro, expansão de 2025, seleção do ano, atualização para 123 mortes/1.166 feridos e limpeza para o contexto geral.
- Medida em estado Ready; consultas DAX executadas, incluindo comparação noturna/diurna e contextos de múltiplos períodos.
- Arquivos: `scripts/validar_feedback_prf.mjs`, `output/prf/validacao_feedback.md`, `feedback_dark.png`, `feedback_light.png`; fontes anteriores em `dashboard/backup-pre-feedback`.
- Scripts antigos que usam selectOption nos antigos selects ou esperam um único mês descrevem a interface anterior. A suíte nova substitui esses contratos, sem declarar retrospectivamente sua execução como válida nesta versão.
- Revisão visual (1–5): decisão 4 (ação contextual e evidência); hierarquia 4; adequação analítica 4 (denominadores e escopo explícitos); identidade 4; densidade 4 (sete filtros, tabela simples); interação 4; acessibilidade 4 (teclado, texto, foco e adaptação).

O PBIX **não foi salvo**. Alteração aplicada à sessão aberta, com fontes locais atualizados; não houve commit/push nesta etapa. O aceite da nova EULA do MCP foi realizado somente após autorização expressa do usuário.
