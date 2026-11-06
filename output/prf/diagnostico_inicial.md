# Diagnostico inicial da base PRF

## Escopo e fonte
Projeto aberto: BI. Tema: frequencia e gravidade dos acidentes nas BRs 116 e 222 no Ceara, 2021-2025.
Fonte: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
Arquivos por ocorrencia, preservados sem alteracao em data/raw/prf.

## Granularidade e reducao
Fonte nacional: 342,670 linhas; CE: 7,083; CE e BR 116/222: 5,513.
Colunas originais: 30. Uma linha por ocorrencia; chave candidata id.
IDs repetidos no recorte: 0; IDs repetidos na fonte nacional consolidada: 0.
Linhas inteiramente iguais no recorte (30 campos originais): 0.
Periodo: 2021-01-01 a 2025-12-31.
Nenhuma exclusao por qualidade, nenhum preenchimento artificial de datas, nenhuma remocao de duplicidades.
A reducao e apenas tematica/geografica: CE, BR 116 ou BR 222; nao restringe a Fortaleza ou regiao metropolitana.

## Temporal e campos incompativeis com o prompt logistico
data_inversa = data do acidente; horario = horario do acidente. Nao existem datas de pedido, promessa ou entrega.
Entregas pendentes, OTIF, receita, frete, custo, CO2, transportadora, modal logistico e avaliacoes nao se aplicam.
Nenhum valor financeiro existe ou pode ser repetido por item; a base nao tem itens de pedido.

## Dimensoes sustentadas
Calendario; municipio/UF; rodovia e trecho por faixas analiticas de 10 km; tipo; causa registrada; classificacao da gravidade; circunstancias (fase do dia, pista, clima, tracado, sentido e uso do solo); faixa horaria.
As faixas de 10 km sao agrupamentos de analise, nao trechos administrativos oficiais.

## Verificacoes de qualidade
- DataInvalida: 0
- HorarioInvalido: 0
- IDInvalido: 0
- IDDuplicado: 0
- KmInvalido: 0
- CoordenadaInvalida: 0
- ContagemInvalida: 0
- FeridosDivergentes: 0
- PessoasDivergentes: 212
- AnoArquivoDivergente: 0
- GravidadeDivergente: 1
- DiaSemanaDivergente: 0

## Categorias observadas
- classificacao_acidente: {'Com Vítimas Feridas': 4114, 'Sem Vítimas': 875, 'Com Vítimas Fatais': 523, 'NA': 1}
- fase_dia: {'Pleno dia': 3132, 'Plena Noite': 1888, 'Anoitecer': 255, 'Amanhecer': 238}
- tipo_acidente: {'Colisão traseira': 1359, 'Colisão transversal': 675, 'Colisão lateral mesmo sentido': 673, 'Tombamento': 479, 'Saída de leito carroçável': 426, 'Atropelamento de Pedestre': 398, 'Colisão frontal': 358, 'Colisão com objeto': 312, 'Queda de ocupante de veículo': 265, 'Colisão lateral sentido oposto': 154, 'Atropelamento de Animal': 116, 'Engavetamento': 105, 'Incêndio': 88, 'Capotamento': 57, 'Eventos atípicos': 23, 'Colisão lateral': 14, 'Derramamento de carga': 10, 'Sinistro pessoal de trânsito': 1}
- tipo_pista: {'Simples': 2398, 'Dupla': 1799, 'Múltipla': 1316}
- uso_solo: {'Sim': 3123, 'Não': 2390}

## Totais independentes de controle
- Acidentes: 5513
- Pessoas: 13901
- FeridosLeves: 4355
- FeridosGraves: 1809
- Feridos: 6164
- Mortes: 574
- Ilesos: 5409
- Ignorados: 2092
- Veiculos: 11301
- GravesFatais: 1931
- PlenaNoite: 1888

## Tipos, ausencias e erros
Os arquivos CSV nao declaram tipos. id e br serao identificadores; data e horario serao convertidos; km, latitude e longitude usam virgula decimal e cultura pt-BR; contagens serao inteiras.
O arquivo perfil_colunas.csv documenta tipos interpretados, vazios e erros de conversao por coluna.

## Limitacoes
As vitimas sao pessoas. O arquivo nao informa especies ou animais mortos, fluxo de trafego, custos, acao preventiva implantada ou efeito causal.
Causas sao as registradas pela PRF e nao autorizam atribuir causalidade ou decidir automaticamente por radar.
Registrar esta fotografia da coleta e hashes; publicacoes anuais podem ser retificadas.
