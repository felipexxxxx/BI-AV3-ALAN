import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import cases from './casos_evolucao_prf.mjs';
const require=createRequire('C:/Users/felip/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.join(root,'output','prf');
const browser=await chromium.launch({headless:true,channel:'msedge'});
try{
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[],requests=[],checks=[];
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
const assert=(ok,msg)=>{checks.push({ok,msg});if(!ok)throw Error(msg);};
const snap=()=>page.evaluate(()=>document.querySelector('.ld-root').__ldApp.snapshot());
await page.goto(pathToFileURL(path.join(root,'dashboard','preview_prf.html')).href);
await page.waitForSelector('.ld-root[data-ready=true]');
const results=[];
for(const c of cases){
 await page.locator('[data-clear]').click();
 for(const [k,v] of Object.entries(c.filters))await page.locator('[data-filter="'+k+'"]').selectOption(v);
 const s=await snap();
 assert(s.stats.acidentes===c.acidentes,c.name+' · acidentes reconciliados');
 assert(s.stats.graves===c.graves&&s.stats.mortes===c.mortes,c.name+' · gravidade e mortes reconciliadas');
 assert(c.median==null?s.median==null:Math.abs(s.median-c.median)<1e-12,c.name+' · mediana igual ao DAX');
 assert(c.percentual==null?s.stats.percentualGrave==null:Math.abs(s.stats.percentualGrave-c.percentual)<1e-12,c.name+' · media ponderada igual ao DAX');
 if(c.acidentes){
  const readout=await page.locator('[data-readout]').innerText();
  assert(readout.includes(s.executive.rodovia.name)&&readout.includes(s.executive.municipio.name)&&readout.includes(s.executive.causa.name),c.name+' · leitura executiva atualizada');
  assert(await page.locator('.ld-median-line').count()===1,c.name+' · linha mediana presente');
  assert(s.roads.every((r,i)=>i===0||s.roads[i-1].percentualGrave>=r.percentualGrave),c.name+' · rodovias ordenadas por gravidade');
  const tags=await page.locator('.ld-pista-card').evaluateAll(nodes=>nodes.map(e=>({outcome:e.dataset.outcome,text:e.querySelector('.ld-outcome-tag').textContent})));
  assert(tags.every((t,i)=>s.pistas[i].mortes>0?t.outcome==='fatal'&&t.text.includes('mortes'):s.pistas[i].feridosGraves>0?t.outcome==='grave':t.outcome==='sem-graves'),c.name+' · estados descrevem consequencias reais');
 }else assert(await page.locator('[data-readout]').innerText()===''&&await page.locator('[data-causas] .ld-rank').count()===0,c.name+' · novos componentes sem valores obsoletos');
 results.push({contexto:c.name,acidentes:s.stats.acidentes,mediana:s.median,media:s.stats.percentualGrave});
}
await page.locator('[data-clear]').click();
const columns=['trecho','acidentes','graves','percentualGrave','feridos','mortes'];
const original=await page.locator('[data-trechos] tr').evaluateAll(rows=>rows.map(r=>r.dataset.rowKey).sort());
for(let i=0;i<columns.length;i++){
 const key=columns[i];
 for(let turn=0;turn<2;turn++){
  await page.locator('[data-sort="'+key+'"]').click();
  const s=await snap(),dir=s.sort.dir;
  const actual=await page.locator('[data-trechos] tr').evaluateAll((rows,i)=>rows.map(r=>r.children[i].dataset.value),i);
  const collator=new Intl.Collator('pt-BR',{numeric:true,sensitivity:'base'});
  const ordered=actual.every((v,j)=>!j||(i===0?(dir==='asc'?collator.compare(actual[j-1],v)<=0:collator.compare(actual[j-1],v)>=0):(dir==='asc'?Number(actual[j-1])<=Number(v)+1e-12:Number(actual[j-1])+1e-12>=Number(v))));
  assert(ordered,key+' · ordem '+dir+' confere com valores exibidos');
  assert(await page.locator('[data-sort-header="'+key+'"]').getAttribute('aria-sort')===(dir==='asc'?'ascending':'descending'),key+' · aria-sort '+dir);
  assert(await page.locator('th[aria-sort=ascending],th[aria-sort=descending]').count()===1,key+' · apenas uma coluna ativa');
  const now=await page.locator('[data-trechos] tr').evaluateAll(rows=>rows.map(r=>r.dataset.rowKey).sort());
  assert(JSON.stringify(now)===JSON.stringify(original),key+' · ordenacao preserva a selecao de dez trechos');
 }
}
await page.locator('[data-sort=mortes]').focus();
const before=(await snap()).sort.dir;
await page.keyboard.press('Enter');
assert((await snap()).sort.dir!==before,'Ordenacao funciona por Enter');
assert(await page.locator('[data-sort=mortes]').evaluate(e=>e===document.activeElement),'Foco preservado apos ordenar');
const sortState=(await snap()).sort;
await page.locator('[data-filter=municipio]').selectOption('FORTALEZA');
assert(JSON.stringify((await snap()).sort)===JSON.stringify(sortState),'Ordenacao preservada apos filtrar');
await page.locator('[data-clear]').click();
await page.locator('[data-causas] .ld-rank').first().click();
assert(Boolean((await snap()).filters.causa),'Ranking de causas aplica filtro combinado');
await page.locator('[data-clear]').click();
await page.locator('[data-rodovias] .ld-rank').first().click();
assert(Boolean((await snap()).filters.rodovia),'Ranking de rodovias aplica filtro');
await page.locator('[data-clear]').click();
for(const index of [0,30,59]){
 await page.locator('.ld-bar').nth(index).hover();
 const tip=page.locator('.ld-tooltip');assert(await tip.isVisible(),'Tooltip visivel no mes '+index);
 const text=await tip.innerText();assert(text.includes('Mediana mensal:')&&text.includes('média ponderada do recorte')&&text.includes('feridos')&&text.includes('mortes'),'Tooltip completo no mes '+index);
 const b=await tip.boundingBox();assert(b.x>=0&&b.y>=0&&b.x+b.width<=1440&&b.y+b.height<=1100,'Tooltip dentro da janela no mes '+index);
}
await page.locator('[data-filter=mes]').selectOption('2025-01');
assert((await page.locator('[data-monthly-note]').innerText()).includes('único mês'),'Cenario de um unico mes comunicado');
assert((await snap()).series.length===1&&await page.locator('.ld-line-point').count()===1,'Um mes preserva ponto e mediana');
await page.locator('[data-clear]').click();
const stateCounts=[];
for(const theme of ['dark','light']){
 if((await snap()).theme!==theme)await page.locator('[data-theme-toggle]').click();
 const contrasts=await page.locator('.ld-pista-card').evaluateAll(cards=>{
   const lum=c=>{const a=c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);});return a.reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0);};
   return cards.map(card=>{const a=lum(getComputedStyle(card).backgroundColor),b=lum(getComputedStyle(card.querySelector('.ld-outcome-tag')).color);return(Math.max(a,b)+.05)/(Math.min(a,b)+.05);});
 });
 assert(contrasts.every(c=>c>=4.5),'Contraste dos estados '+theme+' >= 4,5:1');stateCounts.push({theme,contrasts});
 await page.locator('.ld-root').hover({position:{x:2,y:2}});
 await page.screenshot({path:path.join(out,'evolucao_'+theme+'.png'),fullPage:true});
}
for(const width of [1440,1024,768,480,390,320]){
 await page.setViewportSize({width,height:1100});
 const overflow=await page.evaluate(()=>({doc:document.documentElement.scrollWidth,root:document.querySelector('.ld-root').scrollWidth,width:document.querySelector('.ld-root').clientWidth}));
 assert(overflow.doc<=width&&overflow.root<=overflow.width,'Sem overflow apos evolucao em '+width+'px');
 assert(await page.locator('[data-sort=mortes]').isVisible(),'Ordenacao disponivel em '+width+'px');
}
assert(errors.length===0,'Sem erros JavaScript');assert(requests.length===0,'Sem requisicoes remotas');
const report=['# Validacao da evolucao HTML PRF','',checks.length+' verificacoes aprovadas.','',...checks.map(c=>'- OK: '+c.msg),'','## Medianas reconciliadas com DAX',...results.map(r=>'- '+r.contexto+': '+r.acidentes+' ocorrencias; mediana '+r.mediana+'; media ponderada '+r.media),'','## Contraste dos estados descritivos',...stateCounts.map(s=>'- '+s.theme+': '+s.contrasts.map(c=>c.toFixed(2)+':1').join(', ')),'','Somente a camada HTML foi alterada. Validacao em Edge/Chromium; verificacao no custom visual real do Power BI continua pendente.'];
await fs.writeFile(path.join(out,'validacao_evolucao_html.md'),report.join('\n'),'utf8');
console.log(JSON.stringify({checks:checks.length,errors,requests,results,stateCounts}));
}finally{await browser.close();}
