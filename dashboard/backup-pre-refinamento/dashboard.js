(function(){
  'use strict';
  const root=document.getElementById('ld-prf-root');
  if(!root)return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const integer=new Intl.NumberFormat('pt-BR',{maximumFractionDigits:0});
  const decimal=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1});
  const n=v=>integer.format(v||0), pct=v=>v==null?'—':decimal.format(v*100)+'%';
  const el=s=>root.querySelector(s);
  const monthLabel=s=>{const [y,m]=s.split('-');return new Date(Number(y),Number(m)-1,1).toLocaleDateString('pt-BR',{month:'short',year:'numeric'}).replace('.','');};
  try{
    const data=JSON.parse(el('.ld-data').textContent);
    if(!data.meta?.baseCompleta||!Array.isArray(data.baseInterativa))throw Error('Contrato de dados incompleto.');
    const toMap=a=>new Map((a||[]).map(x=>[x.k,x]));
    const loc=toMap(data.localidades),trecho=toMap(data.trechos),cond=toMap(data.condicoes),tipos=toMap(data.tipos),causas=toMap(data.causas),gravidades=toMap(data.gravidades);
    const base=data.baseInterativa.map(r=>{
      const l=loc.get(r.l),t=trecho.get(r.t),v=cond.get(r.v),c=tipos.get(r.c),ca=causas.get(r.ca),g=gravidades.get(r.g);
      if(!l||!t||!v||!c||!ca||!g)throw Error('Referência de dados ausente.');
      return {...r,mes:r.d.slice(0,7),municipio:l.municipio,uf:l.uf,rodovia:t.rodovia,trecho:t.rotulo,trechoChave:t.chave,inicio:t.inicio,tipo:c.rotulo,causa:ca.rotulo,gravidade:g.rotulo,fase:v.fase,pista:v.pista,clima:v.clima,grave:r.fg>0||r.m>0,noite:v.fase==='Plena Noite'};
    });
    if(base.length!==(data.meta.linhas??0)||new Set(base.map(r=>r.id)).size!==base.length)throw Error('Base incompleta ou IDs repetidos.');
    const keys=['mes','municipio','tipo','rodovia','fase','causa','pista','trechoChave'];
    const previous=window.__ldPRFState||{};
    const sortKeys=['trecho','acidentes','graves','percentualGrave','feridos','mortes'];
    const state={theme:previous.theme==='light'?'light':'dark',filters:Object.fromEntries(keys.map(k=>[k,Array.isArray(previous.filters?.[k])?previous.filters[k]:(previous.filters?.[k]?[previous.filters[k]]:[])])),sort:sortKeys.includes(previous.sort?.key)?{key:previous.sort.key,dir:previous.sort.dir==='asc'?'asc':'desc'}:{key:'acidentes',dir:'desc'}};
    const save=()=>{window.__ldPRFState={theme:state.theme,filters:{...state.filters},sort:{...state.sort}};};
    const groups=(rows,key)=>{const m=new Map();for(const r of rows){const k=r[key];if(!m.has(k))m.set(k,[]);m.get(k).push(r);}return m;};
    const basic=rows=>({acidentes:rows.length,graves:rows.filter(r=>r.grave).length,feridos:rows.reduce((s,r)=>s+r.f,0),feridosGraves:rows.reduce((s,r)=>s+r.fg,0),mortes:rows.reduce((s,r)=>s+r.m,0),plenaNoite:rows.filter(r=>r.noite).length,comAlertas:rows.filter(r=>r.q).length,pessoasDivergentes:rows.filter(r=>r.qp).length,classificacoesDivergentes:rows.filter(r=>r.qc).length,classificacoesAusentes:rows.filter(r=>r.qa).length});
    const ranked=(rows,key)=>[...groups(rows,key)].map(([name,rs])=>{const a=basic(rs);return {name,...a,percentualGrave:a.graves/a.acidentes};});
    const byVolume=(x,y)=>y.acidentes-x.acidentes||x.name.localeCompare(y.name,'pt-BR');
    const byConsequences=(x,y)=>y.graves-x.graves||y.acidentes-x.acidentes||x.name.localeCompare(y.name,'pt-BR');
    const median=values=>{const v=values.filter(x=>typeof x==='number'&&Number.isFinite(x)).sort((a,b)=>a-b);const mid=Math.floor(v.length/2);return !v.length?null:v.length%2?v[mid]:(v[mid-1]+v[mid])/2;};
    const aggregate=rows=>{
      const a=basic(rows);a.percentualGrave=a.acidentes?a.graves/a.acidentes:null;a.percentualNoite=a.acidentes?a.plenaNoite/a.acidentes:null;
      a.trechos=[...groups(rows,'trechoChave')].map(([k,rs])=>({k,rotulo:rs[0].trecho,rodovia:rs[0].rodovia,inicio:rs[0].inicio,...basic(rs)})).sort((x,y)=>y.acidentes-x.acidentes||x.k.localeCompare(y.k));
      a.concentracaoTop5=a.acidentes?a.trechos.slice(0,5).reduce((s,t)=>s+t.acidentes,0)/a.acidentes:null;
      return a;
    };
    const matches=(r,k)=>!state.filters[k].length||state.filters[k].includes(r[k]);
    const filtered=(except=null)=>base.filter(r=>keys.every(k=>k===except||matches(r,k)));
    const names={mes:'Período',municipio:'Município',tipo:'Tipo de acidente',rodovia:'Rodovia / trecho',fase:'Fase do dia',causa:'Causa registrada',pista:'Tipo de pista'};
    const norm=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    let opened=null,query='';
    const options=()=>{root.querySelectorAll('[data-picker]').forEach(b=>{const k=b.dataset.picker,vs=k==='rodovia'?[...state.filters.rodovia,...state.filters.trechoChave]:state.filters[k];b.textContent=!vs.length?'Todos':vs.length===1?(k==='mes'?monthLabel(vs[0]):k==='rodovia'&&state.filters.trechoChave.length?base.find(r=>r.trechoChave===vs[0])?.trecho||vs[0]:vs[0]):vs.length+' selecionados';b.setAttribute('aria-label',names[k]+': '+b.textContent);});};
    const setFilter=(k,v)=>{if(!keys.includes(k))return;state.filters[k]=Array.isArray(v)?[...new Set(v)]:(v?[v]:[]);options();save();render();};
    const toggleFilter=(k,v,add)=>{setFilter(k,add?(state.filters[k].includes(v)?state.filters[k].filter(x=>x!==v):[...state.filters[k],v]):[v]);};
    const closePopup=()=>{el('[data-popup]').hidden=true;root.querySelectorAll('[data-picker]').forEach(b=>b.setAttribute('aria-expanded','false'));opened=null;};
    function drawChoices(){
      const k=opened;if(!k)return;const host=el('[data-filter-choices]'),q=norm(query);const found=text=>q.split(/\s+/).every(w=>norm(text).includes(w));
      const check=(key,value,label,checked,group=false,mixed=false)=>'<label class="ld-choice"><input type="checkbox" data-choice="'+key+'" value="'+esc(value)+'" '+(group?'data-group="true" ':'')+(mixed?'data-mixed="true" ':'')+(checked?'checked ':'')+'/><span>'+esc(label)+'</span></label>';
      let html='';
      if(k==='mes'||k==='rodovia'){
        const groupsMap=new Map();const values=k==='mes'?[...new Set((data.seriesMensais||[]).map(r=>r.mes))].sort():[...new Map(base.map(r=>[r.trechoChave,r])).values()].sort((a,b)=>a.rodovia.localeCompare(b.rodovia)||a.inicio-b.inicio);
        for(const v of values){const group=k==='mes'?v.slice(0,4):v.rodovia;if(!groupsMap.has(group))groupsMap.set(group,[]);groupsMap.get(group).push(v);}
        for(const[g,vs]of groupsMap){const visible=vs.filter(v=>found(g+' '+(k==='mes'?monthLabel(v):v.trecho)));if(!visible.length)continue;const leafKey=k==='mes'?'mes':'trechoChave';const selected=v=>state.filters[leafKey].includes(k==='mes'?v:v.trechoChave)||(k==='rodovia'&&state.filters.rodovia.includes(g));const count=vs.filter(selected).length;html+='<details '+(q||count?'open':'')+'><summary>'+esc(g)+'</summary>'+check(k,g,'Selecionar '+g,count===vs.length,true,count>0&&count<vs.length)+'<div class="ld-choice-children">'+visible.map(v=>check(leafKey,k==='mes'?v:v.trechoChave,k==='mes'?monthLabel(v):v.trecho,selected(v))).join('')+'</div></details>';}
      }else html=[...new Set(base.map(r=>r[k]))].sort((a,b)=>a.localeCompare(b,'pt-BR')).filter(v=>found(v)).map(v=>check(k,v,v,state.filters[k].includes(v))).join('');
      host.innerHTML=html||'<p class="ld-small-note">Nenhuma opção encontrada.</p>';host.querySelectorAll('[data-mixed]').forEach(e=>e.indeterminate=true);
    }
    function openPopup(button){if(opened===button.dataset.picker){closePopup();return;}closePopup();opened=button.dataset.picker;query='';const pop=el('[data-popup]');pop.innerHTML='<div class="ld-popup-head"><strong>'+names[opened]+'</strong><button type="button" data-popup-close aria-label="Fechar filtro">×</button></div><input type="search" data-filter-search aria-label="Pesquisar opções" placeholder="Pesquisar…"/><div class="ld-filter-choices" data-filter-choices></div><button type="button" data-filter-reset>Limpar este filtro</button>';pop.hidden=false;button.setAttribute('aria-expanded','true');const b=button.getBoundingClientRect();pop.style.width=Math.min(340,window.innerWidth-16)+'px';pop.style.left=Math.max(8,Math.min(b.left,window.innerWidth-Math.min(340,window.innerWidth-16)-8))+'px';pop.style.top=Math.max(8,Math.min(b.bottom+5,window.innerHeight-350))+'px';drawChoices();el('[data-filter-search]').focus();}
    const periods=(rows,selected=true)=>{
      const observed=groups(rows,'mes');
      const months=(data.seriesMensais||[]).map(x=>x.mes).filter(m=>!selected||!state.filters.mes.length||state.filters.mes.includes(m));
      return months.map(m=>{const a=basic(observed.get(m)||[]);return {mes:m,...a,percentualGrave:a.acidentes?a.graves/a.acidentes:null};});
    };
    let lastRows=[],lastStats=null,lastSeries=[],lastMedian=null,lastExecutive=null,lastRoads=[],lastPistas=[];
    function renderTable(){
      const selection=lastStats?.trechos.slice(0,10)||[];
      const compare=new Intl.Collator('pt-BR',{numeric:true,sensitivity:'base'});
      const value=t=>state.sort.key==='trecho'?t.rotulo:state.sort.key==='percentualGrave'?t.graves/t.acidentes:t[state.sort.key];
      const sorted=[...selection].sort((a,b)=>{const av=value(a),bv=value(b),order=typeof av==='string'?compare.compare(av,bv):av-bv;return (state.sort.dir==='asc'?order:-order)||compare.compare(a.k,b.k);});
      el('[data-trechos]').innerHTML=sorted.map(t=>'<tr data-row-key="'+esc(t.k)+'"><td data-value="'+esc(t.rotulo)+'"><button type="button" class="ld-trecho-name ld-trecho-link" data-investigate="'+esc(t.k)+'">'+esc(t.rodovia)+' · km '+n(t.inicio)+'–'+n(t.inicio+10)+'</button><span class="ld-trecho-sub">Ceará · intervalo de 10 km</span></td><td class="ld-num" data-label="Acidentes" data-value="'+t.acidentes+'">'+n(t.acidentes)+'</td><td class="ld-num" data-label="Graves/fatais" data-value="'+t.graves+'">'+n(t.graves)+'</td><td class="ld-num ld-severity" data-label="% graves/fatais" data-value="'+t.graves/t.acidentes+'">'+pct(t.graves/t.acidentes)+'</td><td class="ld-num" data-label="Feridos" data-value="'+t.feridos+'">'+n(t.feridos)+'</td><td class="ld-num" data-label="Mortes" data-value="'+t.mortes+'">'+n(t.mortes)+'</td></tr>').join('');
      root.querySelectorAll('[data-sort-header]').forEach(th=>{const active=th.dataset.sortHeader===state.sort.key;th.setAttribute('aria-sort',active?(state.sort.dir==='asc'?'ascending':'descending'):'none');th.querySelector('[data-sort-icon]').textContent=active?(state.sort.dir==='asc'?'↑':'↓'):'↕';th.querySelector('button').setAttribute('aria-label','Ordenar por '+th.querySelector('button').textContent.replace(/[↑↓↕]/g,'').trim()+(active?', ordem '+(state.sort.dir==='asc'?'crescente':'decrescente'):', sem ordenação ativa'));});
    }
    function drawMonthly(){
      const host=el('[data-monthly]'),series=lastSeries;
      if(!lastRows.length||!series.length){host.innerHTML='<div class="ld-chart-empty">Sem dados no período selecionado.</div>';return;}
      const w=Math.max(230,Math.floor(host.clientWidth)),h=244,left=36,right=38,top=35,bottom=35,pw=w-left-right,ph=h-top-bottom;
      const raw=Math.max(1,...series.map(s=>s.acidentes)),power=Math.pow(10,Math.floor(Math.log10(raw/4))),unit=[1,2,5,10].find(x=>x*power>=raw/4)*power,yMax=Math.max(unit,Math.ceil(raw/unit)*unit);
      const x=i=>left+(i+.5)*pw/series.length,y=v=>top+ph-v/yMax*ph,yp=v=>top+ph-v*ph;
      let grid='',bars='',labels='',points='',path='',active=false;
      for(let v=0;v<=yMax+unit/10;v+=unit){const yy=y(v);grid+='<line class="ld-grid-line" x1="'+left+'" x2="'+(w-right)+'" y1="'+yy+'" y2="'+yy+'"/><text x="'+(left-7)+'" y="'+(yy+4)+'" text-anchor="end">'+n(v)+'</text>';}
      [0,.5,1].forEach(v=>{grid+='<text x="'+(w-right+7)+'" y="'+(yp(v)+4)+'">'+Math.round(v*100)+'%</text>';});
      grid+='<text class="ld-axis-title" x="'+left+'" y="13">Acidentes (n)</text><text class="ld-axis-title" x="'+(w-right)+'" y="13" text-anchor="end">Graves/fatais (%)</text>';
      const tickEvery=Math.max(1,Math.ceil(series.length/Math.max(2,Math.floor(pw/85))));
      series.forEach((s,i)=>{
        const xx=x(i),yy=y(s.acidentes),bw=Math.max(1,Math.min(25,pw/series.length*.62));
        const delta=s.percentualGrave==null||lastStats.percentualGrave==null?null:s.percentualGrave-lastStats.percentualGrave;
        const comparison=delta==null?'Sem proporção calculável neste mês.':Math.abs(delta)<1e-12?'Igual à média ponderada do recorte.':decimal.format(Math.abs(delta)*100)+' p.p. '+(delta>0?'acima':'abaixo')+' da média ponderada do recorte.';
        const tip=monthLabel(s.mes)+'\n'+n(s.acidentes)+' acidentes\n'+n(s.graves)+' graves ou fatais · '+pct(s.percentualGrave)+'\n'+n(s.feridos)+' feridos · '+n(s.mortes)+' mortes\nMediana mensal: '+pct(lastMedian)+'\n'+comparison+'\n'+n(s.comAlertas)+' registros com alertas de qualidade';
        bars+='<rect class="ld-bar" x="'+(xx-bw/2)+'" y="'+yy+'" width="'+bw+'" height="'+Math.max(0,top+ph-yy)+'" aria-pressed="'+state.filters.mes.includes(s.mes)+'" data-month="'+s.mes+'" data-hc-suppress="filter" data-tip="'+esc(tip)+'" role="button" tabindex="0" aria-label="'+esc(tip+' · Selecionar; Ctrl combina meses')+'"/>';
        if(s.percentualGrave!=null){path+=(active?'L':'M')+xx+','+yp(s.percentualGrave)+' ';active=true;points+='<circle class="ld-line-point" cx="'+xx+'" cy="'+yp(s.percentualGrave)+'" r="'+(series.length>24?1.7:3)+'" aria-pressed="'+state.filters.mes.includes(s.mes)+'" data-month="'+s.mes+'" data-hc-suppress="filter" data-tip="'+esc(tip)+'" role="button" tabindex="0" aria-label="'+esc(tip+' · Selecionar; Ctrl combina meses')+'"/>';}else active=false;
        if(i%tickEvery===0||series.length===1){const lab=new Date(s.mes+'-02T12:00:00').toLocaleDateString('pt-BR',{month:'short',year:'2-digit'}).replace('.','');labels+='<text x="'+xx+'" y="'+(h-8)+'" text-anchor="middle">'+esc(lab)+'</text>';}
      });
      const medianLine=lastMedian==null?'':'<line class="ld-median-line" x1="'+left+'" x2="'+(w-right)+'" y1="'+yp(lastMedian)+'" y2="'+yp(lastMedian)+'" aria-label="Mediana mensal '+pct(lastMedian)+'"/>';
      host.innerHTML='<svg class="ld-monthly" viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Ocorrências mensais, percentual grave/fatal e mediana mensal. Eixos nomeados de quantidade e percentual.">'+grid+bars+medianLine+'<path class="ld-curve" d="'+path+'"/>'+points+labels+'</svg>';
      const months=periods(lastRows).filter(s=>s.percentualGrave!=null).length;
      el('[data-monthly-note]').textContent='Mediana dos meses do recorte: '+pct(lastMedian)+' · média ponderada do recorte: '+pct(lastStats.percentualGrave)+(months===1?' · Um único mês com ocorrências; sem comparação temporal.':' · '+n(months)+' meses com ocorrências.');
    }
    let lastSparkSeries=[];
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
    function render(){
      const rows=filtered(),a=aggregate(rows);lastRows=rows;lastStats=a;lastSeries=periods(rows);lastMedian=median(lastSeries.map(s=>s.percentualGrave));lastExecutive=null;lastRoads=[];lastPistas=[];
      root.dataset.theme=state.theme;
      el('[data-theme-toggle]').textContent=state.theme==='dark'?'Modo claro ↗':'Modo escuro ↗';
      el('[data-theme-toggle]').setAttribute('aria-pressed',String(state.theme==='light'));
      const history=base.filter(r=>keys.every(k=>k==='mes'||matches(r,k)));
      const end=state.filters.mes.length?[...state.filters.mes].sort().at(-1):[...new Set(history.map(r=>r.mes))].sort().at(-1);
      lastSeries=periods(history,false);
      const prior=end?new Date(Number(end.slice(0,4)),Number(end.slice(5))-2,1):null;
      const priorKey=prior?prior.getFullYear()+'-'+String(prior.getMonth()+1).padStart(2,'0'):'';
      const current=aggregate(history.filter(r=>r.mes===end)),previous=aggregate(history.filter(r=>r.mes===priorKey));
      const metricKeys={acidentes:'acidentes',graves:'percentualGrave',mortes:'mortes',feridos:'feridos',noite:'percentualNoite',concentracao:'concentracaoTop5'};
      const variation=key=>{const field=metricKeys[key],x=current[field],y=previous[field],ratio=['graves','noite','concentracao'].includes(key);if(!previous.acidentes||!current.acidentes||x==null||y==null||(!ratio&&!y))return '<span class="ld-variation">Comparação mensal indisponível</span>';const delta=ratio?(x-y)*100:(x-y)/y*100;const direction=key==='concentracao'?'neutral':delta>0?'bad':delta<0?'good':'neutral';return '<span class="ld-variation" data-direction="'+direction+'">'+(delta>0?'↑ +':delta<0?'↓ ':'= ')+decimal.format(delta)+(ratio?' p.p.':'%')+' · '+monthLabel(end)+' vs '+monthLabel(priorKey)+'</span>';};
      lastSparkSeries=periods(rows).slice(-12).map(s=>({mes:s.mes,...aggregate(rows.filter(r=>r.mes===s.mes))}));
      const cards=[
        ['acidentes','Acidentes registrados',n(a.acidentes),'Ocorrências distintas'],
        ['graves','Graves ou fatais',pct(a.percentualGrave),n(a.graves)+' ocorrências'],
        ['mortes','Mortes registradas',n(a.mortes),'Pessoas mortas na fonte'],
        ['feridos','Pessoas feridas',n(a.feridos),'Ferimentos leves ou graves'],
        ['noite','Em plena noite',pct(a.percentualNoite),n(a.plenaNoite)+' ocorrências'],
        ['concentracao','Nos 5 principais trechos',pct(a.concentracaoTop5),'Participação nos registros']
      ];
      el('[data-kpis]').innerHTML=cards.map(([key,label,value,detail])=>'<article class="ld-kpi" data-metric="'+key+'"><span class="ld-kpi-label">'+label+'</span><strong class="ld-kpi-value">'+value+'</strong><span class="ld-kpi-detail">'+detail+'</span>'+sparkline(key)+variation(key)+'</article>').join('');
      const choices=keys.filter(k=>state.filters[k].length).map(k=>(names[k]||'Trecho')+': '+(state.filters[k].length>2?state.filters[k].length+' selecionados':state.filters[k].map(v=>k==='mes'?monthLabel(v):k==='trechoChave'?base.find(r=>r.trechoChave===v)?.trecho||v:v).join(', ')));
      const dates=rows.map(r=>r.d).sort();
      el('[data-period]').textContent=dates.length?(dates[0].slice(0,7)===dates[dates.length-1].slice(0,7)?monthLabel(dates[0].slice(0,7)):monthLabel(dates[0].slice(0,7))+' — '+monthLabel(dates[dates.length-1].slice(0,7))):'Recorte sem registros';
      el('[data-selection]').textContent=choices.length?'Recorte interno: '+choices.join(' · '):'Explorando todo o recorte recebido do relatório';
      el('[data-empty]').hidden=rows.length>0;el('[data-analysis]').hidden=!rows.length;
      el('.ld-tooltip').hidden=true;
      if(!rows.length){
        el('[data-ticker]').textContent='Sem ocorrências na combinação atual.';
        for(const s of ['[data-monthly]','[data-readout]','[data-municipios]','[data-tipos]','[data-pistas]','[data-trechos]','[data-causas]','[data-rodovias]'])el(s).innerHTML='';
        el('[data-monthly-note]').textContent='';el('[data-pista-alert]').textContent='';
        el('[data-quality]').textContent='';el('[data-table-total]').textContent='';
      }else{
        const municipality=ranked(rows,'municipio').sort(byVolume);
        const typeRanks=ranked(rows,'tipo').sort(byVolume);
        const causeRanks=ranked(rows,'causa').sort(byVolume);
        const roadRanks=ranked(rows,'rodovia').sort((x,y)=>y.percentualGrave-x.percentualGrave||y.acidentes-x.acidentes||x.name.localeCompare(y.name));
        const roadAttention=[...roadRanks].sort(byConsequences)[0],municipalityAttention=[...municipality].sort(byConsequences)[0];
        lastRoads=roadRanks;lastExecutive={rodovia:roadAttention,municipio:municipalityAttention,causa:causeRanks[0]};
        el('[data-ticker]').innerHTML='<div class="ld-ticker-track">'+typeRanks.slice(0,4).map((t,i)=>'<span>'+String(i+1).padStart(2,'0')+' · '+esc(t.name)+' — '+n(t.acidentes)+' ocorrências</span>').join('')+'</div>';
        const priority=[...a.trechos].sort((x,y)=>y.graves-x.graves||y.acidentes-x.acidentes||x.k.localeCompare(y.k))[0];
        const priorityShare=a.graves?priority.graves/a.graves:priority.acidentes/a.acidentes;
        const priorityLabel=a.graves?'dos graves/fatais estão neste trecho':'dos registros estão neste trecho';
        const target=rows.filter(r=>r.trechoChave===priority.k),context=filtered('fase').filter(r=>r.trechoChave===priority.k),night=aggregate(context.filter(r=>r.fase==='Plena Noite')),day=aggregate(context.filter(r=>r.fase==='Pleno dia'));
        const cause=ranked(target,'causa').sort(byVolume)[0],type=ranked(target,'tipo').sort(byConsequences)[0];
        const comparison=night.acidentes&&day.acidentes?'No mesmo trecho e período, plena noite: '+n(night.graves)+'/'+n(night.acidentes)+' graves/fatais ('+pct(night.percentualGrave)+'); pleno dia: '+n(day.graves)+'/'+n(day.acidentes)+' ('+pct(day.percentualGrave)+'). Diferença: '+decimal.format((night.percentualGrave-day.percentualGrave)*100)+' p.p.':'Não há ocorrências suficientes nas duas fases para comparar noite e pleno dia neste recorte.';
        const focus=night.acidentes&&day.acidentes?(night.percentualGrave>day.percentualGrave?' Observar especialmente as condições noturnas.':night.percentualGrave<day.percentualGrave?' A proporção diurna é maior neste recorte.':' As proporções são iguais neste recorte.') :'';
        const action=/pedestre/i.test(type.name)?'Vistoriar travessias, acessos de pedestres e visibilidade.':/animal/i.test(type.name)?'Vistoriar pontos de entrada e presença de animais; revisar os registros com as equipes locais.':/traseira/i.test(type.name)?'Vistoriar aproximações, filas, sinalização e condições de visibilidade; avaliar atuação sobre distância de segurança.':/transversal|lateral/i.test(type.name)?'Vistoriar acessos, cruzamentos, conflitos de circulação e visibilidade.':'Vistoriar o local e revisar a dinâmica dos acidentes registrados antes de definir a intervenção.';
        const pavement=context.filter(r=>/buraco|defeito.*via|pavimento/i.test(r.causa)).length;
        el('[data-readout]').innerHTML='<p class="ld-insight-number">'+pct(priorityShare)+'</p><p class="ld-insight-title">'+priorityLabel+'</p><p class="ld-insight-copy"><strong>'+esc(priority.rotulo)+'</strong>: '+n(priority.acidentes)+' ocorrências, '+n(priority.graves)+' graves/fatais e '+n(priority.mortes)+' mortes no recorte.</p><div class="ld-decision"><strong>Comparação que orienta a vistoria</strong><p>'+comparison+'</p><small>Comparação mantém os demais filtros e retira apenas o filtro de fase do dia. Proporção entre acidentes registrados; não é risco por veículo.</small></div><div class="ld-decision"><strong>O que os registros apontam</strong><p>Tipo com mais graves/fatais no trecho: '+esc(type.name)+' ('+n(type.graves)+' em '+n(type.acidentes)+' ocorrências). Causa mais registrada: '+esc(cause.name)+' ('+n(cause.acidentes)+').</p></div><div class="ld-action"><strong>Ação a avaliar</strong>'+action+focus+' '+(pavement?n(pavement)+' registros mencionam defeito de via/pavimento; confirmar em vistoria.':'Não há registro de causa de pavimento identificado neste contexto; não atribuir os acidentes a buracos.')+'</div><p class="ld-small-note">A causa registrada é uma pista de investigação, não prova causal. Conferir localização exata, fluxo, condições atuais e '+n(target.filter(r=>r.q).length)+' registros com alertas antes da decisão.</p><button type="button" class="ld-clear" data-investigate="'+esc(priority.k)+'">Investigar este trecho</button>';

        function ranks(selector,list,key,metric='acidentes'){const maximum=metric==='percentualGrave'?1:list[0]?.acidentes||1;el(selector).innerHTML=list.slice(0,5).map(r=>'<button type="button" class="ld-rank" data-filter-kind="'+key+'" data-filter-value="'+esc(r.name)+'" data-hc-suppress="filter" data-tip="'+esc(r.name+'\n'+n(r.acidentes)+' ocorrências · '+pct(r.acidentes/a.acidentes)+' do recorte\n'+n(r.graves)+' graves/fatais · '+pct(r.percentualGrave)+'\n'+n(r.feridos)+' feridos · '+n(r.mortes)+' mortes')+'"><span class="ld-rank-label"><span class="ld-rank-name">'+esc(r.name)+'</span><span class="ld-rank-value">'+(metric==='percentualGrave'?pct(r.percentualGrave):n(r.acidentes))+'</span></span><span class="ld-track"><i style="width:'+100*r[metric]/maximum+'%"></i></span>'+(metric==='percentualGrave'?'<span class="ld-rank-context">'+n(r.graves)+' graves/fatais em '+n(r.acidentes)+' ocorrências</span>':'')+'</button>').join('');}
        ranks('[data-municipios]',municipality,'municipio');ranks('[data-tipos]',typeRanks,'tipo');
        ranks('[data-causas]',causeRanks,'causa');ranks('[data-rodovias]',roadRanks,'rodovia','percentualGrave');
        const pistes=ranked(rows,'pista').sort(byVolume);lastPistas=pistes;
        el('[data-pista-alert]').textContent=n(pistes.filter(p=>p.mortes>0).length)+' de '+n(pistes.length)+' tipos de pista com mortes registradas neste recorte.';
        el('[data-pistas]').innerHTML=pistes.map(p=>{const status=p.mortes>0?'fatal':p.feridosGraves>0?'grave':'sem-graves';const label=p.mortes>0?'Há mortes registradas':p.feridosGraves>0?'Há feridos graves':'Sem graves/fatais registrados';return '<article class="ld-pista-card" data-outcome="'+status+'"><div class="ld-pista-head"><h3>'+esc(p.name)+'</h3><strong>'+pct(p.percentualGrave)+'</strong></div><span class="ld-outcome-tag">'+(status==='fatal'?'! ':status==='grave'?'△ ':'• ')+label+'</span><dl class="ld-pista-numbers"><div><dt>Ocorrências</dt><dd>'+n(p.acidentes)+'</dd></div><div><dt>Graves/fatais</dt><dd>'+n(p.graves)+'</dd></div><div><dt>Feridos</dt><dd>'+n(p.feridos)+'</dd></div><div><dt>Mortes</dt><dd>'+n(p.mortes)+'</dd></div></dl></article>';}).join('');
        renderTable();
        el('[data-table-total]').textContent=n(a.trechos.length)+' trechos no recorte';
        el('[data-quality]').textContent=n(a.comAlertas)+' registros com inconsistências na fonte; valores preservados.';
        drawMonthly();
      }
      el('[data-status]').textContent=rows.length?'Dados carregados':'Recorte sem registros';
      const track=el('.ld-ticker-track');if(track)track.style.setProperty('--ld-ticker-shift',Math.min(0,el('[data-ticker]').clientWidth-track.scrollWidth)+'px');
      root.dataset.ready='true';
    }
    const stamp=data.meta.atualizadoEmUTC?new Date(data.meta.atualizadoEmUTC):null;
    el('[data-updated]').textContent=stamp&&!Number.isNaN(stamp.valueOf())?'Carga do modelo: '+new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short',timeStyle:'short'}).format(stamp)+' BRT':'Data de carga não informada';
    options();render();
    root.addEventListener('input',e=>{if(e.target.matches('[data-filter-search]')){query=e.target.value;drawChoices();}});
    root.addEventListener('change',e=>{const c=e.target.closest('[data-choice]');if(!c)return;e.stopPropagation();let k=c.dataset.choice,vs=[c.value];if(c.dataset.group){if(k==='mes')vs=[...new Set((data.seriesMensais||[]).map(r=>r.mes))].filter(v=>v.startsWith(c.value));else{k='trechoChave';vs=[...new Set(base.filter(r=>r.rodovia===c.value).map(r=>r.trechoChave))];}}if(k==='trechoChave'&&state.filters.rodovia.length){state.filters.trechoChave=[...new Set([...state.filters.trechoChave,...base.filter(r=>state.filters.rodovia.includes(r.rodovia)).map(r=>r.trechoChave)])];state.filters.rodovia=[];}setFilter(k,c.checked?[...state.filters[k],...vs]:state.filters[k].filter(v=>!vs.includes(v)));drawChoices();});
    root.addEventListener('click',e=>{const p=e.target.closest('[data-picker]');if(p){e.stopPropagation();openPopup(p);}if(e.target.closest('[data-popup-close]'))closePopup();if(e.target.closest('[data-filter-reset]')){const k=opened;setFilter(k,[]);if(k==='rodovia')setFilter('trechoChave',[]);drawChoices();}const t=e.target.closest('[data-investigate]');if(t){e.stopPropagation();setFilter('trechoChave',[t.dataset.investigate]);}});
    document.addEventListener('click',e=>{if(!root.contains(e.target)||!e.target.closest('[data-popup],[data-picker]'))closePopup();});
    root.addEventListener('keydown',e=>{if(e.key==='Escape'&&opened){const b=el('[data-picker="'+opened+'"]');closePopup();b?.focus();}});
    root.addEventListener('click',e=>{
      const clear=e.target.closest('[data-clear]'),theme=e.target.closest('[data-theme-toggle]'),rank=e.target.closest('[data-filter-kind]'),month=e.target.closest('[data-month]'),sort=e.target.closest('[data-sort]');
      if(clear){e.stopPropagation();keys.forEach(k=>state.filters[k]=[]);closePopup();options();save();render();}
      if(theme){e.stopPropagation();state.theme=state.theme==='dark'?'light':'dark';save();render();}
      if(rank){e.stopPropagation();toggleFilter(rank.dataset.filterKind,rank.dataset.filterValue,e.ctrlKey||e.metaKey);}
      if(month){e.stopPropagation();toggleFilter('mes',month.dataset.month,e.ctrlKey||e.metaKey);}
      if(sort){e.stopPropagation();const key=sort.dataset.sort;if(sortKeys.includes(key)){state.sort={key,dir:state.sort.key===key&&state.sort.dir==='asc'?'desc':'asc'};save();renderTable();}}
    });
    root.addEventListener('keydown',e=>{const month=e.target.closest('[data-month]');if(month&&(e.key==='Enter'||e.key===' ')){e.preventDefault();e.stopPropagation();toggleFilter('mes',month.dataset.month,e.ctrlKey||e.metaKey);}});
    const tip=el('.ld-tooltip');
    function showTip(target,x,y){if(!target?.dataset.tip){tip.hidden=true;return;}tip.textContent=target.dataset.tip;tip.hidden=false;const rb=root.getBoundingClientRect(),tb=tip.getBoundingClientRect();const minX=Math.max(5,rb.left+5),maxX=Math.min(window.innerWidth-8,rb.right-5)-tb.width;const minY=Math.max(5,rb.top+5),maxY=Math.min(window.innerHeight-8,rb.bottom-5)-tb.height;tip.style.left=Math.max(minX,Math.min(x+12,maxX))+'px';tip.style.top=Math.max(minY,Math.min(y-tb.height-12,maxY))+'px';}
    root.addEventListener('keydown',()=>tip.hidden=true);
    root.addEventListener('pointermove',e=>showTip(e.target.closest('[data-tip]'),e.clientX,e.clientY));
    root.addEventListener('pointerleave',()=>tip.hidden=true);
    root.addEventListener('focusin',e=>{const t=e.target.closest('[data-tip]');if(t){const b=t.getBoundingClientRect();showTip(t,b.left,b.bottom);}});
    root.addEventListener('focusout',()=>tip.hidden=true);
    if(window.__ldPRFObserver)window.__ldPRFObserver.disconnect();
    if(typeof ResizeObserver!=='undefined'){let width=0;window.__ldPRFObserver=new ResizeObserver(entries=>{const w=entries[0]?.contentRect.width;if(w!==width){width=w;drawMonthly();const t=el('.ld-ticker-track');if(t)t.style.setProperty('--ld-ticker-shift',Math.min(0,el('[data-ticker]').clientWidth-t.scrollWidth)+'px');}});window.__ldPRFObserver.observe(el('[data-monthly]'));}
    root.__ldApp={snapshot:()=>({stats:{...lastStats,trechos:lastStats?.trechos?.slice(0,10)},series:lastSeries,median:lastMedian,executive:lastExecutive,roads:lastRoads,pistas:lastPistas,sparkSeries:lastSparkSeries.map(s=>({mes:s.mes,acidentes:s.acidentes,percentualGrave:s.percentualGrave,mortes:s.mortes,feridos:s.feridos,percentualNoite:s.percentualNoite,concentracaoTop5:s.concentracaoTop5})),sort:{...state.sort},filters:{...state.filters},theme:state.theme,rows:lastRows.map(r=>r.id)}),setFilter,baseCount:base.length};
  }catch(error){
    const style=root.querySelector('style')?.outerHTML||'';
    root.dataset.ready='error';root.innerHTML=style+'<section class="ld-empty"><h2>Dados indisponíveis</h2><p>Não foi possível carregar este recorte. Verifique a fonte do painel no relatório.</p></section>';
    console.error('Dashboard PRF:',error);
  }
})();
