# Etapa 1 - Power Query e modelagem PRF

Escopo: CE, BR 116 ou 222, de 01/01/2021 a 31/12/2025.

- Fonte nacional: 342.670 linhas em cinco CSVs com 30 colunas originais.
- Ceara: 7.083 linhas. Recorte: 5.513 linhas antes e depois do tratamento.
- Fora do escopo: 337.157 linhas nacionais; nenhuma exclusao por qualidade.
- Nenhuma duplicidade removida da fato. Chave IDAcidente unica, sem nulos.
- Dimensao dCausa agrupa apenas a equivalencia de caixa comprovada Transitar no acostamento / Transitar no Acostamento, conforme collation do modelo.
- Staging sem carga: pPastaPRF, stgPRF_Bruta, prfRecorte_Tratado. Arquivos originais preservados e manifesto com hashes em data/raw/prf.
- Fato: fAcidentes (5.513 linhas, 42 colunas). Uma linha por ocorrencia. ArquivoFonte, LinhaFonte e AnoArquivo preservam a rastreabilidade.
- Dimensoes: dCalendario (1.826), dLocalidade (41), dTrecho (90), dTipoAcidente (18), dCausa (69), dGravidade (4), dCondicoesVia (1.043), dHorario (24).
- auditoriaImportacao: cinco linhas, tecnica e oculta, sem relacionamentos.
- Oito relacionamentos ativos, dimensao 1 para muitos na fato, direcao unica. Nenhum relacionamento entre dimensoes, nenhum caminho ambiguo.
- dCalendario marcada como Time, chave Data unica e continua, data ativa fAcidentes[DataAcidente]. Atributos temporais e ordenacao definidos. Sem outras datas de negocio na fonte.
- Trecho: UF + BR + faixa analitica de 10 km, limite inferior inclusivo e superior exclusivo. Nao e trecho administrativo oficial.
- 212 ocorrencias com divergencia em pessoas versus estados fisicos; uma classificacao divergente e uma ausente, sobrepostas as ocorrencias sinalizadas. Todas mantidas.
- Feridos e mortos sao pessoas. UsoSoloFonte Sim=Urbano e Nao=Rural conforme dicionario oficial.
- Entregas pendentes, OTIF, frete, custos, CO2, transportadora, modal logistico e categoria de produto nao se aplicam. Nao foram criados.
- Nao houve criacao de medidas DAX, JSON ou visuais nesta etapa.
- PBIX no disco permaneceu com o mesmo hash SHA256; alteracoes estao na sessao aberta.

## Reconciliacao no motor DAX

Fonte independente versus modelo: 5.513 ocorrencias, 13.901 pessoas informadas, 6.164 feridos, 574 mortes, 1.931 acidentes com feridos graves ou mortos, 1.888 ocorrencias em plena noite.

## Limitacoes e regras pendentes

As divergencias da fonte nao foram corrigidas sem comprovacao. As causas registradas nao demonstram causalidade. Nao ha fluxo de trafego, custos, historico de intervencoes, especies de animais nem dados para comprovar efeito de radar. Nao se presume calendario de feriados. O recorte nao se limita a Fortaleza ou sua regiao metropolitana. A tipologia agregada de grave/fatal usa contagens objetivas e preserva a classificacao PRF original.
