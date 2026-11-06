from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'dashboard'
css=(DIR/'dashboard.css').read_text(encoding='utf-8')
markup=(DIR/'dashboard.markup.html').read_text(encoding='utf-8')
js=(DIR/'dashboard.js').read_text(encoding='utf-8')
prefix='<div id="ld-prf-root" class="ld-root" data-theme="dark"><style>'+css+'</style><script type="application/json" class="ld-data">'
suffix='</script>'+markup+'<script>'+js+'</script></div>'
def lit(s):return '"'+s.replace('"','""')+'"'
def parts(s):return ' &\n'.join(lit(s[i:i+12000]) for i in range(0,len(s),12000))
expr='VAR _Json = [JSON Gold Dashboard PRF]\nVAR _Seguro = SUBSTITUTE(_Json, "<", "\\u003c")\nVAR _Inicio = '+parts(prefix)+'\nVAR _Fim = '+parts(suffix)+'\nRETURN IF(ISBLANK(_Json), "<div>Dados indisponíveis para este recorte.</div>", _Inicio & _Seguro & _Fim)'
measure=dict(name='HTML Dashboard PRF',tableName='fAcidentes',expression=expr,displayFolder='06 Apresentacao\\HTML Normal',
 description='HTML Normal/Regular. Unica fonte: [JSON Gold Dashboard PRF]. Filtros combinados de mes, municipio, tipo, rodovia, fase, causa e pista. Mediana mensal e media ponderada de gravidade no recorte, leitura executiva, causas, consequencias por pista e tabela ordenavel. Nao inventa limiares de risco. Preserva filtros nativos. Exige HTML Content Regular com scripts; incompatível com Lite/Secure. Validacao no navegador nao substitui a verificacao no visual real.')
if __name__=='__main__':
    (ROOT/'dax'/'html_dashboard_prf.dax').write_text(measure['name']+' =\n'+expr+'\n',encoding='utf-8')
    (DIR/'template.html').write_text(prefix+'__PRF_GOLD_PAYLOAD__'+suffix,encoding='utf-8')
    print(json.dumps(measure,ensure_ascii=True))
