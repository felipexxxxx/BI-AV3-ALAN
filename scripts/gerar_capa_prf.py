from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];D=R/'dashboard'
prefix='<div id="cp-prf-root" class="cp-root"><style>'+(D/'capa.css').read_text(encoding='utf-8')+'</style><script type="application/json" class="cp-data">'
suffix='</script>'+(D/'capa.markup.html').read_text(encoding='utf-8')+'<script>'+(D/'capa.js').read_text(encoding='utf-8')+'</script></div>'
def parts(s):return ' &\n'.join('"'+s[i:i+12000].replace('"','""')+'"' for i in range(0,len(s),12000))
expr='VAR _Json = [JSON Gold Dashboard PRF]\nVAR _Seguro = SUBSTITUTE(_Json, "<", "\\u003c")\nVAR _Inicio = '+parts(prefix)+'\nVAR _Fim = '+parts(suffix)+'\nRETURN IF(ISBLANK(_Json), "<div>Dados indisponíveis.</div>", _Inicio & _Seguro & _Fim)'
(R/'dax/capa_prf.dax').write_text('HTML Capa PRF =\n'+expr,encoding='utf-8')
for src,target in [('preview_prf.html','capa_prf.html'),('preview_prf_externo.html','capa_prf_externo.html'),('preview_prf_vazio.html','capa_prf_vazio.html')]:
 payload=re.search(r'<script type="application/json" class="ld-data">([\s\S]*?)</script>',(D/src).read_text(encoding='utf-8')).group(1)
 (D/target).write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;background:#09131e}</style>'+prefix+payload+suffix+'</html>',encoding='utf-8')
print(json.dumps(dict(name='HTML Capa PRF',tableName='fAcidentes',expression=expr,displayFolder='06 Apresentacao\\HTML Normal',description='Capa PRF; unica fonte JSON Gold Dashboard PRF. Anel da proporcao grave/fatal, sem meta. Animacao finita requestAnimationFrame com reduced-motion. Espaco reservado para botao nativo Ir para Analise. A entrada pode repetir quando o Power BI recriar o visual.'),ensure_ascii=True))
