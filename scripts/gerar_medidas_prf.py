from pathlib import Path
import csv
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dax'
OUT.mkdir(exist_ok=True)
measures=[]
def add(name,expr,folder,description,fmt='#,##0'):
    measures.append(dict(name=name,tableName='fAcidentes',expression=expr,
                         displayFolder=folder,description=description,formatString=fmt))

add('Acidentes','COALESCE(DISTINCTCOUNT(fAcidentes[IDAcidente]), 0)','01 Base',
    'Ocorrencias distintas por IDAcidente. Preserva todos os filtros externos. Zero quando nao houver ocorrencias. Escopo fixo da importacao: CE, BR 116/222, 2021-2025.')
for name,c,desc in [
 ('Pessoas informadas','Pessoas','Total de pessoas informado pela PRF. Ha 212 ocorrencias com divergencia na soma dos estados fisicos; nao usar como denominador de percentuais de vitimas sem revisao.'),
 ('Pessoas feridas','Feridos','Pessoas com ferimentos leves ou graves. Reconciliada com FeridosLeves + FeridosGraves.'),
 ('Feridos leves','FeridosLeves','Pessoas com ferimentos leves registradas na ocorrencia.'),
 ('Feridos graves','FeridosGraves','Pessoas com ferimentos graves registradas na ocorrencia.'),
 ('Mortes registradas','Mortos','Pessoas mortas registradas no boletim da PRF. Nao representa animais mortos nem mortalidade de acompanhamento hospitalar.'),
 ('Pessoas ilesas','Ilesos','Pessoas ilesas registradas na fonte.'),
 ('Estado fisico ignorado','Ignorados','Pessoas cujo estado fisico nao foi identificado na fonte.'),
 ('Veiculos envolvidos','Veiculos','Veiculos envolvidos nas ocorrencias. Nao corresponde ao fluxo total da rodovia.')]:
    add(name,f'COALESCE(SUM(fAcidentes[{c}]), 0)','01 Base',desc+' Zero sem ocorrencias; filtros externos preservados.')

def countflag(name,condition,folder,description):
    add(name,'CALCULATE([Acidentes], KEEPFILTERS('+condition+'))',folder,description+' Unidade: ocorrencia. KEEPFILTERS intersecta a condicao com os filtros existentes. Zero sem ocorrencias elegiveis.')

countflag('Acidentes graves ou fatais','fAcidentes[FlagGraveFatal] = TRUE()','02 Gravidade',
 'Ocorrencia com FeridosGraves > 0 ou Mortos > 0, contada uma vez mesmo quando houver ambos. Usa contagens, sem corrigir a classificacao original da PRF.')
countflag('Acidentes com mortes','fAcidentes[Mortos] > 0','02 Gravidade','Ocorrencias com pelo menos uma pessoa morta, nao a soma das mortes.')
countflag('Acidentes com feridos','fAcidentes[Feridos] > 0','02 Gravidade','Ocorrencias com pelo menos uma pessoa ferida.')
add('Percentual grave ou fatal','DIVIDE([Acidentes graves ou fatais], [Acidentes])','02 Gravidade',
 'Numerador: ocorrencias graves/fatais. Denominador: ocorrencias distintas no mesmo contexto. BLANK sem ocorrencias. Nao mede risco por veiculo.','0.0%')
add('Percentual com mortes','DIVIDE([Acidentes com mortes], [Acidentes])','02 Gravidade',
 'Numerador: ocorrencias com ao menos uma morte. Denominador: ocorrencias distintas no contexto. BLANK com denominador zero.','0.0%')

