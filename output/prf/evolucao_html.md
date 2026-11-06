# Evolução do dashboard HTML PRF

## Entrega e preservação

A medida **HTML Dashboard PRF** foi atualizada diretamente no Power BI Desktop aberto, pela conexão MCP. Estado final: **Ready**. O nome mantém a adaptação já adotada para a PRF; não foi criada uma segunda medida com o nome do exemplo logístico.

Foi criada antes da alteração a cópia oculta **HTML Dashboard PRF Backup Antes Evolucao**, em `99 Backup`. A expressão da cópia é idêntica à versão funcional anterior. Os arquivos de apresentação anteriores estão em `dashboard/backup-pre-evolucao`.

A comparação das 50 medidas anteriores encontrou alteração de expressão somente em **HTML Dashboard PRF**. O JSON Gold, as 47 medidas de negócio e o backup anterior permaneceram iguais. Os oito relacionamentos também permaneceram iguais. Não houve alteração de dados, consultas, chaves ou regras de negócio nesta etapa.

O arquivo **BI.pbix não foi salvo nem sobrescrito**. SHA-256 do arquivo em disco, igual ao início: `5a7b56aa296c206012b2961f8fe9ed2a478cadfe03cf2b61d8c7fcb21f9d1212`. As alterações estão na sessão aberta do Desktop.

## Adaptação do pedido à base

| Elemento do exemplo logístico | Implementação sustentada pelos dados PRF |
|---|---|
| Transportadora que exige atenção | Rodovia e município com mais ocorrências graves/fatais; trecho prioritário apresentado separadamente |
| Região e categorias | Município, rodovia, tipo de acidente, fase do dia, causa registrada e tipo de pista |
| Pedidos e OTIF mensais | Ocorrências e percentual de ocorrências graves/fatais |
| Produtos e motivos de atraso | Tipos de acidente e causas registradas pela PRF |
| Comparativo de transportadoras | Comparativo dos dez trechos com mais ocorrências |
| Risco por modal | Consequências observadas por tipo de pista |

Custos, lead time, atrasos, produtos, transportadoras e OTIF não existem nesta base. Não foram criados substitutos fictícios nem alterado o JSON para incluí-los.

## O que mudou

- **Leitura executiva:** recalcula trecho, rodovia, município, causa mais registrada e alertas de qualidade após cada filtro. A prioridade usa quantidade absoluta de ocorrências graves/fatais, com desempate por volume e chave. Os textos descrevem concentração e indicam investigação/vistoria, sem afirmar causalidade.
- **Gráfico mensal:** barras de ocorrências, linha de percentual grave/fatal, eixos nomeados e mediana mensal tracejada. O tooltip acrescenta feridos, mortes, qualidade e diferença em pontos percentuais para a média ponderada do contexto. Um único mês continua visível e recebe mensagem específica.
- **Rankings:** preservados municípios e tipos de acidente por volume; adicionadas causas por volume e rodovias por proporção grave/fatal, da maior para a menor. Tooltips exibem tamanho da amostra, participação, gravidade e vítimas.
- **Tipo de pista:** cards separados com ocorrências, gravidade, feridos e mortes. Os estados são fatos observados: “Há mortes registradas”, “Há feridos graves” ou “Sem graves/fatais registrados”. Cor, símbolo e texto comunicam o estado. O alerta informa quantos tipos de pista têm mortes no recorte.
- **Tabela:** ordenação crescente e decrescente em trecho, acidentes, graves/fatais, percentual, feridos e mortes. Cabeçalhos possuem botões, indicador de direção e `aria-sort`. A seleção permanece sendo os dez trechos com mais ocorrências; ordenar reorganiza essa seleção. A ordenação persiste ao filtrar.
- **Filtros:** preservados mês, município, tipo, rodovia e fase; adicionados causa registrada e tipo de pista. Todos são combináveis, derivados da própria base e atualizam os componentes dependentes. Limpar redefine apenas os filtros internos.
- **Apresentação:** preservados temas claro/escuro, estados vazio/erro, tooltips, interação nos rankings e no gráfico e seleções da sessão. Ajustes de largura evitam transbordamento horizontal entre 320 e 1440 pixels.

Não há limites de risco confirmados no JSON. Portanto, os cards não classificam pistas como saudáveis, em atenção ou críticas. Também não existe volume de tráfego para estimar risco por veículo. Causas registradas não demonstram causalidade.

## Contrato consumido e cálculos

Fonte única: **[JSON Gold Dashboard PRF]**, sem alteração.

Objetos utilizados: `meta`, `seriesMensais`, `localidades`, `trechos`, `condicoes`, `tipos`, `causas`, `gravidades` e `baseInterativa`. O HTML decodifica os dicionários locais de cada payload e usa os valores de rótulo para preservar seleções, sem depender da estabilidade das chaves numéricas entre filtros externos.

A base permanece em uma linha por ocorrência, com ID único. Campos granulares utilizados: ID, data, referências de localidade/trecho/tipo/causa/gravidade/condições, feridos, feridos graves, mortes e flags de qualidade.

