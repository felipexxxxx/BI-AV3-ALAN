# Contrato JSON Gold PRF 1.0

Fonte unica do HTML: [JSON Gold Dashboard PRF]. Gerado em etapa intermediaria apos validar medidas e antes de criar HTML.

Objetos: meta, kpis, seriesMensais, rankings (trechos, municipios, tipos), localidades, trechos, condicoes, tipos, causas, gravidades e baseInterativa.

Compactacao: l, t, c, ca, g e v referenciam o campo numerico k dos respectivos dicionarios contidos no mesmo payload. Esses indices sao locais a cada payload, nao chaves persistentes do modelo. A selecao do front-end deve persistir por atributos, nao por esses indices. Isso mantem a base completa em cerca de 1,26 milhao de caracteres, dentro do limite do motor DAX.

A base nao e truncada nem agregada: uma ocorrencia por id. Dicionarios contem apenas chaves presentes no contexto atual da fato.

Campos de baseInterativa: id=IDAcidente; d=data ISO; l=LocalidadeKey; t=TrechoKey; c=tipo principal; ca=causa principal com grafia canonica da dimensao; g=classificacao PRF; v=CondicoesViaKey; h=hora 0-23; km=quilometro; lat/lon=coordenadas; p=pessoas informadas; f=feridos; fg=feridos graves; m=mortos; ve=veiculos; q=alerta de qualidade; qp=pessoas divergentes; qc=classificacao divergente; qa=classificacao ausente.

Grave/fatal: fg>0 ou m>0; plena noite: fase exatamente Plena Noite. Top 5 respeita filtros e usa desempate por chave. Participacoes sem registros retornam null, contagens retornam zero.

Filtros internos seguros: mes, municipio, tipo de acidente, rodovia e fase do dia, combinados. Todos os componentes podem ser recalculados a partir dos registros e dicionarios deste JSON. Os filtros internos nao chamam APIs nem alteram filtros nativos. Limpar atua apenas nas escolhas internas.

seriesMensais inclui os meses do calendario sob contexto externo. Comparacoes internas so podem usar periodos presentes nesse contexto; nao presumir dados de periodos removidos pelos filtros externos. Medidas temporais nativas permanecem independentes, sem serem reimplementadas como se a base exportasse periodos ocultos.

A fonte nao contem custo, frete, receita, OTIF, lead time, transportadora ou modal logistico. Esses campos nao sao simulados ou substituidos por numeros artificiais. AtualizadoEmUTC representa a ultima carga do modelo, nao o ultimo acidente nem a revisao da fonte.
