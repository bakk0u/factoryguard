const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
let server;
(async()=>{
 if(!process.argv[2]){server=spawn(process.env.PYTHON||'python',['-m','http.server','8781','--directory','reports/local'],{stdio:'ignore'});}
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||chromium.executablePath(),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const url=process.argv[2]||'http://127.0.0.1:8781/reviewer-site/';
 for(let i=0;i<50;i++){try{if((await fetch(url)).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 await page.goto(url);await page.waitForSelector('body[data-reviewer-ready="true"]');
 await page.screenshot({path:'docs/images/reviewer-desktop.png',fullPage:true});
 assert.ok((await page.locator('[data-view="0"]').innerText()).includes('12.83%'));
 await page.locator('#exploreAction').click();assert.equal(await page.evaluate(()=>state.events.length),377);
 await page.locator('#historyPanel summary').click();
 await page.locator('tr[data-index]').first().focus();await page.keyboard.press('Enter');
 assert.equal(await page.evaluate(()=>focus),376);
 assert.equal(await page.locator('tr[data-index]').first().evaluate(el=>el===document.activeElement),true);
 await page.locator('#periodStop').fill('8');await page.locator('#note').fill('Snapshot-specific reviewer note');
 await page.locator('#reviewPeriod').click();await page.waitForFunction(()=>!busy);assert.ok((await page.locator('#periodSummary').innerText()).includes('8 bursts'));
 await page.locator('#saveNote').click();await page.waitForFunction(()=>!busy);
 assert.ok((await page.locator('#notes').innerText()).includes('Snapshot-specific'));
 const report=await page.evaluate(()=>investigationReport());
 assert.equal(report.source_manifest.snapshot_id,await page.evaluate(()=>snapshot));
 assert.equal(report.website_build_commit,report.source_manifest.website_build_commit);
 assert.equal(report.result_code_commit,null);assert.equal(report.result_generation_time,null);
 assert.equal(report.machine_generated_evidence.length,8);
 assert.deepEqual(report.model_settings,await page.evaluate(()=>meta.models.B01));
 assert.equal(report.reference_identifiers.sha256,await page.evaluate(()=>meta.reference_sha256??null));
 const download=page.waitForEvent('download');await page.locator('#report').click();await download;
 await page.evaluate(()=>localStorage.setItem(legacyKey(),JSON.stringify([{id:1,start:1,stop:1,text:'Legacy only'}])));
 await page.evaluate(()=>showNotes());assert.ok((await page.locator('#notes').innerText()).includes('Export legacy notes'));
 assert.equal(await page.evaluate(()=>notebook.some(n=>n.text==='Legacy only')),false);
 await page.evaluate(()=>localStorage.setItem(noteKey().replace(snapshot,'different-snapshot'),JSON.stringify([{text:'Other snapshot'}])));
 await page.reload();await page.waitForSelector('body[data-reviewer-ready="true"]');await page.locator('#exploreAction').click();
 assert.ok((await page.locator('#notes').innerText()).includes('Snapshot-specific'));
 assert.equal(await page.evaluate(()=>notebook.some(n=>n.text==='Other snapshot')),false);
 await page.locator('#reset').click();await page.waitForFunction(()=>!busy&&state.revealed===0);
 assert.ok((await page.locator('#notes').innerText()).includes('Snapshot-specific'));
 await page.locator('#showAll').click();await page.waitForFunction(()=>!busy&&state.revealed===377);
 for(const run of ['B02','B04','B01']){await page.selectOption('#run',run);await page.waitForFunction(r=>!busy&&state.run===r,run);}
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'docs/images/reviewer-mobile.png'});
 await page.evaluate(()=>{meta.reviewer_source_manifest=undefined;meta.models.B01=undefined;});
 const missing=await page.evaluate(()=>investigationReport());assert.equal(missing.source_manifest,null);assert.equal(missing.model_settings,null);
 // Storage failures must leave exploration and in-tab report notes usable.
 const blocked=await browser.newPage();await blocked.addInitScript(()=>{Storage.prototype.getItem=()=>{throw Error('Storage blocked')};Storage.prototype.setItem=()=>{throw Error('Storage blocked')};});
 await blocked.goto(url);await blocked.waitForSelector('#exploreAction');await blocked.locator('#exploreAction').click();
 await blocked.locator('#note').fill('Volatile note');await blocked.locator('#saveNote').click();await blocked.waitForFunction(()=>!busy);
 assert.ok((await blocked.locator('#notes').innerText()).includes('Volatile note'));
 assert.ok((await blocked.locator('#noteMode').innerText()).includes('tab only'));
 assert.equal(await blocked.evaluate(()=>investigationReport().user_notes[0].text),'Volatile note');
 assert.deepEqual(errors,[]);await browser.close();server?.kill();console.log('Reviewer views, keyboard, report provenance, isolated/legacy notes, blocked storage, resets, run switching and mobile passed');
})().catch(e=>{server?.kill();console.error(e);process.exit(1)});
