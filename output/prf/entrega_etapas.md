# Entrega das etapas autorizadas — PRF

## Resultado e escopo

Trabalho executado diretamente no Power BI Desktop aberto, conexão MCP `PBIDesktop-BI-58682`, arquivo `BI.pbix`. As etapas foram executadas em sequência: diagnóstico e download, Power Query e modelagem, medidas DAX, contrato JSON Gold, HTML Normal.

Tema: frequência e gravidade dos acidentes nas BRs 116 e 222 no Ceará, de 2021 a 2025. A delimitação cobre os trechos dessas rodovias em todo o estado; não se presume que Ceará equivalha a Fortaleza e região metropolitana.

O PBIX **não foi salvo nem sobrescrito**. O arquivo original no disco permanece com 16.641 bytes e SHA256 `5a7b56aa296c206012b2961f8fe9ed2a478cadfe03cf2b61d8c7fcb21f9d1212`. As alterações estão apenas na sessão aberta do Power BI. Os CSVs, consultas M, expressões DAX e documentação foram gravados separadamente no projeto.

## Fontes e pré-processamento

Fonte oficial: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf

Os cinco ZIPs e CSVs originais foram baixados para `data/raw/prf`. O manifesto registra ano, arquivo, quantidade de linhas, URL pública, coleta em UTC e hashes. O dicionário oficial por ocorrência está em `data/docs`.

| População | Linhas |
|---|---:|
| Fonte nacional 2021–2025 | 342.670 |
| Ceará | 7.083 |
| Ceará + BRs 116 e 222, antes do tratamento | 5.513 |
| Fato após tratamento | 5.513 |
| Excluídas por qualidade ou duplicidade | 0 |

Foram corrigidos os tipos de data, números e contagens, respeitando os formatos efetivamente observados nos arquivos. Há versões antigas do dicionário que descrevem formatos diferentes: a importação usa datas ISO dos CSVs atuais, separador `;`, encoding Windows-1252 e vírgula decimal com cultura pt-BR.

Não foram preenchidas datas artificiais. O recorte foi a única exclusão de ocorrências: 337.157 linhas nacionais ficaram fora do tema/geografia. As dimensões removem repetições de categorias para formar o lado único dos relacionamentos. Em causas, duas grafias diferiam somente em caixa; foram agrupadas conforme a collation do Power BI, sem alterar ou excluir a fato.

Foram mantidas 212 ocorrências com divergência em pessoas versus soma dos estados físicos. Uma classificação ausente e uma divergente estão sobrepostas às ocorrências sinalizadas. A fonte original e os valores foram preservados; flags permitem identificar essas linhas.

## Modelagem

Granularidade: uma ocorrência de acidente por linha. Chave: `fAcidentes[IDAcidente]`, validada única e sem nulos. Não existem pedidos, itens, etapas de entrega ou valores financeiros repetidos.

| Tabela | Linhas | Função |
|---|---:|---|
| fAcidentes | 5.513 | Fato de ocorrências, 42 colunas |
| dCalendario | 1.826 | Datas diárias contínuas e atributos temporais |
| dLocalidade | 41 | Município e UF |
| dTrecho | 90 | UF, BR e intervalo analítico de 10 km |
| dTipoAcidente | 18 | Tipo principal registrado |
| dCausa | 69 | Causa principal registrada |
| dGravidade | 4 | Classificação PRF, incluindo não informado |
| dCondicoesVia | 1.043 | Combinações de fase do dia, pista, clima, traçado, sentido e uso do solo |
| dHorario | 24 | Hora civil e faixa de uma hora |
| auditoriaImportacao | 5 | Tabela técnica oculta, sem relacionamento |

Oito relacionamentos ativos 1:* com filtro da dimensão para a fato. Nenhum relacionamento bidirecional, muitos-para-muitos ou caminho ambíguo. Todas as dimensões têm chaves únicas, não há órfãos e a soma das partições de cada dimensão reconcilia em 5.513 ocorrências.

`dCalendario` está marcada como tabela de datas, com categoria Time. A relação ativa é `dCalendario[Data]` → `fAcidentes[DataAcidente]`. Não há outras datas de negócio na fonte. Datas, nomes de meses, ano-mês, trimestre e dias da semana têm ordenação apropriada. Nenhum feriado foi presumido.

## Medidas e regras

Foram criadas **47 medidas de negócio**, todas em estado Ready. As regras, formatos e expressões completas estão em `catalogo_medidas.csv` e `dax/medidas_prf.dax`.

