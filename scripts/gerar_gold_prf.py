from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def lit(s):return '"'+s.replace('"','""')+'"'
def quoted(e):
    x=f'COALESCE({e}, "")'
    for old,new in [('\\','\\\\'),('"','\\"')]:x=f'SUBSTITUTE({x}, {lit(old)}, {lit(new)})'
    for code,new in [(13,'\\r'),(10,'\\n'),(9,'\\t')]:x=f'SUBSTITUTE({x}, UNICHAR({code}), {lit(new)})'
    return lit('"')+' & '+x+' & '+lit('"')
def num(e,fmt='0'):
    formatted=f'FORMAT({e}, {lit(fmt)}, "en-US")'
    if fmt!='0':formatted=f'IF({e} = INT({e}), FORMAT({e}, "0", "en-US"), {formatted})'
    return f'IF(ISBLANK({e}), "null", {formatted})'
def boolean(e):return f'IF({e}, "true", "false")'
def obj(fields):return lit('{')+' & '+(' & '+lit(',')+' & ').join(lit('"'+k+'":')+' & '+e for k,e in fields)+' & '+lit('}')
def array(expr):return lit('[')+' & '+expr+' & '+lit(']')
def concat(table,fields,order=None,direction='ASC'):
    return 'CONCATENATEX('+table+', '+obj(fields)+', ","'+(', '+order+', '+direction if order else '')+')'

meta=obj([
 ('versaoContrato',lit('"1.0"')),
 ('titulo',lit('"Segurança viária · Ceará"')),
 ('subtitulo',lit('"Frequência e gravidade nas BRs 116 e 222"')),
 ('fonte',lit('"Polícia Rodoviária Federal · dados por ocorrência"')),
 ('escopo',lit('"Ceará · BR-116 e BR-222 · 2021–2025"')),
 ('atualizadoEmUTC',quoted('FORMAT(MAX(auditoriaImportacao[AtualizadoEmUTC]), "yyyy-MM-ddTHH:mm:ss", "en-US") & "Z"')),
 ('dataInicio',quoted('FORMAT(MIN(dCalendario[Data]), "yyyy-MM-dd", "en-US")')),
 ('dataFim',quoted('FORMAT(MAX(dCalendario[Data]), "yyyy-MM-dd", "en-US")')),
 ('baseCompleta','"true"'),('linhas',num('COUNTROWS(fAcidentes)')),
 ('trechoKm','"10"'),
 ('limite',lit('"Ocorrências registradas; não representa risco por fluxo de tráfego. Vítimas são pessoas."'))
])
kpis=obj([(key,num('['+measure+']','0.###############')) for key,measure in [
 ('acidentes','Acidentes'),('graves','Acidentes graves ou fatais'),('percentualGrave','Percentual grave ou fatal'),
 ('feridos','Pessoas feridas'),('mortes','Mortes registradas'),('plenaNoite','Acidentes em plena noite'),
 ('percentualNoite','Percentual em plena noite'),('concentracaoTop5','Concentracao top 5 trechos'),
 ('comAlertas','Ocorrencias com alertas'),('pessoasDivergentes','Ocorrencias pessoas divergentes')]])
