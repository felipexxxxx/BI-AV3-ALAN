from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'dashboard'
p=D/'dashboard.js';s=p.read_text(encoding='utf-8')
anchor='    function render(){'
function='''    let lastSparkSeries=[];
    function sparkline(key){
      const field={acidentes:'acidentes',graves:'percentualGrave',mortes:'mortes',feridos:'feridos',noite:'percentualNoite',concentracao:'concentracaoTop5'}[key];
      const values=lastSparkSeries.map(s=>s[field]),valid=values.filter(v=>v!=null&&Number.isFinite(v));
      const lo=valid.length?Math.min(...valid):0,hi=valid.length?Math.max(...valid):0;
      const x=i=>values.length===1?80:4+i*152/(values.length-1),y=v=>hi===lo?13:22-(v-lo)/(hi-lo)*18;
      const segments=[];let segment=[];
      values.forEach((v,i)=>{if(v==null||!Number.isFinite(v)){if(segment.length)segments.push(segment);segment=[];}else segment.push({x:x(i),y:y(v)});});if(segment.length)segments.push(segment);
      const curve=pts=>pts.map((p,i)=>{if(!i)return 'M'+p.x+','+p.y;const a=pts[i-1],d=(p.x-a.x)/3;return 'C'+(a.x+d)+','+a.y+' '+(p.x-d)+','+p.y+' '+p.x+','+p.y;}).join(' ');
      const id='ld-spark-fill-'+key;
      const line=segments.map(curve).join(' '),area=segments.filter(p=>p.length>1).map(p=>curve(p)+' L'+p.at(-1).x+',25 L'+p[0].x+',25 Z').join(' ');
      const final=values.at(-1),dot=final==null||!Number.isFinite(final)?'':'<circle class="ld-spark-end" cx="'+x(values.length-1)+'" cy="'+y(final)+'" r="2.2"/>';
      const label=lastSparkSeries.length?'Tendência mensal: '+monthLabel(lastSparkSeries[0].mes)+' a '+monthLabel(lastSparkSeries.at(-1).mes)+'. '+(valid.length===1?'Um único período válido.':''): 'Sem série disponível.';
      return '<svg class="ld-sparkline" viewBox="0 0 160 26" preserveAspectRatio="none" role="img" aria-label="'+esc(label)+'"><defs><linearGradient id="'+id+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--ld-spark)" stop-opacity=".12"/><stop offset="100%" stop-color="var(--ld-spark)" stop-opacity="0"/></linearGradient></defs><path class="ld-spark-area" fill="url(#'+id+')" d="'+area+'"/><path class="ld-spark-line" d="'+line+'"/>'+dot+'</svg>';
    }
'''
s=s.replace(anchor,function+anchor)
s=s.replace("      const cards=[", "      lastSparkSeries=periods(rows).slice(-12).map(s=>({mes:s.mes,...aggregate(rows.filter(r=>r.mes===s.mes))}));\n      const cards=[")
s=s.replace("+detail+'</span>'+variation(key)","+detail+'</span>'+sparkline(key)+variation(key)")
s=s.replace("sort:{...state.sort},filters:","sparkSeries:lastSparkSeries.map(s=>({mes:s.mes,acidentes:s.acidentes,percentualGrave:s.percentualGrave,mortes:s.mortes,feridos:s.feridos,percentualNoite:s.percentualNoite,concentracaoTop5:s.concentracaoTop5})),sort:{...state.sort},filters:")
p.write_text(s,encoding='utf-8')
p=D/'dashboard.css';s=p.read_text(encoding='utf-8')+'''
.ld-root{--ld-spark:#64b9c1}.ld-root[data-theme=light]{--ld-spark:#087d83}.ld-kpi{padding-bottom:12px}.ld-sparkline{display:block;width:80%;height:26px;margin:4px 0 0;overflow:visible;pointer-events:none}.ld-spark-line{fill:none;stroke:var(--ld-spark);stroke-width:1.7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}.ld-spark-end{fill:var(--ld-spark);stroke:var(--ld-panel);stroke-width:1;vector-effect:non-scaling-stroke}.ld-spark-area{stroke:none}.ld-kpi .ld-variation{margin-top:3px}
''';p.write_text(s,encoding='utf-8')
print('Sparklines inseridos sem alterar valores ou badges existentes.')