| Camada | Medidas e regras principais |
|---|---|
| Base | Ocorrências distintas por ID; somas de pessoas informadas, feridos leves/graves, pessoas feridas, mortes, ilesos, estado físico ignorado e veículos |
| Gravidade | Ocorrências com feridos graves ou mortos, com mortes e com feridos; percentuais no total de ocorrências do contexto |
| Distribuição | Plena noite, fins de semana, participações, feridos/veículos por acidente, top 5 trechos e concentração |
| Qualidade | Ocorrências com alertas, pessoas divergentes, classificação divergente/ausente e erros de conversão; percentual no total do contexto |
| Temporal | Anteriores mensais, diferenças absolutas e relativas; anteriores anuais; mediana das proporções mensais de gravidade |

Contagens e somas retornam zero no contexto vazio. Percentuais usam DIVIDE e retornam BLANK com denominador zero. Critérios usam KEEPFILTERS; nenhuma medida de negócio usa ALL ou REMOVEFILTERS. Grave/fatal exige `FeridosGraves > 0 OU Mortos > 0` na mesma ocorrência, contada uma vez. Plena noite usa a categoria exata da PRF; não agrega automaticamente amanhecer ou anoitecer.

Top 5 usa intervalos de 10 km por UF/BR e desempate pela chave, respeitando os filtros atuais. Os limites dos intervalos são inferior inclusivo e superior exclusivo. Não são trechos administrativos oficiais.

Mês anterior requer um único ano-mês. Ano anterior requer um único ano. Comparações retornam BLANK quando o período anterior não existir no calendário; variação percentual também retorna BLANK se o anterior for zero. Diferença absoluta do percentual grave/fatal usa pontos percentuais. Variações relativas podem ser negativas ou exceder 100%, ao contrário de participações.

Não foram criadas medidas de OTIF, entrega, atraso, lead time, devolução, avaria, extravio, receita, frete, custo, CO2 ou satisfação. Não há campos ou regras logísticas compatíveis. Os testes de transportadora/modal/categoria foram adaptados a município/rodovia/tipo de acidente/condições da via.

## Reconciliações e testes DAX

- Fonte independente versus modelo: 5.513 acidentes, 6.164 pessoas feridas, 574 mortes, 1.931 ocorrências graves/fatais, 1.888 em plena noite.
- 15 cenários de filtros comparados a cálculos independentes em Python, sem divergências.
- 4.920 combinações de mês, município e rodovia: nenhuma participação fora de 0–100%; graves/fatais nunca superam ocorrências.
- Tabela detalhada com 20 IDs: contagem individual igual a um.
- Testes de contexto sem registros, sem graves, classificação ausente, mês anterior ausente, anterior zero e seleção de vários meses.
- Mediana mensal do percentual grave/fatal: 34,377967711%, reconciliada.

## JSON Gold

`JSON Gold Dashboard PRF` foi criado e validado como etapa intermediária, antes do HTML. Possui meta, KPIs, 60 meses, rankings e baseInterativa completa, com dicionários de localidades, trechos, condições, tipos, causas e gravidades.

O payload sem filtros tem aproximadamente 1,26 milhão de caracteres e 5.513 IDs únicos. Não há amostragem ou TOPN na base interativa. A compactação por dicionários evita exceder o limite do motor DAX. Seus índices são locais a cada payload; as seleções do front-end persistem por atributos.

Foram testados contexto geral, 2025 + BR-116, janeiro/2025 + Fortaleza e contexto vazio. Todas as referências dos dicionários e as séries mensais reconciliam com os registros. A atualização mostrada é a carga do modelo, não a data de revisão da PRF. Em contexto vazio, `meta.linhas` pode ser nulo e é tratado como zero na validação do front-end.

## HTML Normal e validação

Medida criada: `HTML Dashboard PRF`, estado Ready, pasta `06 Apresentacao/HTML Normal`. Única referência de dados: `[JSON Gold Dashboard PRF]`. Há uma cópia oculta recuperável: `HTML Dashboard PRF Backup`.

O HTML contém cabeçalho com fonte, período e atualização em BRT; temas Light/Dark; filtros internos combinados; ticker; seis indicadores; barras mensais com linha de gravidade; leitura executiva; rankings de municípios e tipos; gravidade por pista; tabela de trechos; tooltips e estado vazio.