basefields=[
 ('id',num('fAcidentes[IDAcidente]')),('d',quoted('FORMAT(fAcidentes[DataAcidente], "yyyy-MM-dd", "en-US")')),
 ('l',num('RANKX(_Loc, dLocalidade[LocalidadeKey], fAcidentes[LocalidadeKey], ASC, DENSE)')),
 ('t',num('RANKX(_Trechos, dTrecho[TrechoKey], fAcidentes[TrechoKey], ASC, DENSE)')),
 ('c',num('RANKX(_Tipos, dTipoAcidente[TipoAcidente], fAcidentes[TipoKey], ASC, DENSE)')),
 ('ca',num('RANKX(_Causas, dCausa[CausaRegistrada], RELATED(dCausa[CausaRegistrada]), ASC, DENSE)')),
 ('g',num('RANKX(_Gravidades, dGravidade[ClassificacaoPRF], fAcidentes[GravidadeKey], ASC, DENSE)')),
 ('v',num('RANKX(_Condicoes, dCondicoesVia[CondicoesViaKey], fAcidentes[CondicoesViaKey], ASC, DENSE)')),
 ('h',num('fAcidentes[Hora]')),('km',num('fAcidentes[Km]','0.###############')),
 ('lat',num('fAcidentes[Latitude]','0.###############')),('lon',num('fAcidentes[Longitude]','0.###############')),
 ('p',num('fAcidentes[Pessoas]')),('f',num('fAcidentes[Feridos]')),('fg',num('fAcidentes[FeridosGraves]')),
 ('m',num('fAcidentes[Mortos]')),('ve',num('fAcidentes[Veiculos]')),
 ('q',boolean('fAcidentes[FlagQualidade]')),('qp',boolean('fAcidentes[FlagPessoasDivergentes]')),
 ('qc',boolean('fAcidentes[FlagClassificacaoDivergente]')),('qa',boolean('fAcidentes[FlagClassificacaoAusente]')),
]
locfields=[('k',num('RANKX(_Loc, dLocalidade[LocalidadeKey], , ASC, DENSE)')),('chave',quoted('dLocalidade[LocalidadeKey]')),('uf',quoted('dLocalidade[UF]')),('municipio',quoted('dLocalidade[Municipio]'))]
trechofields=[('k',num('RANKX(_Trechos, dTrecho[TrechoKey], , ASC, DENSE)')),('chave',quoted('dTrecho[TrechoKey]')),('rodovia',quoted('dTrecho[Rodovia]')),('inicio',num('dTrecho[KmInicial]')),('fim',num('dTrecho[KmFinalExclusivo]')),('rotulo',quoted('dTrecho[Trecho]'))]
condfields=[('k',num('RANKX(_Condicoes, dCondicoesVia[CondicoesViaKey], , ASC, DENSE)')),('fase',quoted('dCondicoesVia[FaseDia]')),('pista',quoted('dCondicoesVia[TipoPista]')),('clima',quoted('dCondicoesVia[CondicaoMeteorologica]')),('tracado',quoted('dCondicoesVia[TracadoVia]')),('sentido',quoted('dCondicoesVia[SentidoVia]')),('uso',quoted('dCondicoesVia[UsoSolo]'))]
metricfields=[('acidentes',num('[Acidentes]')),('graves',num('[Acidentes graves ou fatais]')),('feridos',num('[Pessoas feridas]')),('mortes',num('[Mortes registradas]')),('percentualGrave',num('[Percentual grave ou fatal]','0.###############'))]
seriesfields=[('mes',quoted('dCalendario[AnoMes]'))]+metricfields
ranktrecho=[('k',quoted('dTrecho[TrechoKey]')),('rotulo',quoted('dTrecho[Trecho]'))]+metricfields
rankmunicipio=[('k',quoted('dLocalidade[LocalidadeKey]')),('rotulo',quoted('dLocalidade[Municipio]'))]+metricfields
ranktipo=[('rotulo',quoted('dTipoAcidente[TipoAcidente]'))]+metricfields

variables='''VAR _Loc = SUMMARIZE(fAcidentes, dLocalidade[LocalidadeKey], dLocalidade[UF], dLocalidade[Municipio])
VAR _Trechos = SUMMARIZE(fAcidentes, dTrecho[TrechoKey], dTrecho[Rodovia], dTrecho[KmInicial], dTrecho[KmFinalExclusivo], dTrecho[Trecho])
VAR _Condicoes = SUMMARIZE(fAcidentes, dCondicoesVia[CondicoesViaKey], dCondicoesVia[FaseDia], dCondicoesVia[TipoPista], dCondicoesVia[CondicaoMeteorologica], dCondicoesVia[TracadoVia], dCondicoesVia[SentidoVia], dCondicoesVia[UsoSolo])
VAR _Tipos = SUMMARIZE(fAcidentes, dTipoAcidente[TipoAcidente])
VAR _Causas = SUMMARIZE(fAcidentes, dCausa[CausaRegistrada])
VAR _Gravidades = SUMMARIZE(fAcidentes, dGravidade[ClassificacaoPRF])
VAR _Meses = VALUES(dCalendario[AnoMes])
VAR _RankTrechos = TOPN(10, FILTER(ADDCOLUMNS(SUMMARIZE(fAcidentes,dTrecho[TrechoKey],dTrecho[Trecho]),"@N",[Acidentes]), [@N]>0), [@N],DESC,dTrecho[TrechoKey],ASC)
VAR _RankMunicipios = TOPN(10, FILTER(ADDCOLUMNS(SUMMARIZE(fAcidentes,dLocalidade[LocalidadeKey],dLocalidade[Municipio]),"@N",[Acidentes]), [@N]>0), [@N],DESC,dLocalidade[LocalidadeKey],ASC)
VAR _RankTipos = TOPN(10, FILTER(ADDCOLUMNS(SUMMARIZE(fAcidentes,dTipoAcidente[TipoAcidente]),"@N",[Acidentes]), [@N]>0), [@N],DESC,dTipoAcidente[TipoAcidente],ASC)
'''
rankings=obj([
 ('trechos',array(concat('_RankTrechos',ranktrecho,'dTrecho[TrechoKey]'))),
 ('municipios',array(concat('_RankMunicipios',rankmunicipio,'dLocalidade[LocalidadeKey]'))),
 ('tipos',array(concat('_RankTipos',ranktipo,'dTipoAcidente[TipoAcidente]')))
])
expression=variables+'RETURN\n'+obj([
 ('meta',meta),('kpis',kpis),
 ('seriesMensais',array(concat('_Meses',seriesfields,'dCalendario[AnoMes]'))),
 ('rankings',rankings),
 ('localidades',array(concat('_Loc',locfields,'dLocalidade[LocalidadeKey]'))),
 ('trechos',array(concat('_Trechos',trechofields,'dTrecho[TrechoKey]'))),
 ('condicoes',array(concat('_Condicoes',condfields,'dCondicoesVia[CondicoesViaKey]'))),
 ('tipos',array(concat('_Tipos',[('k',num('RANKX(_Tipos, dTipoAcidente[TipoAcidente], , ASC, DENSE)')),('rotulo',quoted('dTipoAcidente[TipoAcidente]'))],'dTipoAcidente[TipoAcidente]'))),
 ('causas',array(concat('_Causas',[('k',num('RANKX(_Causas, dCausa[CausaRegistrada], , ASC, DENSE)')),('rotulo',quoted('dCausa[CausaRegistrada]'))],'dCausa[CausaRegistrada]'))),
 ('gravidades',array(concat('_Gravidades',[('k',num('RANKX(_Gravidades, dGravidade[ClassificacaoPRF], , ASC, DENSE)')),('rotulo',quoted('dGravidade[ClassificacaoPRF]'))],'dGravidade[ClassificacaoPRF]'))),
 ('baseInterativa',array(concat('fAcidentes',basefields,'fAcidentes[IDAcidente]')))
])
measure=dict(name='JSON Gold Dashboard PRF',tableName='fAcidentes',expression=expression,
 displayFolder='06 Apresentacao\\JSON Gold',description='Contrato JSON 1.0, unica fonte da medida HTML Dashboard PRF. Exporta todas as ocorrencias do contexto externo sem TOPN na baseInterativa, mais dicionarios filtrados, series e KPIs nativos. Numeros em cultura en-US e strings escapadas. Metadados de atualizacao referem-se ao modelo, nao a revisao da PRF.')
