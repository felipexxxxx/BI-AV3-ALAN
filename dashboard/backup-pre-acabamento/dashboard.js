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
    const keys=['mes','municipio','tipo','rodovia','fase','causa','pista'];
    const previous=window.__ldPRFState||{};
    const sortKeys=['trecho','acidentes','graves','percentualGrave','feridos','mortes'];
    const state={theme:previous.theme==='light'?'light':'dark',filters:Object.fromEntries(keys.map(k=>[k,previous.filters?.[k]||''])),sort:sortKeys.includes(previous.sort?.key)?{key:previous.sort.key,dir:previous.sort.dir==='asc'?'asc':'desc'}:{key:'acidentes',dir:'desc'}};
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
    const filtered=()=>base.filter(r=>keys.every(k=>!state.filters[k]||r[k]===state.filters[k]));
    const options=()=>{for(const k of keys){const select=el('[data-filter="'+k+'"]');let values=[...new Set(base.map(r=>r[k]))].sort(k==='mes'?undefined:(a,b)=>a.localeCompare(b,'pt-BR'));const chosen=state.filters[k];if(chosen&&!values.includes(chosen))values.push(chosen);select.innerHTML='<option value="">'+(k==='mes'?'Todos os meses':k==='municipio'?'Todos os municípios':k==='tipo'?'Todos os tipos':k==='rodovia'?'Todas as rodovias':k==='causa'?'Todas as causas':k==='pista'?'Todos os tipos de pista':'Todas as fases')+'</option>'+values.map(v=>'<option value="'+esc(v)+'">'+esc(k==='mes'?monthLabel(v):v)+'</option>').join('');select.value=chosen;}};
    const setFilter=(k,v)=>{state.filters[k]=v;options();save();render();};
    const periods=(rows)=>{
      const observed=groups(rows,'mes');
      const months=(data.seriesMensais||[]).map(x=>x.mes).filter(m=>!state.filters.mes||m===state.filters.mes);
      return months.map(m=>{const a=basic(observed.get(m)||[]);return {mes:m,...a,percentualGrave:a.acidentes?a.graves/a.acidentes:null};});
    };
    let lastRows=[],lastStats=null,lastSeries=[],lastMedian=null,lastExecutive=null,lastRoads=[],lastPistas=[];
    function renderTable(){
      const selection=lastStats?.trechos.slice(0,10)||[];
      const compare=new Intl.Collator('pt-BR',{numeric:true,sensitivity:'base'});
      const value=t=>state.sort.key==='trecho'?t.rotulo:state.sort.key==='percentualGrave'?t.graves/t.acidentes:t[state.sort.key];
      const sorted=[...selection].sort((a,b)=>{const av=value(a),bv=value(b),order=typeof av==='string'?compare.compare(av,bv):av-bv;return (state.sort.dir==='asc'?order:-order)||compare.compare(a.k,b.k);});
      el('[data-trechos]').innerHTML=sorted.map(t=>'<tr data-row-key="'+esc(t.k)+'"><td data-value="'+esc(t.rotulo)+'"><span class="ld-trecho-name">'+esc(t.rodovia)+' · km '+n(t.inicio)+'–'+n(t.inicio+10)+'</span><span class="ld-trecho-sub">Ceará · intervalo de 10 km</span></td><td class="ld-num" data-label="Acidentes" data-value="'+t.acidentes+'">'+n(t.acidentes)+'</td><td class="ld-num" data-label="Graves/fatais" data-value="'+t.graves+'">'+n(t.graves)+'</td><td class="ld-num ld-severity" data-label="% graves/fatais" data-value="'+t.graves/t.acidentes+'">'+pct(t.graves/t.acidentes)+'</td><td class="ld-num" data-label="Feridos" data-value="'+t.feridos+'">'+n(t.feridos)+'</td><td class="ld-num" data-label="Mortes" data-value="'+t.mortes+'">'+n(t.mortes)+'</td></tr>').join('');
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
        bars+='<rect class="ld-bar" x="'+(xx-bw/2)+'" y="'+yy+'" width="'+bw+'" height="'+Math.max(0,top+ph-yy)+'" data-month="'+s.mes+'" data-hc-suppress="filter" data-tip="'+esc(tip)+'" role="button" tabindex="0" aria-label="'+esc(tip+' · Selecionar este mês')+'"/>';
        if(s.percentualGrave!=null){path+=(active?'L':'M')+xx+','+yp(s.percentualGrave)+' ';active=true;points+='<circle class="ld-line-point" cx="'+xx+'" cy="'+yp(s.percentualGrave)+'" r="'+(series.length>24?1.7:3)+'" data-month="'+s.mes+'" data-hc-suppress="filter" data-tip="'+esc(tip)+'" role="button" tabindex="0" aria-label="'+esc(tip+' · Selecionar este mês')+'"/>';}else active=false;
        if(i%tickEvery===0||series.length===1){const lab=new Date(s.mes+'-02T12:00:00').toLocaleDateString('pt-BR',{month:'short',year:'2-digit'}).replace('.','');labels+='<text x="'+xx+'" y="'+(h-8)+'" text-anchor="middle">'+esc(lab)+'</text>';}
      });
      const medianLine=lastMedian==null?'':'<line class="ld-median-line" x1="'+left+'" x2="'+(w-right)+'" y1="'+yp(lastMedian)+'" y2="'+yp(lastMedian)+'" aria-label="Mediana mensal '+pct(lastMedian)+'"/>';
      host.innerHTML='<svg class="ld-monthly" viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Ocorrências mensais, percentual grave/fatal e mediana mensal. Eixos nomeados de quantidade e percentual.">'+grid+bars+medianLine+'<path class="ld-curve" d="'+path+'"/>'+points+labels+'</svg>';
      const months=series.filter(s=>s.percentualGrave!=null).length;
      el('[data-monthly-note]').textContent='Mediana mensal: '+pct(lastMedian)+' · média ponderada do recorte: '+pct(lastStats.percentualGrave)+(months===1?' · Um único mês com ocorrências; sem comparação temporal.':' · '+n(months)+' meses com ocorrências.');
    }
    function render(){
      const rows=filtered(),a=aggregate(rows);lastRows=rows;lastStats=a;lastSeries=periods(rows);lastMedian=median(lastSeries.map(s=>s.percentualGrave));lastExecutive=null;lastRoads=[];lastPistas=[];
      root.dataset.theme=state.theme;
      el('[data-theme-toggle]').textContent=state.theme==='dark'?'Modo claro ↗':'Modo escuro ↗';
      el('[data-theme-toggle]').setAttribute('aria-pressed',String(state.theme==='light'));
      const cards=[
        ['acidentes','Acidentes registrados',n(a.acidentes),'Ocorrências distintas'],
        ['graves','Graves ou fatais',pct(a.percentualGrave),n(a.graves)+' ocorrências'],
        ['mortes','Mortes registradas',n(a.mortes),'Pessoas mortas na fonte'],
        ['feridos','Pessoas feridas',n(a.feridos),'Ferimentos leves ou graves'],
        ['noite','Em plena noite',pct(a.percentualNoite),n(a.plenaNoite)+' ocorrências'],
        ['concentracao','Nos 5 principais trechos',pct(a.concentracaoTop5),'Participação nos registros']
      ];
      el('[data-kpis]').innerHTML=cards.map(([key,label,value,detail])=>'<article class="ld-kpi" data-metric="'+key+'"><span class="ld-kpi-label">'+label+'</span><strong class="ld-kpi-value">'+value+'</strong><span class="ld-kpi-detail">'+detail+'</span></article>').join('');
      const choices=keys.filter(k=>state.filters[k]).map(k=>k==='mes'?monthLabel(state.filters[k]):state.filters[k]);
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
        el('[data-ticker]').innerHTML='<span>'+n(rows.length)+' registros no recorte</span><span>'+esc(municipality[0].name)+': '+n(municipality[0].acidentes)+' ocorrências</span><span>'+n(a.trechos.length)+' trechos com registros</span>';
        const priority=[...a.trechos].sort((x,y)=>y.graves-x.graves||y.acidentes-x.acidentes||x.k.localeCompare(y.k))[0];
        const priorityShare=a.graves?priority.graves/a.graves:priority.acidentes/a.acidentes;
        const priorityLabel=a.graves?'dos graves/fatais estão neste trecho':'dos registros estão neste trecho';
        el('[data-readout]').innerHTML='<p class="ld-insight-number">'+pct(priorityShare)+'</p><p class="ld-insight-title">'+priorityLabel+'</p><p class="ld-insight-copy">'+esc(priority.rotulo)+' reúne '+n(priority.graves)+' ocorrências graves ou fatais entre '+n(priority.acidentes)+' registros.</p><ul class="ld-executive-list"><li><strong>'+esc(roadAttention.name)+'</strong> requer atenção pela concentração: '+n(roadAttention.graves)+' graves/fatais em '+n(roadAttention.acidentes)+' ocorrências.</li><li><strong>'+esc(municipalityAttention.name)+'</strong> concentra '+n(municipalityAttention.graves)+' graves/fatais; proporção de '+pct(municipalityAttention.percentualGrave)+'.</li><li><strong>Causa mais registrada:</strong> '+esc(causeRanks[0].name)+' ('+n(causeRanks[0].acidentes)+' ocorrências).</li><li><strong>Qualidade da base:</strong> '+n(a.comAlertas)+' ocorrências com alertas; '+n(a.pessoasDivergentes)+' com contagens de pessoas divergentes.</li></ul><div class="ld-action"><strong>Ação a avaliar</strong>Priorizar vistoria no trecho em destaque e investigar os registros. Frequência, causas registradas e gravidade não comprovam causa nem risco por veículo.</div>';
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
      root.dataset.ready='true';
    }
    const stamp=data.meta.atualizadoEmUTC?new Date(data.meta.atualizadoEmUTC):null;
    el('[data-updated]').textContent=stamp&&!Number.isNaN(stamp.valueOf())?'Carga do modelo: '+new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short',timeStyle:'short'}).format(stamp)+' BRT':'Data de carga não informada';
    options();render();
    root.addEventListener('change',e=>{const select=e.target.closest('[data-filter]');if(select){e.stopPropagation();setFilter(select.dataset.filter,select.value);}});
    root.addEventListener('click',e=>{
      const clear=e.target.closest('[data-clear]'),theme=e.target.closest('[data-theme-toggle]'),rank=e.target.closest('[data-filter-kind]'),month=e.target.closest('[data-month]'),sort=e.target.closest('[data-sort]');
      if(clear){e.stopPropagation();keys.forEach(k=>state.filters[k]='');options();save();render();}
      if(theme){e.stopPropagation();state.theme=state.theme==='dark'?'light':'dark';save();render();}
      if(rank){e.stopPropagation();setFilter(rank.dataset.filterKind,rank.dataset.filterValue);}
      if(month){e.stopPropagation();setFilter('mes',month.dataset.month);}
      if(sort){e.stopPropagation();const key=sort.dataset.sort;if(sortKeys.includes(key)){state.sort={key,dir:state.sort.key===key&&state.sort.dir==='asc'?'desc':'asc'};save();renderTable();}}
    });
    root.addEventListener('keydown',e=>{const month=e.target.closest('[data-month]');if(month&&(e.key==='Enter'||e.key===' ')){e.preventDefault();e.stopPropagation();setFilter('mes',month.dataset.month);}});
    const tip=el('.ld-tooltip');
    function showTip(target,x,y){if(!target?.dataset.tip){tip.hidden=true;return;}tip.textContent=target.dataset.tip;tip.hidden=false;const box=tip.getBoundingClientRect();tip.style.left=Math.max(5,Math.min(x+12,window.innerWidth-box.width-8))+'px';tip.style.top=Math.max(5,Math.min(y+12,window.innerHeight-box.height-8))+'px';}
    root.addEventListener('pointermove',e=>showTip(e.target.closest('[data-tip]'),e.clientX,e.clientY));
    root.addEventListener('pointerleave',()=>tip.hidden=true);
    root.addEventListener('focusin',e=>{const t=e.target.closest('[data-tip]');if(t){const b=t.getBoundingClientRect();showTip(t,b.left,b.bottom);}});
    root.addEventListener('focusout',()=>tip.hidden=true);
    if(window.__ldPRFObserver)window.__ldPRFObserver.disconnect();
    if(typeof ResizeObserver!=='undefined'){let width=0;window.__ldPRFObserver=new ResizeObserver(entries=>{const w=entries[0]?.contentRect.width;if(w!==width){width=w;drawMonthly();}});window.__ldPRFObserver.observe(el('[data-monthly]'));}
    root.__ldApp={snapshot:()=>({stats:{...lastStats,trechos:lastStats?.trechos?.slice(0,10)},series:lastSeries,median:lastMedian,executive:lastExecutive,roads:lastRoads,pistas:lastPistas,sort:{...state.sort},filters:{...state.filters},theme:state.theme,rows:lastRows.map(r=>r.id)}),setFilter,baseCount:base.length};
  }catch(error){
    const style=root.querySelector('style')?.outerHTML||'';
    root.dataset.ready='error';root.innerHTML=style+'<section class="ld-empty"><h2>Dados indisponíveis</h2><p>Não foi possível carregar este recorte. Verifique a fonte do painel no relatório.</p></section>';
    console.error('Dashboard PRF:',error);
  }
})();