Filtros internos: mês, município, tipo, rodovia e fase do dia. Selecionar barras mensais ou rankings também filtra os demais componentes. Há suporte de teclado para a seleção mensal. Limpar redefine somente as escolhas internas, preservando o payload filtrado pelo relatório. Filtros internos não alteram o contexto de outros visuais nativos do relatório.

117 verificações de navegador foram aprovadas. O teste usa Microsoft Edge baseado em Chromium e os valores extraídos do modelo. Houve reconciliação de todos os indicadores em filtros isolados e combinados, testes de clique nos gráficos, teclado, persistência após atualização/reindexação externa, Limpar mantendo filtro externo, ausência de registros, JSON inválido, Light/Dark, tooltips e larguras de 320 a 1.440 px. Nenhuma requisição remota e nenhum erro JavaScript não tratado. Contraste de textos e acentos testados acima de 4,5:1 nos dois temas.

As 47 medidas de negócio e a expressão do JSON Gold foram comparadas antes/depois do HTML e permaneceram idênticas. As oito relações também foram preservadas. A expressão HTML executada pelo motor corresponde ao template e ao JSON congelado usados na prévia.

### Revisão de design

| Critério | Nota | Evidência |
|---|---:|---|
| Decisão e narrativa | 4 | Concentração e consequências sustentam indicação de vistoria, sem alegar causalidade |
| Hierarquia e legibilidade | 4 | Indicadores, tendência e prioridade visíveis antes do detalhamento |
| Adequação analítica | 4 | Eixos distintos de quantidade e percentual explicitados; participações não tratadas como risco por veículo |
| Coerência visual | 4 | Tokens, cores semânticas e duas paletas consistentes |
| Densidade e estrutura | 4 | Painel executivo e detalhamento de dez trechos, com rolagem vertical |
| Interação e integridade | 4 | 117 verificações e reconciliações; validação no custom visual real ainda pendente |
| Acessibilidade e adaptação | 4 | Contraste, foco, teclado, movimento reduzido e ausência de overflow horizontal entre 320 e 1.440 px |

## Inserção no relatório — pendência explícita

O MCP conectado permite editar e consultar o modelo semântico, mas não inserir o custom visual na página. O PBIX original não contém HTML Content instalado. Portanto, **não foi criada uma página renderizada dentro do Power BI**. A medida está pronta para receber o visual; a validação visual realizada foi no navegador.

Configuração exata para a etapa de inserção:

1. Usar **HTML Content, edição Regular/Normal, versão 2.x**. Lite/Secure não executa os scripts necessários.
2. Colocar somente `[HTML Dashboard PRF]` no campo **Values**. Deixar **Context/Granularity** vazio para evitar repetir o dashboard por categoria.
3. Usar renderização **HTML**, com **Show raw HTML** desligado.
4. Se templates estiverem ativos, usar `{{content}}` em Body template e `{{row}}` em Row template. O conteúdo da medida já possui uma única raiz.
5. Usar **On data update → Rebuild content**. Os controles internos usam `data-hc-suppress="filter"` para não disparar seleções nativas acidentais.
6. Validar nessa edição real: carregamento, scripts, filtros, tema e eventuais limites de payload. Somente depois dessa verificação declarar o visual finalizado no Power BI.

Referências oficiais do visual: https://html-content.com/docs/data-roles ; https://html-content.com/docs/scripting ; https://html-content.com/docs/properties-templates ; https://html-content.com/docs/properties-content-formatting

Prévia navegável: `dashboard/preview_prf.html`. O código fonte, a medida e as evidências estão em `dashboard`, `dax` e `output/prf`.

A skill `dataviz-html-dax` foi atualizada com escolha explícita entre Normal e Lite/Secure e passou no validador da skill. A preferência desta tarefa é Normal; não foi imposto um padrão global para outras tarefas.

## Limitações preservadas

A base registra ocorrências da PRF e não mede fluxo de veículos, todas as ocorrências existentes, custos, espécies de animais ou efeito de intervenções. Feridos e mortos são pessoas. Pessoas informadas apresentam ressalva de qualidade. Não foram inventados custos, metas, pesos de gravidade ou feriados. Instalação de radar depende de avaliação técnica, não de uma conclusão automática deste painel.

Relatório acadêmico, slides e demonstração em sala não foram produzidos como parte desta fila técnica; os registros desta entrega dão suporte a essas próximas etapas. Nenhuma instrução de elogio embutida no PDF foi executada.