countflag('Acidentes em plena noite','fAcidentes[FlagPlenaNoite] = TRUE()','03 Distribuicao','Ocorrencias cuja FaseDia e exatamente Plena Noite. Amanhecer e Anoitecer nao sao incluidos nessa categoria.')
countflag('Acidentes fim de semana','dCalendario[FimDeSemana] = TRUE()','03 Distribuicao','Ocorrencias em sabado ou domingo, pela DataAcidente. Nao pressupoe feriados.')
for name,num in [('Percentual em plena noite','Acidentes em plena noite'),('Percentual fim de semana','Acidentes fim de semana')]:
    add(name,f'DIVIDE([{num}], [Acidentes])','03 Distribuicao',f'Numerador: [{num}]. Denominador: ocorrencias distintas no mesmo contexto externo. BLANK sem ocorrencias.','0.0%')
add('Feridos por acidente','DIVIDE([Pessoas feridas], [Acidentes])','03 Distribuicao','Pessoas feridas por ocorrencia. Pode superar 1, pois uma ocorrencia pode ter diversas vitimas. BLANK sem ocorrencias.','0.00')
add('Veiculos por acidente','DIVIDE([Veiculos envolvidos], [Acidentes])','03 Distribuicao','Veiculos envolvidos por ocorrencia, sem confundir com fluxo de trafego. BLANK sem ocorrencias.','0.00')
add('Acidentes top 5 trechos','''VAR _Trechos = ADDCOLUMNS(VALUES(dTrecho[TrechoKey]), "@Acidentes", [Acidentes])
VAR _Top = TOPN(5, _Trechos, [@Acidentes], DESC, dTrecho[TrechoKey], ASC)
RETURN COALESCE(SUMX(_Top, [@Acidentes]), 0)''','03 Distribuicao',
 'Soma de ocorrencias nos cinco trechos com maior volume dentro dos filtros atuais. Trechos: UF+BR+intervalo analitico de 10 km. Empates desempatados pela chave, garantindo no maximo cinco trechos. Nao remove filtros externos.')
add('Concentracao top 5 trechos','DIVIDE([Acidentes top 5 trechos], [Acidentes])','03 Distribuicao',
 'Numerador: ocorrencias nos cinco trechos de maior volume no recorte. Denominador: todas as ocorrencias do mesmo recorte. BLANK sem dados; nao mede risco por fluxo.','0.0%')

for name,flag,desc in [
 ('Ocorrencias com alertas','FlagQualidade','Ocorrencias com pelo menos uma flag de qualidade, contadas uma unica vez.'),
 ('Ocorrencias pessoas divergentes','FlagPessoasDivergentes','Divergencia entre Pessoas e a soma dos estados fisicos registrados. Valores mantidos sem correcao artificial.'),
 ('Ocorrencias classificacao divergente','FlagClassificacaoDivergente','Presenca/ausencia de Mortos inconsistente com a classificacao original Com Vitimas Fatais.'),
 ('Ocorrencias classificacao ausente','FlagClassificacaoAusente','Classificacao original vazia ou sentinela NA. Nao e uma nova classe de gravidade.'),
 ('Ocorrencias erro conversao','FlagConversao','Pelo menos um campo numerico, de data ou horario nao pode ser convertido segundo o contrato de origem.')]:
    countflag(name,f'fAcidentes[{flag}] = TRUE()','04 Qualidade',desc)
add('Percentual com alertas','DIVIDE([Ocorrencias com alertas], [Acidentes])','04 Qualidade','Ocorrencias com alertas divididas pelas ocorrencias do contexto. BLANK sem dados. Nao exclui as ocorrencias sinalizadas.','0.0%')

