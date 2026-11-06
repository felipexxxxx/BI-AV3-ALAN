from pathlib import Path
import pandas as pd
import json
import math

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data'/'raw'/'prf'
d=pd.concat([pd.read_csv(p/f'datatran{y}.csv',sep=';',encoding='cp1252',keep_default_na=False) for y in range(2021,2026)],ignore_index=True)
d=d[d.uf.eq('CE') & d.br.isin([116,222])].copy()
d['Data']=pd.to_datetime(d.data_inversa)
d['Mes']=d.Data.dt.strftime('%Y-%m')
d['Grave']=d.feridos_graves.gt(0)|d.mortos.gt(0)
d['PessoasDivergentes']=d.pessoas.ne(d.mortos+d.feridos_leves+d.feridos_graves+d.ilesos+d.ignorados)
d['Trecho']=d.uf+'|BR-'+d.br.astype(str)+'|'+((pd.to_numeric(d.km.str.replace(',','.',regex=False))//10)*10).astype(int).astype(str).str.zfill(6)

def expected(s):
    n=len(s)
    counts=s.groupby('Trecho').size().sort_values(ascending=False).head(5)
    return {'Acidentes':n,'Feridos':int(s.feridos.sum()),'Mortes':int(s.mortos.sum()),
            'Graves':int(s.Grave.sum()),'PercentualGrave':float(s.Grave.mean()) if n else None,
            'PercentualNoite':float(s.fase_dia.eq('Plena Noite').mean()) if n else None,
            'ConcentracaoTop5':float(counts.sum()/n) if n else None,
            'PessoasDivergentes':int(s.PessoasDivergentes.sum())}

cases=[]
def case(name,mask,filters):
    cases.append({'name':name,'filters':filters,'expected':expected(d.loc[mask])})

case('Geral',d.index.notna(),[])
case('Ano 2025',d.Data.dt.year.eq(2025),['dCalendario[Ano] = 2025'])
case('Janeiro 2025',d.Mes.eq('2025-01'),['dCalendario[AnoMes] = "2025-01"'])
case('BR116',d.br.eq(116),['dTrecho[BRNumero] = 116'])
case('Fortaleza',d.municipio.eq('FORTALEZA'),['dLocalidade[Municipio] = "FORTALEZA"'])
case('Tipo animal',d.tipo_acidente.eq('Atropelamento de Animal'),['dTipoAcidente[TipoAcidente] = "Atropelamento de Animal"'])
case('Plena noite',d.fase_dia.eq('Plena Noite'),['dCondicoesVia[FaseDia] = "Plena Noite"'])
case('Pista simples',d.tipo_pista.eq('Simples'),['dCondicoesVia[TipoPista] = "Simples"'])
case('Chuva',d.condicao_metereologica.eq('Chuva'),['dCondicoesVia[CondicaoMeteorologica] = "Chuva"'])
case('Urbano',d.uso_solo.eq('Sim'),['dCondicoesVia[UsoSolo] = "Urbano"'])
case('Causa caixa equivalente',d.causa_acidente.str.casefold().eq('transitar no acostamento'),['dCausa[CausaRegistrada] = "Transitar no acostamento"'])
case('Filtros combinados',d.Mes.eq('2025-01')&d.br.eq(116)&d.municipio.eq('FORTALEZA'),['dCalendario[AnoMes] = "2025-01"','dTrecho[BRNumero] = 116','dLocalidade[Municipio] = "FORTALEZA"'])
case('Sem registros',d.index<0,['dLocalidade[Municipio] = "__SEM_REGISTROS__"'])
case('Sem graves',~d.Grave,['fAcidentes[FlagGraveFatal] = FALSE()'])
case('Classificacao ausente',d.classificacao_acidente.eq('NA'),['dGravidade[ClassificacaoPRF] = "Não informado"'])

fields={'Acidentes':'Acidentes','Feridos':'Pessoas feridas','Mortes':'Mortes registradas','Graves':'Acidentes graves ou fatais',
        'PercentualGrave':'Percentual grave ou fatal','PercentualNoite':'Percentual em plena noite',
        'ConcentracaoTop5':'Concentracao top 5 trechos','PessoasDivergentes':'Ocorrencias pessoas divergentes'}
parts=[]
for c in cases:
    row='ROW("Cenario", '+json.dumps(c['name'],ensure_ascii=False)+', '+', '.join(json.dumps(k)+', ['+v+']' for k,v in fields.items())+')'
    parts.append('CALCULATETABLE('+row+(', '+', '.join(c['filters']) if c['filters'] else '')+')')
query='EVALUATE UNION('+',\n'.join(parts)+')'
(ROOT/'dax'/'validacao_filtros.dax').write_text(query,encoding='utf-8')

monthly=d.groupby('Mes').agg(Acidentes=('id','size'),Mortes=('mortos','sum'),Feridos=('feridos','sum'),Graves=('Grave','sum'))
monthly['PercentualGrave']=monthly.Graves/monthly.Acidentes
monthly.to_csv(ROOT/'output'/'prf'/'controle_mensal.csv',encoding='utf-8-sig')
temporal=[]
for month in ['2021-01','2021-02','2025-01','2025-12']:
    current=monthly.loc[month]
    previous=(pd.Period(month)-1).strftime('%Y-%m')
    prev=monthly.loc[previous] if previous in monthly.index else None
    temporal.append({'Mes':month,'Acidentes':int(current.Acidentes),'Anterior':int(prev.Acidentes) if prev is not None else None,
                     'Variacao':float((current.Acidentes-prev.Acidentes)/prev.Acidentes) if prev is not None else None})
months_cities=d.groupby(['municipio','Mes']).size()
zero_case=None
for (city,month),n in months_cities.items():
    previous=(pd.Period(month)-1).strftime('%Y-%m')
    if previous>='2021-01' and (city,previous) not in months_cities.index:
        zero_case={'Municipio':city,'Mes':month,'Atual':int(n),'Anterior':0}
        break
print(json.dumps({'query':query,'cases':cases,'temporal':temporal,'previous_zero_case':zero_case,'monthly_median_grave':float(monthly.PercentualGrave.median())},ensure_ascii=True))