- Grave/fatal: mesma regra já confirmada no modelo, feridos graves > 0 **ou** mortes > 0 na ocorrência.
- Percentual grave/fatal: ocorrências graves/fatais / ocorrências do contexto; sem denominador retorna ausência de proporção.
- Mediana: mediana das proporções mensais dos meses com ocorrências. Meses sem ocorrências têm proporção ausente e não entram no cálculo; meses com ocorrências e zero graves entram como zero.
- Média ponderada do contexto: total de graves/fatais / total de ocorrências. Não é média aritmética das proporções mensais.
- Comparação do tooltip: proporção mensal menos proporção agregada do contexto, expressa em pontos percentuais.
- Filtros externos: o HTML recebe apenas os registros já contidos no JSON do contexto Power BI. Limpar filtros internos não recupera registros excluídos externamente.
- Atualização exibida: data de carga do modelo, convertida para BRT. Não representa data de revisão dos arquivos pela PRF.

## Validação realizada

**266 verificações aprovadas:** 117 de regressão e 149 da evolução. Nenhum erro JavaScript e nenhuma requisição remota nos testes.

A regressão verificou totais, filtros isolados e combinados, limpeza, contexto externo, vazio/erro, temas, teclado e responsividade. A evolução verificou leitura executiva, rankings, estados descritivos, medianas, tooltips nas extremidades e no centro, mês único, todas as seis colunas nos dois sentidos, persistência de ordenação, foco e `aria-sort`. Contraste dos estados: 6,90:1 no escuro e 5,57:1 no claro.

Referências nativas DAX e resultados do HTML coincidiram:

| Contexto | Ocorrências | Mediana mensal | Proporção agregada |
|---|---:|---:|---:|
| Geral | 5.513 | 34,3780% | 35,0263% |
| Fortaleza | 1.720 | 27,8889% | 28,0233% |
| Alto Santo | 33 | 0% | 39,3939% |
| BR-116 | 3.389 | 33,3333% | 33,9923% |
| Janeiro/2025 | 92 | 32,6087% | 32,6087% |
| Plena noite | 1.888 | 41,1458% | 42,5847% |
| Causa: transitar no acostamento | 40 | 0% | 30% |
| Pista simples | 2.398 | 41,6667% | 41,7431% |
| Sem registros | 0 | Ausente | Ausente |

A execução final no Desktop confirmou 5.513 ocorrências, 1.931 graves/fatais e a mediana 0,34377967711301044. A expressão atual corresponde ao código gerado; o HTML retornado pelo DAX é exatamente a composição dos arquivos de apresentação com o Gold congelado, com 1.304.429 caracteres. O payload da prévia também corresponde ao Gold preservado.

Relatórios detalhados: `output/prf/validacao_html.md` e `output/prf/validacao_evolucao_html.md`. Evidências de integridade: `output/prf/auditoria_evolucao_html.json`. Prévia: `dashboard/preview_prf.html`. Imagens: `output/prf/evolucao_dark.png` e `evolucao_light.png`.

## Revisão visual

| Critério | Nota / 5 | Evidência |
|---|---:|---|
| Decisão e narrativa | 4 | Prioridade territorial, números de suporte e ação de investigação sem causalidade presumida |
| Hierarquia e legibilidade | 4 | KPIs, gráfico temporal e leitura executiva antes do detalhamento; rótulos e eixos explícitos |
| Adequação analítica | 4 | Volume e proporção em eixos identificados; mediana distinta da média ponderada; amostras visíveis |
| Coerência e identidade | 4 | Tokens e paleta consistentes nos dois temas, com acentos limitados |
| Densidade e estrutura | 4 | Visão principal seguida de causas, pistas e comparação; detalhes em tooltip |
| Interação e integridade | 4 | Filtros e ordenação testados, reconciliação DAX e contrato preservado |
| Acessibilidade e adaptação | 4 | Teclado, foco, aria-sort, estados por texto/símbolo, contraste e telas estreitas |

Na leitura executiva, os primeiros dados percebidos são ocorrências e gravidade. A decisão sustentada é escolher territórios para investigar e vistoriar. A comparação é descritiva; a ausência de exposição de tráfego impede converter concentração em risco de circulação.

## Validação ainda pendente no Power BI

O conector MCP utilizado opera o modelo semântico; não insere nem configura visuais na página. A renderização foi validada em **Microsoft Edge/Chromium**, incluindo os dois temas; falta verificar a execução dentro do custom visual real.

Visual necessário: **HTML Content Regular/Normal**, com JavaScript permitido, e não Lite/Secure. Colocar **[HTML Dashboard PRF]** em **Values** e deixar **Context/Granularity** vazio. Usar renderização HTML, Raw HTML desligado e reconstrução na atualização de dados. Na configuração por templates da versão 2.x, corpo `{{content}}` e linha `{{row}}`.

Na página real, conferir altura/rolagem vertical do visual, filtros externos, execução dos scripts, tema, tooltips, ordenação e recorte vazio. O HTML contém cerca de 1,3 milhão de caracteres e 5.513 registros no contexto geral; desempenho e limites do host ainda dependem dessa validação. Os filtros internos afetam os componentes deste HTML; não enviam seleção aos demais visuais do relatório.

Esta etapa não cria relatório acadêmico nem slides.
