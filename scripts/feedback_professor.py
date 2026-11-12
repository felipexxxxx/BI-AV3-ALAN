from pathlib import Path
import re
R=Path(__file__).resolve().parents[1];D=R/'dashboard'
p=D/'dashboard.markup.html';s=p.read_text(encoding='utf-8')
labels={'mes':'PERÍODO','municipio':'MUNICÍPIO','tipo':'TIPO DE ACIDENTE','rodovia':'RODOVIA / TRECHO','fase':'FASE DO DIA','causa':'CAUSA REGISTRADA','pista':'TIPO DE PISTA'}
for k,label in labels.items():
 s=re.sub(r'<label class="ld-field">[^<]*<select[^>]*data-filter="'+k+r'"[^>]*></select></label>',f'<div class="ld-field"><span>{label}</span><button type="button" class="ld-select" data-picker="{k}" aria-expanded="false" aria-haspopup="dialog" data-hc-suppress="filter"></button></div>',s)
s=s.replace('Selecione um mês no gráfico · referências recalculadas para o recorte','Clique para selecionar · Ctrl+clique soma ou remove meses. Gráfico mantém o período de referência.')
s=s.replace('Prioridade de investigação','Onde agir e por quê')
s=s.replace('Dez trechos com mais ocorrências · selecione os títulos para ordenar esta seleção','Dez trechos com mais ocorrências · clique no trecho para investigar; cabeçalhos ordenam')
s=s.replace('<div class="ld-tooltip"','<div class="ld-filter-popup" data-popup hidden data-hc-suppress="filter"></div>\n<div class="ld-tooltip"')
p.write_text(s,encoding='utf-8')
p=D/'dashboard.js';s=p.read_text(encoding='utf-8')
s=s.replace("'causa','pista'];","'causa','pista','trechoChave'];")
s=s.replace("previous.filters?.[k]||''","Array.isArray(previous.filters?.[k])?previous.filters[k]:(previous.filters?.[k]?[previous.filters[k]]:[])")
start=s.index('    const filtered=');end=s.index('    const periods=',start)
s=s[:start]+'''    const matches=(r,k)=>!state.filters[k].length||state.filters[k].includes(r[k]);
    const filtered=(except=null)=>base.filter(r=>keys.every(k=>k===except||matches(r,k)));
    const names={mes:'Período',municipio:'Município',tipo:'Tipo de acidente',rodovia:'Rodovia / trecho',fase:'Fase do dia',causa:'Causa registrada',pista:'Tipo de pista'};
    const norm=s=>String(s).normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
    let opened=null,query='';
    const options=()=>{root.querySelectorAll('[data-picker]').forEach(b=>{const k=b.dataset.picker,vs=k==='rodovia'?[...state.filters.rodovia,...state.filters.trechoChave]:state.filters[k];b.textContent=!vs.length?'Todos':vs.length===1?(k==='mes'?monthLabel(vs[0]):k==='rodovia'&&state.filters.trechoChave.length?base.find(r=>r.trechoChave===vs[0])?.trecho||vs[0]:vs[0]):vs.length+' selecionados';b.setAttribute('aria-label',names[k]+': '+b.textContent);});};
    const setFilter=(k,v)=>{if(!keys.includes(k))return;state.filters[k]=Array.isArray(v)?[...new Set(v)]:(v?[v]:[]);options();save();render();};
    const toggleFilter=(k,v,add)=>{setFilter(k,add?(state.filters[k].includes(v)?state.filters[k].filter(x=>x!==v):[...state.filters[k],v]):[v]);};
    const closePopup=()=>{el('[data-popup]').hidden=true;root.querySelectorAll('[data-picker]').forEach(b=>b.setAttribute('aria-expanded','false'));opened=null;};
    function drawChoices(){
      const k=opened;if(!k)return;const host=el('[data-filter-choices]'),q=norm(query);
      const check=(key,value,label,checked,group=false,mixed=false)=>'<label class="ld-choice"><input type="checkbox" data-choice="'+key+'" value="'+esc(value)+'" '+(group?'data-group="true" ':'')+(mixed?'data-mixed="true" ':'')+(checked?'checked ':'')+'/><span>'+esc(label)+'</span></label>';
      let html='';
      if(k==='mes'||k==='rodovia'){
        const groupsMap=new Map();const values=k==='mes'?[...new Set((data.seriesMensais||[]).map(r=>r.mes))].sort():[...new Map(base.map(r=>[r.trechoChave,r])).values()].sort((a,b)=>a.rodovia.localeCompare(b.rodovia)||a.inicio-b.inicio);
        for(const v of values){const group=k==='mes'?v.slice(0,4):v.rodovia;if(!groupsMap.has(group))groupsMap.set(group,[]);groupsMap.get(group).push(v);}
        for(const[g,vs]of groupsMap){const visible=vs.filter(v=>norm(g+' '+(k==='mes'?monthLabel(v):v.trecho)).includes(q));if(!visible.length)continue;const leafKey=k==='mes'?'mes':'trechoChave';const selected=v=>state.filters[leafKey].includes(k==='mes'?v:v.trechoChave)||(k==='rodovia'&&state.filters.rodovia.includes(g));const count=vs.filter(selected).length;html+='<details '+(q||count?'open':'')+'><summary>'+esc(g)+'</summary>'+check(k,g,'Selecionar '+g,count===vs.length,true,count>0&&count<vs.length)+'<div class="ld-choice-children">'+visible.map(v=>check(leafKey,k==='mes'?v:v.trechoChave,k==='mes'?monthLabel(v):v.trecho,selected(v))).join('')+'</div></details>';}
      }else html=[...new Set(base.map(r=>r[k]))].sort((a,b)=>a.localeCompare(b,'pt-BR')).filter(v=>norm(v).includes(q)).map(v=>check(k,v,v,state.filters[k].includes(v))).join('');
      host.innerHTML=html||'<p class="ld-small-note">Nenhuma opção encontrada.</p>';host.querySelectorAll('[data-mixed]').forEach(e=>e.indeterminate=true);
    }
    function openPopup(button){if(opened===button.dataset.picker){closePopup();return;}closePopup();opened=button.dataset.picker;query='';const pop=el('[data-popup]');pop.innerHTML='<div class="ld-popup-head"><strong>'+names[opened]+'</strong><button type="button" data-popup-close aria-label="Fechar filtro">×</button></div><input type="search" data-filter-search aria-label="Pesquisar opções" placeholder="Pesquisar…"/><div class="ld-filter-choices" data-filter-choices></div><button type="button" data-filter-reset>Limpar este filtro</button>';pop.hidden=false;button.setAttribute('aria-expanded','true');const b=button.getBoundingClientRect();pop.style.width=Math.min(340,window.innerWidth-16)+'px';pop.style.left=Math.max(8,Math.min(b.left,window.innerWidth-Math.min(340,window.innerWidth-16)-8))+'px';pop.style.top=Math.max(8,Math.min(b.bottom+5,window.innerHeight-350))+'px';drawChoices();el('[data-filter-search]').focus();}
'''+s[end:]
s=s.replace('const periods=(rows)=>','const periods=(rows,selected=true)=>').replace("!state.filters.mes||m===state.filters.mes","!selected||!state.filters.mes.length||state.filters.mes.includes(m)")
s=s.replace("!state.filters[k]||r[k]===state.filters[k]","matches(r,k)")
s=s.replace("const end=state.filters.mes||", "const end=state.filters.mes.length===1?state.filters.mes[0]:")
s=s.replace("      const prior=end?", "      lastSeries=periods(history,false);\n      const prior=end?")
s=s.replace("      const choices=keys.filter(k=>state.filters[k]).map(k=>k==='mes'?monthLabel(state.filters[k]):state.filters[k]);", "      const choices=keys.filter(k=>state.filters[k].length).map(k=>(names[k]||'Trecho')+': '+(state.filters[k].length>2?state.filters[k].length+' selecionados':state.filters[k].map(v=>k==='mes'?monthLabel(v):k==='trechoChave'?base.find(r=>r.trechoChave===v)?.trecho||v:v).join(', ')));")
s=s.replace("keys.forEach(k=>state.filters[k]='')","keys.forEach(k=>state.filters[k]=[])")
s=s.replace("setFilter(rank.dataset.filterKind,rank.dataset.filterValue)","toggleFilter(rank.dataset.filterKind,rank.dataset.filterValue,e.ctrlKey||e.metaKey)")
s=s.replace("setFilter('mes',month.dataset.month)","toggleFilter('mes',month.dataset.month,e.ctrlKey||e.metaKey)")
s=s.replace("data-month=\"'+s.mes+'\"", "aria-pressed=\"'+state.filters.mes.includes(s.mes)+'\" data-month=\"'+s.mes+'\"")
s=s.replace("data-row-key=\"'+esc(t.k)+'\"", "data-row-key=\"'+esc(t.k)+'\"")
s=s.replace("<span class=\"ld-trecho-name\">'+esc(t.rodovia)","<button type=\"button\" class=\"ld-trecho-name ld-trecho-link\" data-investigate=\"'+esc(t.k)+'\">'+esc(t.rodovia)")
s=s.replace("+n(t.inicio+10)+'</span><span", "+n(t.inicio+10)+'</button><span")
# Replace decision output only; keep calculations and rankings.
start=s.index("        el('[data-readout]').innerHTML=");end=s.index('\n',start)
s=s[:start]+'''        const target=rows.filter(r=>r.trechoChave===priority.k),context=filtered('fase').filter(r=>r.trechoChave===priority.k),night=aggregate(context.filter(r=>r.fase==='Plena Noite')),day=aggregate(context.filter(r=>r.fase==='Pleno dia'));
        const cause=ranked(target,'causa').sort(byVolume)[0],type=ranked(target,'tipo').sort(byConsequences)[0];
        const comparison=night.acidentes&&day.acidentes?'No mesmo trecho e período, plena noite: '+n(night.graves)+'/'+n(night.acidentes)+' graves/fatais ('+pct(night.percentualGrave)+'); pleno dia: '+n(day.graves)+'/'+n(day.acidentes)+' ('+pct(day.percentualGrave)+'). Diferença: '+decimal.format((night.percentualGrave-day.percentualGrave)*100)+' p.p.':'Não há ocorrências suficientes nas duas fases para comparar noite e pleno dia neste recorte.';
        const focus=night.acidentes&&day.acidentes?(night.percentualGrave>day.percentualGrave?' Observar especialmente as condições noturnas.':night.percentualGrave<day.percentualGrave?' A proporção diurna é maior neste recorte.':' As proporções são iguais neste recorte.') :'';
        const action=/pedestre/i.test(type.name)?'Vistoriar travessias, acessos de pedestres e visibilidade.':/animal/i.test(type.name)?'Vistoriar pontos de entrada e presença de animais; revisar os registros com as equipes locais.':/traseira/i.test(type.name)?'Vistoriar aproximações, filas, sinalização e condições de visibilidade; avaliar atuação sobre distância de segurança.':/transversal|lateral/i.test(type.name)?'Vistoriar acessos, cruzamentos, conflitos de circulação e visibilidade.':'Vistoriar o local e revisar a dinâmica dos acidentes registrados antes de definir a intervenção.';
        const pavement=context.filter(r=>/buraco|defeito.*via|pavimento/i.test(r.causa)).length;
        el('[data-readout]').innerHTML='<p class="ld-insight-number">'+pct(priorityShare)+'</p><p class="ld-insight-title">'+priorityLabel+'</p><p class="ld-insight-copy"><strong>'+esc(priority.rotulo)+'</strong>: '+n(priority.acidentes)+' ocorrências, '+n(priority.graves)+' graves/fatais e '+n(priority.mortes)+' mortes no recorte.</p><div class="ld-decision"><strong>Comparação que orienta a vistoria</strong><p>'+comparison+'</p><small>Comparação mantém os demais filtros e retira apenas o filtro de fase do dia. Proporção entre acidentes registrados; não é risco por veículo.</small></div><div class="ld-decision"><strong>O que os registros apontam</strong><p>Tipo com mais graves/fatais no trecho: '+esc(type.name)+' ('+n(type.graves)+' em '+n(type.acidentes)+' ocorrências). Causa mais registrada: '+esc(cause.name)+' ('+n(cause.acidentes)+').</p></div><div class="ld-action"><strong>Ação a avaliar</strong>'+action+focus+' '+(pavement?n(pavement)+' registros mencionam defeito de via/pavimento; confirmar em vistoria.':'Não há registro de causa de pavimento identificado neste contexto; não atribuir os acidentes a buracos.')+'</div><p class="ld-small-note">A causa registrada é uma pista de investigação, não prova causal. Conferir localização exata, fluxo, condições atuais e '+n(target.filter(r=>r.q).length)+' registros com alertas antes da decisão.</p><button type="button" class="ld-clear" data-investigate="'+esc(priority.k)+'">Investigar este trecho</button>';
'''+s[end:]
# New filter interactions.
start=s.index("    root.addEventListener('change'");end=s.index("    root.addEventListener('click'",start)
s=s[:start]+'''    root.addEventListener('input',e=>{if(e.target.matches('[data-filter-search]')){query=e.target.value;drawChoices();}});
    root.addEventListener('change',e=>{const c=e.target.closest('[data-choice]');if(!c)return;e.stopPropagation();let k=c.dataset.choice,vs=[c.value];if(c.dataset.group){if(k==='mes')vs=[...new Set((data.seriesMensais||[]).map(r=>r.mes))].filter(v=>v.startsWith(c.value));else{k='trechoChave';vs=[...new Set(base.filter(r=>r.rodovia===c.value).map(r=>r.trechoChave))];}}if(k==='trechoChave'&&state.filters.rodovia.length){state.filters.trechoChave=[...new Set([...state.filters.trechoChave,...base.filter(r=>state.filters.rodovia.includes(r.rodovia)).map(r=>r.trechoChave)])];state.filters.rodovia=[];}setFilter(k,c.checked?[...state.filters[k],...vs]:state.filters[k].filter(v=>!vs.includes(v)));drawChoices();});
    root.addEventListener('click',e=>{const p=e.target.closest('[data-picker]');if(p){e.stopPropagation();openPopup(p);}if(e.target.closest('[data-popup-close]'))closePopup();if(e.target.closest('[data-filter-reset]')){const k=opened;setFilter(k,[]);if(k==='rodovia')setFilter('trechoChave',[]);drawChoices();}const t=e.target.closest('[data-investigate]');if(t){e.stopPropagation();setFilter('trechoChave',[t.dataset.investigate]);}});
    document.addEventListener('click',e=>{if(!root.contains(e.target)||!e.target.closest('[data-popup],[data-picker]'))closePopup();});
    root.addEventListener('keydown',e=>{if(e.key==='Escape'&&opened){const b=el('[data-picker="'+opened+'"]');closePopup();b?.focus();}});
'''+s[end:]
s=s.replace("keys.forEach(k=>state.filters[k]=[]);options();", "keys.forEach(k=>state.filters[k]=[]);closePopup();options();")
s=s.replace("' · Selecionar este mês'", "' · Selecionar; Ctrl combina meses'")
p.write_text(s,encoding='utf-8')
p=D/'dashboard.css';s=p.read_text(encoding='utf-8')+'''
.ld-filter-popup{position:fixed;z-index:10000;background:var(--ld-panel);color:var(--ld-fg);border:1px solid var(--ld-line);box-shadow:0 12px 40px #0005;border-radius:12px;padding:12px;max-height:340px;overflow:auto}.ld-popup-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}.ld-popup-head button,.ld-filter-popup>button{background:var(--ld-soft);color:var(--ld-fg);border:1px solid var(--ld-line);border-radius:6px;padding:5px 9px}.ld-filter-popup input[type=search]{width:100%;border:1px solid var(--ld-line);border-radius:6px;background:var(--ld-bg);color:var(--ld-fg);padding:9px;font:inherit}.ld-filter-choices{max-height:200px;overflow:auto;margin:8px 0}.ld-filter-choices summary{cursor:pointer;font-weight:600;padding:7px}.ld-choice{display:flex;align-items:center;gap:9px;padding:7px 4px;font-size:12px;cursor:pointer}.ld-choice input{accent-color:var(--ld-accent);width:16px;height:16px;flex-shrink:0}.ld-choice-children{margin-left:18px}.ld-select{text-align:left;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;cursor:pointer}.ld-bar[aria-pressed=true]{opacity:1;stroke:var(--ld-fg);stroke-width:1.5}.ld-line-point[aria-pressed=true]{r:4}.ld-decision{border-top:1px solid var(--ld-line);padding-top:12px;margin-top:12px;font-size:12px}.ld-decision strong{display:block;margin-bottom:5px}.ld-decision small{display:block;color:var(--ld-muted);font-size:10px;margin-top:6px}.ld-trecho-link{background:none;border:0;color:var(--ld-accent);text-align:left;padding:0;cursor:pointer;font:inherit;text-decoration:underline;text-underline-offset:3px}.ld-readout [data-investigate]{margin-top:12px}.ld-root input:focus-visible,.ld-root summary:focus-visible{outline:2px solid var(--ld-accent);outline-offset:2px}
''';p.write_text(s,encoding='utf-8')
print('Feedback aplicado nos fontes.')