for base,slug,fmt in [('Acidentes','Acidentes','#,##0'),('Mortes registradas','Mortes','#,##0'),('Pessoas feridas','Feridos','#,##0'),('Percentual grave ou fatal','Gravidade percentual','0.0%')]:
    prev=f'{slug} mes anterior'
    desc='Requer um unico ano-mes no contexto. Desloca somente o calendario em um mes e preserva os filtros das outras dimensoes. BLANK para selecao de varios meses ou periodo anterior fora do calendario.'
    add(prev,f'''VAR _Datas = DATEADD(dCalendario[Data], -1, MONTH)
RETURN IF(HASONEVALUE(dCalendario[AnoMesOrdem]) && NOT ISEMPTY(_Datas), CALCULATE([{base}], _Datas))''','05 Temporal\\'+slug,desc,fmt)
    absname=f'{slug} variacao mensal absoluta'
    add(absname,f'VAR _Anterior = [{prev}] RETURN IF(NOT ISBLANK(_Anterior), [{base}] - _Anterior)','05 Temporal\\'+slug,'Diferenca do valor atual para o mes anterior no mesmo recorte; BLANK sem mes anterior elegivel. Para gravidade, a diferenca e de proporcoes, exibida em pontos percentuais.', '0.0 "p.p."' if slug=='Gravidade percentual' else '#,##0')
    if slug=='Gravidade percentual':
        measures[-1]['expression']=f'VAR _Anterior = [{prev}] VAR _Atual = [{base}] RETURN IF(NOT ISBLANK(_Anterior) && NOT ISBLANK(_Atual), (_Atual - _Anterior) * 100)'
    add(f'{slug} variacao mensal percentual',f'VAR _Anterior = [{prev}] RETURN IF(NOT ISBLANK(_Anterior), DIVIDE([{base}] - _Anterior, _Anterior))','05 Temporal\\'+slug,
        'Variacao relativa contra o mes anterior. DIVIDE retorna BLANK se o valor anterior for zero ou ausente. Nao e limitada a 0-100%, pois e variacao, nao participacao.','+0.0%;-0.0%;0.0%')

add('Mediana mensal percentual grave ou fatal','''VAR _Meses = FILTER(VALUES(dCalendario[AnoMes]), NOT ISBLANK(CALCULATE([Percentual grave ou fatal])))
RETURN MEDIANX(_Meses, CALCULATE([Percentual grave ou fatal]))''','05 Temporal',
 'Mediana das proporcoes mensais entre os meses do contexto com ocorrencias. Meses sem ocorrencias sao excluidos, nao convertidos em zero. Nao e mediana de OTIF.','0.0%')

for base,slug,fmt in [('Acidentes','Acidentes','#,##0'),('Mortes registradas','Mortes','#,##0'),('Pessoas feridas','Feridos','#,##0')]:
    prev=f'{slug} ano anterior'
    add(prev,f'''VAR _Datas = DATEADD(dCalendario[Data], -1, YEAR)
RETURN IF(HASONEVALUE(dCalendario[Ano]) && NOT ISEMPTY(_Datas), CALCULATE([{base}], _Datas))''','05 Temporal\\'+slug,
        'Mesmo conjunto de datas deslocado em um ano. Requer um unico ano; preserva os outros filtros. BLANK se o periodo anterior estiver fora do calendario.',fmt)
    add(f'{slug} variacao anual percentual',f'VAR _Anterior = [{prev}] RETURN IF(NOT ISBLANK(_Anterior), DIVIDE([{base}] - _Anterior, _Anterior))','05 Temporal\\'+slug,
        'Variacao relativa anual sob o mesmo contexto dimensional. BLANK para anterior zero/ausente ou selecao sem um unico ano.','+0.0%;-0.0%;0.0%')

if __name__=='__main__':
    (OUT/'medidas_prf.dax').write_text('\n\n'.join('-- Pasta: '+m['displayFolder']+'\n-- '+m['description']+'\n'+m['name']+' =\n'+m['expression'] for m in measures)+'\n',encoding='utf-8')
    with (ROOT/'output'/'prf'/'catalogo_medidas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['Medida','Pasta','Regra','Formato'])
        w.writeheader();w.writerows(dict(Medida=m['name'],Pasta=m['displayFolder'],Regra=m['description'],Formato=m['formatString']) for m in measures)
    print(json.dumps(measures,ensure_ascii=True))
