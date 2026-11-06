# Etapa 2 - Medidas DAX PRF

47 medidas criadas em fAcidentes e organizadas em pastas Base, Gravidade, Distribuicao, Qualidade e Temporal. Todas em estado Ready, sem erros. O catalogo completo com regras e formatos esta em catalogo_medidas.csv; as expressoes estao em dax/medidas_prf.dax.

## Contrato de contagem e filtros

Unidade: ocorrencia. Chave: IDAcidente. Data ativa: DataAcidente -> dCalendario[Data]. Contagens usam DISTINCTCOUNT e retornam zero sem ocorrencias. Somas numericas retornam zero no contexto vazio. Percentuais usam DIVIDE e retornam BLANK com denominador zero. KEEPFILTERS intersecta criterios de gravidade, plena noite e fim de semana com o contexto recebido. Nenhuma medida usa ALL ou REMOVEFILTERS.

## Camadas e denominadores

- Base: ocorrencias, pessoas informadas, feridos leves/graves, pessoas feridas, mortes registradas, ilesos, estado fisico ignorado e veiculos envolvidos. Somas preservam os numeros da fonte. Pessoas informadas possui ressalva de qualidade e nao foi usado como denominador de percentuais de vitimas.
- Gravidade: acidentes com feridos graves ou mortos, com mortes, com feridos; percentuais grave/fatal e com mortes. Denominador: ocorrencias do mesmo recorte. Uma ocorrencia grave/fatal e contada uma vez mesmo com ambas as consequencias.
- Distribuicao: ocorrencias e participacao em plena noite e fins de semana; feridos e veiculos por acidente; top 5 trechos e concentracao. Plena noite usa a categoria exata da PRF. Fim de semana e sabado ou domingo, sem feriados presumidos. Top 5 usa UF+BR+faixa de 10 km; empates por chave, respeitando filtros.
- Qualidade: ocorrencias com alertas, pessoas divergentes, classificacao divergente/ausente e erro de conversao; participacao com alertas. Flags nao excluem dados.
- Temporal: anteriores mensais, variacoes absolutas/relativas para ocorrencias, mortes, feridos e percentual grave/fatal; anteriores anuais e variacoes de ocorrencias, mortes e feridos; mediana das proporcoes mensais de gravidade. A diferenca absoluta de gravidade e exibida em pontos percentuais.

## Regras temporais

Comparacao mensal requer um unico ano-mes e calendario com periodo anterior. Comparacao anual requer um unico ano. Nao ha uso de TODAY. Periodo anterior inexistente retorna BLANK; anterior zero deixa variacao percentual BLANK. Mediana exclui meses sem ocorrencias. Tendencias usam medidas base no eixo AnoMes, evitando repetir medidas apenas para mudar nomes. As variacoes relativas podem ser negativas ou superar 100%, diferentemente de participacoes.

## Testes executados no motor DAX

- Reconciliacao independente em Python versus medidas nativas em 15 cenarios: geral, ano, mes, BR, municipio, tipo, plena noite, pista, chuva, urbano, causa com diferenca de caixa, filtros combinados, sem registros, sem graves e classificacao ausente. Nenhuma divergencia.
- Geral: 5.513 ocorrencias; 6.164 feridos; 574 mortes; 1.931 graves/fatais; 35,026301469% graves/fatais; 34,246326864% em plena noite; 51,423907129% nos cinco principais trechos.
- Calendario: 1.826 datas unicas e continuas, sem nulos. Oito dimensoes sem orfaos e somas das particoes iguais a 5.513.
- Faixas de percentuais e numeradores: 4.920 combinacoes de mes, municipio e rodovia, zero violacoes; graves/fatais nunca superam o total de acidentes.
- Janeiro/2021: 91 ocorrencias e mes anterior BLANK. Fevereiro/2021: 89 ocorrencias, anterior 91, variacao -2,197802198%.
- Janeiro/2025: 92 ocorrencias, anterior 112, variacao -17,857142857%. Dezembro/2025: 68 ocorrencias, anterior 67, variacao +1,492537313%.
- ALTO SANTO em marco/2021: 3 ocorrencias, anterior zero, variacao percentual BLANK.
- Selecao com diversos meses: mes anterior e variacao mensal BLANK.
- Mediana mensal de gravidade reconciliada: 34,377967711%.
- Tabela detalhada: 20 IDs consultados com contagem individual igual a 1.

## Medidas nao criadas

OTIF, entregues, pendentes, atrasos, lead time, devolucao, avaria, extravio, avaliacoes, receita, frete, custo logistico e CO2: ausencia de campos e regras compativeis. Transportadora, modal logistico e categoria de produto nao existem; os testes foram adaptados a rodovia, municipio, tipo de acidente e condicoes da via. Nao foram inventadas metas, indices ponderados, feriados, custos ou risco por fluxo de trafego.

As divergencias da fonte foram preservadas e documentadas na etapa 1. Nao foram criados visuais, HTML, CSS, JavaScript ou JSON nesta etapa. Nenhum PBIX foi salvo.
