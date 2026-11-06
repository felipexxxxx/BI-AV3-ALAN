import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import cases from './casos_browser_prf.mjs';
const require=createRequire('C:/Users/felip/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const {chromium}=require('playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'output','prf');
const browser=await chromium.launch({headless:true,channel:'msedge'});
const context=await browser.newContext({viewport:{width:1440,height:1100},deviceScaleFactor:1});
const page=await context.newPage();
let errors=[],requests=[],checks=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
await page.goto(pathToFileURL(path.join(root,'dashboard','preview_prf.html')).href);
await page.waitForSelector('.ld-root[data-ready=true]');
const snap=()=>page.evaluate(()=>document.getElementById('ld-prf-root').__ldApp.snapshot());
const fields={Acidentes:'acidentes',Feridos:'feridos',Mortes:'mortes',Graves:'graves',PercentualGrave:'percentualGrave',PercentualNoite:'percentualNoite',ConcentracaoTop5:'concentracaoTop5',PessoasDivergentes:'pessoasDivergentes'};
function assert(ok,msg){checks.push({ok,msg});if(!ok)throw Error(msg);}
for(const test of cases){
  await page.locator('[data-clear]').click();
  for(const [k,v] of Object.entries(test.filters))await page.locator('[data-filter="'+k+'"]').selectOption(v);
  const s=await snap();
  for(const [k,v] of Object.entries(test.expected)){const a=s.stats[fields[k]];assert(v===null?a===null:Math.abs(a-v)<1e-10,test.name+' · '+k+': '+a+' / '+v);}
  const ui=await page.evaluate(()=>({ticker:document.querySelector('[data-ticker]').textContent,hidden:document.querySelector('[data-analysis]').hidden,empty:!document.querySelector('[data-empty]').hidden,card:document.querySelector('[data-metric=acidentes] .ld-kpi-value').textContent,table:document.querySelector('[data-trechos]').children.length,readout:document.querySelector('[data-readout]').textContent}));
  assert(ui.empty===(test.expected.Acidentes===0),test.name+' · estado vazio');
  if(test.expected.Acidentes){assert(s.series.reduce((sum,x)=>sum+x.acidentes,0)===s.stats.acidentes,test.name+' · serie soma o recorte');assert(ui.readout.length>30,test.name+' · leitura executiva presente');assert(ui.table===Math.min(10,s.stats.trechos.length),test.name+' · tabela atualizada');}
  else assert(ui.table===0&&ui.readout==='',test.name+' · sem componentes obsoletos');
}
await page.locator('[data-clear]').click();
assert((await snap()).stats.acidentes===5513,'Limpar retorna ao contexto externo geral');
await page.locator('.ld-bar[data-month="2025-01"]').click();
assert((await snap()).stats.acidentes===92,'Clique na barra mensal filtra todos os componentes');
await page.locator('[data-clear]').click();
await page.locator('.ld-bar[data-month="2025-01"]').focus();
await page.keyboard.press('Enter');
assert((await snap()).stats.acidentes===92,'Selecao do mes acessivel pelo teclado');
await page.locator('[data-clear]').click();
await page.locator('[data-municipios] .ld-rank').first().click();
assert(Boolean((await snap()).filters.municipio),'Clique no ranking aplica filtro e recalcula');
await page.locator('[data-clear]').click();
await page.locator('[data-theme-toggle]').click();
assert((await snap()).theme==='light','Alternancia para Light');
function contrastScript(){
  const r=document.getElementById('ld-prf-root'),s=getComputedStyle(r);
  const rgb=c=>{const el=document.createElement('span');el.style.color=c;r.append(el);const x=getComputedStyle(el).color.match(/[\d.]+/g).slice(0,3).map(Number);el.remove();return x;};
  const lum=arr=>arr.map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4);}).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0);
  const panel=lum(rgb(s.getPropertyValue('--ld-panel').trim()));
  return Object.fromEntries(['--ld-fg','--ld-muted','--ld-accent','--ld-amber'].map(t=>{const f=lum(rgb(s.getPropertyValue(t).trim()));return[t,(Math.max(panel,f)+.05)/(Math.min(panel,f)+.05)];}));
}
const lightContrast=await page.evaluate(contrastScript);
assert(Object.values(lightContrast).every(x=>x>=4.5),'Contraste Light minimo 4,5:1');
await page.screenshot({path:path.join(output,'dashboard_light.png'),fullPage:true});
await page.locator('[data-theme-toggle]').click();
assert((await snap()).theme==='dark','Alternancia para Dark');
const darkContrast=await page.evaluate(contrastScript);
assert(Object.values(darkContrast).every(x=>x>=4.5),'Contraste Dark minimo 4,5:1');
await page.screenshot({path:path.join(output,'dashboard_dark.png'),fullPage:true});
await page.locator('.ld-bar').first().hover();
assert(await page.locator('.ld-tooltip').isVisible(),'Tooltip responde ao ponteiro');
const sizes=[];
for(const width of [1440,1024,768,480,390,320]){
  await page.setViewportSize({width,height:1100});
  await page.waitForTimeout(80);
  const size=await page.evaluate(()=>({width:window.innerWidth,scroll:document.documentElement.scrollWidth,root:document.querySelector('.ld-root').scrollWidth,rootClient:document.querySelector('.ld-root').clientWidth}));
  sizes.push(size);assert(size.scroll<=width&&size.root<=size.rootClient,'Sem overflow horizontal em '+width+'px');
}
await page.locator('.ld-root').hover({position:{x:3,y:3}});
await page.screenshot({path:path.join(output,'dashboard_mobile.png'),fullPage:true});
await page.setViewportSize({width:1440,height:1100});
await page.locator('[data-filter=mes]').selectOption('2025-01');
await page.locator('[data-filter=municipio]').selectOption('FORTALEZA');
const external=await fs.readFile(path.join(root,'dashboard','preview_prf_externo.html'),'utf8');
async function replaceVisual(content){await page.evaluate(content=>{const parsed=new DOMParser().parseFromString(content,'text/html');const html=parsed.getElementById('ld-prf-root').outerHTML;document.getElementById('ld-prf-root').remove();const range=document.createRange();range.selectNodeContents(document.body);document.body.append(range.createContextualFragment(html));},content);await page.waitForSelector('.ld-root[data-ready=true]');}
await replaceVisual(external);
const kept=await snap();
assert(kept.filters.mes==='2025-01'&&kept.filters.municipio==='FORTALEZA','Escolhas persistem apos atualizacao externa e reindexacao dos dicionarios');
assert(kept.stats.acidentes===cases.find(c=>c.name==='Filtros combinados').expected.Acidentes,'Recorte combinado apos atualizacao externa reconcilia');
await page.locator('[data-clear]').click();
assert((await snap()).stats.acidentes===707,'Limpar preserva filtro externo 2025 + BR116');
await replaceVisual(await fs.readFile(path.join(root,'dashboard','preview_prf_vazio.html'),'utf8'));
assert((await snap()).stats.acidentes===0,'Payload externo vazio funciona');
assert(await page.locator('[data-empty]').isVisible(),'Estado vazio externo legivel');
const html=await fs.readFile(path.join(root,'dashboard','preview_prf.html'),'utf8');
await replaceVisual(html);
const invalid=html.replace(/(<script type="application\/json" class="ld-data">)[\s\S]*?(<\/script>)/,'$1{$2');
await page.evaluate(content=>{const parsed=new DOMParser().parseFromString(content,'text/html');const html=parsed.getElementById('ld-prf-root').outerHTML;document.getElementById('ld-prf-root').remove();const range=document.createRange();range.selectNodeContents(document.body);document.body.append(range.createContextualFragment(html));},invalid);
assert(await page.locator('.ld-root[data-ready=error]').isVisible(),'JSON invalido tratado sem carregamento infinito');
assert(errors.length===0,'Sem erros JavaScript nao tratados');
assert(requests.length===0,'Sem requisicoes a bibliotecas, fontes, imagens ou APIs remotas');
const report=['# Validacao do HTML Normal PRF','',checks.length+' verificacoes aprovadas.','',...checks.map(x=>'- '+(x.ok?'OK':'FALHA')+': '+x.msg),'','## Contraste Light',...Object.entries(lightContrast).map(([k,v])=>'- '+k+': '+v.toFixed(2)+':1'),'','## Contraste Dark',...Object.entries(darkContrast).map(([k,v])=>'- '+k+': '+v.toFixed(2)+':1'),'','## Responsividade',...sizes.map(x=>'- '+x.width+'px: largura documento '+x.scroll+', conteudo da raiz '+x.root+', largura da raiz '+x.rootClient),'','Validacao em Chromium com dados extraidos da medida nativa. Nao equivale a validacao no custom visual real do Power BI.'];
await fs.writeFile(path.join(output,'validacao_html.md'),report.join('\n'),'utf8');
console.log(JSON.stringify({checks:checks.length,errors,requests,lightContrast,darkContrast,sizes}));
await browser.close();