if __name__=='__main__':
    (ROOT/'dax'/'json_gold_prf.dax').write_text(measure['name']+' =\n'+expression+'\n',encoding='utf-8')
    (ROOT/'output'/'prf'/'contrato_json_gold.md').write_text('''# Contrato JSON Gold PRF 1.0\n\nFonte unica do HTML: [JSON Gold Dashboard PRF]. Gerado em etapa intermediaria apos validar medidas e antes de criar HTML.\n\nObjetos: meta, kpis, seriesMensais, rankings (trechos, municipios, tipos), localidades, trechos, condicoes, tipos, causas, gravidades e baseInterativa.\n\nA base nao e truncada nem agregada: uma ocorrencia por id. Campos l, t, c, ca, g e v usam indices numericos k dos dicionarios do mesmo payload; esses indices podem mudar conforme filtros externos e nao sao chaves persistentes do modelo. O front-end persiste filtros por atributos. Em contexto vazio, meta.linhas pode ser null (COUNTROWS sem linhas), equivalente a zero para essa verificacao. Dicionarios contem apenas chaves presentes no contexto atual da fato.\n\nCampos de baseInterativa: id=IDAcidente; d=data ISO; l=LocalidadeKey; t=TrechoKey; c=tipo principal; ca=causa principal com grafia canonica da dimensao; g=classificacao PRF; v=CondicoesViaKey; h=hora 0-23; km=quilometro; lat/lon=coordenadas; p=pessoas informadas; f=feridos; fg=feridos graves; m=mortos; ve=veiculos; q=alerta de qualidade; qp=pessoas divergentes; qc=classificacao divergente; qa=classificacao ausente.\n\nGrave/fatal: fg>0 ou m>0; plena noite: fase exatamente Plena Noite. Top 5 respeita filtros e usa desempate por chave. Participacoes sem registros retornam null, contagens retornam zero.\n\nFiltros internos seguros: mes, municipio, tipo de acidente, rodovia e fase do dia, combinados. Todos os componentes podem ser recalculados a partir dos registros e dicionarios deste JSON. Os filtros internos nao chamam APIs nem alteram filtros nativos. Limpar atua apenas nas escolhas internas.\n\nseriesMensais inclui os meses do calendario sob contexto externo. Comparacoes internas so podem usar periodos presentes nesse contexto; nao presumir dados de periodos removidos pelos filtros externos. Medidas temporais nativas permanecem independentes, sem serem reimplementadas como se a base exportasse periodos ocultos.\n\nA fonte nao contem custo, frete, receita, OTIF, lead time, transportadora ou modal logistico. Esses campos nao sao simulados ou substituidos por numeros artificiais. AtualizadoEmUTC representa a ultima carga do modelo, nao o ultimo acidente nem a revisao da fonte.\n''',encoding='utf-8')
    print(json.dumps(measure,ensure_ascii=True))
