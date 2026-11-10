// Real-browser UI checks. Requires an explicitly OFFLINE local server; generation is fixture/mocked only.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {pathToFileURL}=require('node:url');
const base=process.env.FACTORYGUARD_BROWSER_BASE||'http://127.0.0.1:8786/';
const output=process.env.FACTORYGUARD_SCREENSHOT_DIR||'reports/local/redesign';
let browser;
(async()=>{
 assert.ok(!process.env.OPENAI_API_KEY,'Remove provider credentials from browser test tooling.');
 assert.equal((await (await fetch(new URL('health',base))).json()).mode,'offline','Only an offline fixture service is allowed.');
 fs.mkdirSync(output,{recursive:true});
 const browserEnv=Object.fromEntries(Object.entries(process.env).filter(([key])=>key!=='OPENAI_API_KEY'));
 browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||chromium.executablePath(),headless:true,env:browserEnv});
 const errors=[],external=[],checks=[];
 const contrast=(a,b)=>{
   const light=c=>{const x=c.match(/[\d.]+/g).slice(0,3).map(n=>{const v=Number(n)/255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return .2126*x[0]+.7152*x[1]+.0722*x[2];};
   const x=light(a),y=light(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);
 };
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
 let posts=[];
 page.on('request',r=>{if(r.method()==='POST'&&new URL(r.url()).pathname==='/api/investigations')posts.push(r.postDataJSON());});
 await page.goto(base);await page.waitForSelector('body[data-experience-ready="true"]');
 assert.equal(await page.locator('[data-view="0"]').isVisible(),true);
 assert.match(await page.locator('[data-view="0"]').innerText(),/12.83%/);
 const startWords=(await page.locator('[data-view="0"]').innerText()).trim().split(/\s+/).length;
 assert.ok(startWords<=190,`Start view should be a short introduction: ${startWords} words`);
 assert.equal(await page.locator('#attentionRail').isVisible(),true);
 await page.screenshot({path:path.join(output,'start-desktop.png'),fullPage:true});
 const colors=await page.locator('#walkthroughAction').evaluate(el=>({text:getComputedStyle(el).color,background:getComputedStyle(el).backgroundColor}));
 assert.ok(contrast(colors.text,colors.background)>=4.5,'primary action text contrast');
 await page.locator('#walkthroughAction').focus();assert.equal(await page.locator('#walkthroughAction').evaluate(el=>getComputedStyle(el).outlineStyle),'solid');
 await page.keyboard.press('Enter');await page.waitForFunction(()=>!busy&&state.revealed===3);
 assert.equal(await page.evaluate(()=>run),'B01');assert.equal(await page.locator('#assistantChannel').inputValue(),'A');
 assert.match(await page.locator('#assistantScope').innerText(),/observations 1–3.*boundary 3/);
 assert.equal(posts.length,0);
 assert.equal(await page.evaluate(()=>[...document.querySelectorAll('[data-rail-index]')].every(b=>Number(b.dataset.railIndex)<state.revealed)),true);
 await page.locator('#railSearch').fill('nothing-matches-this');assert.match(await page.locator('#railNotices').innerText(),/No matching/);
 await page.locator('#railSearch').fill('');
 const rms=await page.evaluate(()=>state.events.map(e=>e.rms_v[0].toFixed(7)));
 for(const value of rms)assert.ok((await page.locator('#guideCopy').innerText()).includes(value+' V'));
 for(const stage of ['2','4','0']){await page.locator(`[data-guide-stage="${stage}"]`).click();assert.equal(await page.locator('[data-guide-step][aria-current="step"]').getAttribute('data-guide-step'),stage);}
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'guide-notice-desktop.png')});
 for(let i=0;i<5;i++){
   assert.equal(await page.locator('[data-guide-step][aria-current="step"]').getAttribute('data-guide-step'),String(i));
   if(i<4){await page.locator('#guideNext').focus();await page.keyboard.press('Enter');}
 }
 assert.match(await page.locator('#guideCopy').innerText(),/do not establish why/);
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'guide-desktop.png')});
 checks.push('Start default, keyboard focus/activation, five deterministic steps, B01/A 1–3/as_of=3, zero automatic submissions');
 const suggestions=page.locator('[data-assistant-suggestion]');
 for(let i=0;i<await suggestions.count();i++){const text=await suggestions.nth(i).innerText();await suggestions.nth(i).click();assert.equal(await page.locator('#assistantQuestion').inputValue(),text);}
 assert.equal(posts.length,0);
 const desktopColumns=await page.evaluate(()=>{const m=document.getElementById('measurementColumn').getBoundingClientRect(),a=document.getElementById('assistantColumn').getBoundingClientRect();return a.left>=m.right&&Math.abs(a.top-m.top)<2;});assert.ok(desktopColumns,'desktop measurements stay beside assistant');
 await page.locator('#assistantChannel').selectOption('C');
 assert.equal(await page.locator('#measurementColumn #chartC').isVisible(),true);
 assert.equal(await page.locator('#chartError .legend').innerText(),'C');
 await page.locator('#assistantChannel').selectOption('A');
 assert.equal(await page.locator('#measurementColumn #chartA').isVisible(),true);
 assert.equal(posts.length,0);
 await page.locator('#assistantQuestion').fill('Explain this period in plain English.');
 if(await page.locator('#guideExit').isVisible())await page.locator('#guideExit').click();
 await page.locator('#askAssistant').click();
 await page.waitForFunction(()=>document.getElementById('assistantActivity').textContent.startsWith('Complete'));
 assert.equal(posts.length,1);
 assert.deepEqual({...posts[0].selection,snapshot:undefined},{experiment:'B01',channel:'A',start:1,stop:3,as_of:3,mode:'replay',snapshot:undefined});
 assert.equal(posts[0].question,'Explain this period in plain English.');
 assert.equal(await page.locator('#assistantAnswer').getAttribute('data-answer-kind'),'fixture');
 assert.match(await page.locator('#assistantAnswer').innerText(),/Offline fixture response/);
 assert.match(await page.locator('#assistantAnswer').innerText(),/Uncertainty and limitations/);
 const result=JSON.parse(await page.locator('#assistantEvidence').textContent());
 assert.equal(result.model,'offline-deterministic-fixture');
 const records=[...result.context.facts,...result.context.passages];
 const citations=page.locator('[data-assistant-citation]');
 for(let i=0;i<await citations.count();i++){
   const id=await citations.nth(i).getAttribute('data-assistant-citation'),record=records.find(r=>r.id===id);assert.ok(record);
   await citations.nth(i).focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#citationPanel').isVisible(),true);
   assert.equal(await page.locator('#citationPanel').evaluate(el=>el.scrollTop),0);
   const titleBox=await page.locator('#citationTitle').boundingBox();assert.ok(titleBox.y>=0&&titleBox.y+titleBox.height<=page.viewportSize().height);
   const opened=JSON.parse(await page.locator('#assistantEvidence').textContent());assert.equal(opened.selected_evidence.id,id);
   assert.ok((await page.locator('#citationContent').innerText()).includes(record.source.path));
   assert.ok((await page.locator('#citationContent').innerText()).includes(record.source.sha256));
   await page.keyboard.press('Escape');assert.equal(await page.locator('#citationPanel').isVisible(),false);
   assert.equal(await citations.nth(i).evaluate(el=>el===document.activeElement),true);
 }
 await page.locator('[data-nav="3"]').click();
 await page.screenshot({path:path.join(output,'assistant-desktop.png')});
 await citations.first().click();await page.screenshot({path:path.join(output,'citation-desktop.png')});
 checks.push('Suggestions populate without POST; explicit fixture POST matches shown question/scope; citations resolve and open exact source/provenance; Escape restores focus');
 await page.locator('#closeCitation').click();
 await page.locator('[data-nav="1"]').click();await page.locator('#investigationQueue>summary').click();
 await page.locator('#queueFilter').selectOption('regime');assert.match(await page.locator('#queueItems').innerText(),/warm-up/i);
 await page.locator('#queueSearch').fill('nothing-matches-this');assert.match(await page.locator('#queueItems').innerText(),/No matching/);
 await page.locator('#queueSearch').fill('');await page.locator('#queueFilter').selectOption('all');
 await page.locator('[data-nav="2"]').click();assert.match(await page.locator('[data-view="2"]').innerText(),/not held-out/);
 await page.locator('[data-nav="4"]').click();assert.match(await page.locator('[data-view="4"]').innerText(),/remain incomplete/);
 assert.equal(await page.locator('[data-component]').count(),14);
 const expected={data:'Recorded experiments',forecasting:'Forecasting',snapshot:'Pinned evidence',dashboard:'Dashboard',orchestrator:'TypeScript orchestrator',mcp:'MCP connection',retrieval:'Python evidence retrieval',context:'RAG / context assembly',generation:'OpenAI generation',validation:'Citation validation',answer:'Answer + evidence',traces:'Local traces',hybrid:'Hybrid retrieval',hosting:'Restricted hosted demo'};
 for(const [id,title] of Object.entries(expected)){
   await page.locator(`[data-component="${id}"]`).focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#componentTitle').innerText(),title);
   assert.equal(await page.locator('#componentTitle').evaluate(el=>el===document.activeElement),true);
   assert.equal(await page.locator('.system-node[aria-pressed="true"]').count(),1);
   assert.ok((await page.locator('.component-example p').innerText()).length>15);
   if(id==='hosting')assert.match(await page.locator('.component-status').innerText(),/Future · not implemented/i);
   if(id==='hybrid')assert.match(await page.locator('.component-status').innerText(),/unevaluated/i);
   await page.locator('#architectureDetail summary').click();
   const link=await page.locator('#architectureDetail a').getAttribute('href');assert.ok(fs.existsSync(path.resolve(link.split('/blob/master/')[1])),`source exists for ${id}`);
   await page.locator('#backToDiagram').click();assert.equal(await page.locator(`[data-component="${id}"]`).evaluate(el=>el===document.activeElement),true);
 }
 assert.equal(posts.length,1,'diagram interactions never submit an investigation');
 await page.locator('[data-component="dashboard"]').click();await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:path.join(output,'engineering-desktop.png'),fullPage:true});
 await page.locator('[data-nav="2"]').click();await page.screenshot({path:path.join(output,'methods-desktop.png'),fullPage:true});
 checks.push('Layout 3 revealed-only Attention rail/filter, concise Start, desktop parallel columns; all 14 architecture components open correct explanations/examples/sources by keyboard, future and unverified states distinct, no diagram POST');
 for(const width of [1024,390]){
   await page.setViewportSize({width,height:844});
   for(const view of ['0','1','3','2','4']){
     await page.locator(`[data-nav="${view}"]`).click();
     assert.equal(await page.locator('nav [aria-pressed="true"]').count(),1);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow at ${width}/${view}`);
   }
 }
 await page.locator('[data-nav="0"]').click();await page.screenshot({path:path.join(output,'start-mobile.png'),fullPage:true});
 await page.locator('#walkthroughAction').click();await page.waitForFunction(()=>!busy&&state.revealed===3);
 await page.emulateMedia({reducedMotion:'reduce'});assert.equal(await page.locator('#guideCopy').evaluate(el=>getComputedStyle(el).animationName),'none');
 await page.screenshot({path:path.join(output,'guide-mobile.png')});
 const order=await page.evaluate(()=>{const m=document.getElementById('measurementColumn').getBoundingClientRect(),a=document.getElementById('assistantColumn').getBoundingClientRect(),n=document.getElementById('investigationNotebook').getBoundingClientRect();return a.top>=m.bottom&&n.top>=a.bottom;});assert.ok(order,'mobile assistant follows measurements before deeper notebook');
 await page.locator('[data-nav="3"]').click();await page.screenshot({path:path.join(output,'assistant-mobile.png')});
 await page.locator('[data-nav="4"]').click();await page.locator('[data-component="context"]').click();assert.match(await page.locator('#componentTitle').innerText(),/RAG/);await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,'engineering-mobile.png'),fullPage:true});
 checks.push('Queue filters, deeper methods/engineering, desktop/tablet/mobile no overflow, mobile measurement→assistant→notebook order, reduced motion');
 // Static export: usable guidance and suggestions; no backend or automatic submission.
 const staticPage=await browser.newPage();await staticPage.goto(pathToFileURL(path.resolve('reports/local/reviewer-site/index.html')).href);
 await staticPage.waitForSelector('body[data-experience-ready="true"]');await staticPage.locator('#walkthroughAction').click();
 await staticPage.waitForFunction(()=>!busy&&state.revealed===3);
 assert.equal(await staticPage.locator('#askAssistant').isDisabled(),true);
 await staticPage.locator('[data-assistant-suggestion]').first().click();assert.match(await staticPage.locator('#assistantMode').innerText(),/unavailable/);
 await staticPage.locator('[data-nav="4"]').click();await staticPage.locator('[data-component="generation"]').click();assert.equal(await staticPage.locator('#componentTitle').innerText(),'OpenAI generation');assert.match(await staticPage.locator('.component-status').innerText(),/opt-in/i);
 checks.push('Direct-file static walkthrough/suggestions work; new generation visibly unavailable');
 // Mock only the generation interface to test result/failure/cancellation states without providers.
 const makeMock=async({unavailable=false}={})=>{
   const p=await browser.newPage();p.on('pageerror',e=>errors.push(e.message));
   if(unavailable)await p.route('**/health',r=>r.abort());
   await p.addInitScript(()=>{window.EventSource=class{constructor(){window.__testStream=this;this.handlers={};}addEventListener(n,f){this.handlers[n]=f;}close(){this.closed=true;}};});
   await p.route('**/api/investigations',r=>r.fulfill({status:202,contentType:'application/json',body:JSON.stringify({request_id:'mock',events_url:'/mock-events'})}));
   await p.route('**/api/investigations/mock/cancel',r=>r.fulfill({status:200,contentType:'application/json',body:'{"status":"running"}'}));
   await p.goto(base);await p.waitForSelector('body[data-experience-ready="true"]');await p.locator('#walkthroughAction').click();await p.waitForFunction(()=>!busy&&state.revealed===3);return p;
 };
 const mock=await makeMock();await mock.locator('#askAssistant').click();assert.equal(await mock.locator('#askAssistant').isDisabled(),true);
 await mock.locator('#cancelAssistant').click();await mock.waitForFunction(()=>document.getElementById('assistantActivity').textContent.includes('Cancellation requested'));assert.match(await mock.locator('#assistantActivity').innerText(),/Cancellation requested/);
 await mock.locator('#askAssistant').click();
 await mock.waitForFunction(()=>window.__testStream&&!window.__testStream.closed&&window.__testStream.handlers.failure);
 await mock.evaluate(()=>window.__testStream.handlers.failure({data:JSON.stringify({stage:'generation',code:'mock_provider_failure'})}));
 assert.match(await mock.locator('#assistantActivity').innerText(),/Unable to complete/);assert.equal(await mock.locator('#askAssistant').isEnabled(),true);
 await mock.locator('#askAssistant').click();
 await mock.waitForFunction(()=>window.__testStream&&!window.__testStream.closed&&window.__testStream.handlers.result);
 const mockResult={...result,model:'mock-generated-model',answer:{...result.answer,summary:'Mocked generated-answer rendering test; no live model was called.'}};
 await mock.evaluate(r=>window.__testStream.handlers.result({data:JSON.stringify(r)}),mockResult);
 assert.equal(await mock.locator('#assistantAnswer').getAttribute('data-answer-kind'),'generated');assert.match(await mock.locator('#assistantAnswer').innerText(),/Newly generated answer/);
 const unavailable=await makeMock({unavailable:true});assert.equal(await unavailable.locator('#askAssistant').isDisabled(),true);assert.match(await unavailable.locator('#assistantMode').innerText(),/unavailable/);
 assert.equal(await unavailable.locator('#guidedReview').isVisible(),true);
 checks.push('Mock loading/cancel acknowledgement/error/generated-answer labels and unavailable backend; no real provider');
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(path.join(output,'browser-verification.json'),JSON.stringify({checks,start_visible_words:startWords,errors,external_requests:external,real_model_requests:0,fixture_investigations:1,screenshots:fs.readdirSync(output).filter(n=>n.endsWith('.png'))},null,2));
 await browser.close();console.log('Redesign browser checks passed: '+checks.join('; '));
})().catch(async e=>{await browser?.close();console.error(e);process.exitCode=1;});
