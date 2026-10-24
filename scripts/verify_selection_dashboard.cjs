/* Existing Playwright + Chromium are optional development checks, not runtime dependencies. */
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const root=process.argv[2]||'reports/local/selection-v2';
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.setContent(fs.readFileSync(root+'/dashboard.html','utf8'));
 await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 await page.locator('#step').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='1 / 0');
 if(!(await page.locator('#role').innerText()).includes('0.2'))throw Error('B01 settings wrong');
 await page.evaluate(async()=>{for(let i=1;i<111;i++)state=await api('/api/step',{session});render()});
 await page.screenshot({path:root+'/dashboard-B01.png',fullPage:true});
 await page.evaluate(async()=>{for(let i=111;i<377;i++)state=await api('/api/step',{session});render()});
 if(await page.locator('#counts').innerText()!=='377 / 363')throw Error('Common coverage mismatch');
 await page.locator('#run').selectOption('B02');await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 if(!(await page.locator('#role').innerText()).includes('0.5'))throw Error('B02 settings wrong');
 await page.locator('#play').click();await page.waitForFunction(()=>Number(document.querySelector('#counts').textContent.split('/')[0])>=3);await page.locator('#play').click();
 await page.waitForTimeout(600);const n=await page.locator('#counts').innerText();await page.waitForTimeout(600);if(n!==await page.locator('#counts').innerText())throw Error('Pause failed');
 await page.locator('#run').selectOption('B04');await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 if(!(await page.locator('#role').innerText()).includes('unresolved'))throw Error('B04 caveat missing');
 await page.setViewportSize({width:390,height:844});await page.locator('#step').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='1 / 0');
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 await page.screenshot({path:root+'/dashboard-mobile.png',fullPage:true});
 if(errors.length||requests.length)throw Error(JSON.stringify({errors,requests}));
 const result={passed:true,method:'Exact HTML bytes via setContent; managed browser blocks file URLs',page_errors:errors,network_requests:requests,checks:['direction-specific selected settings','step','play/pause','reset across experiments','377 B01 observations / 363 common pairs','B04 caveat','mobile layout']};
 fs.writeFileSync(root+'/browser-verification.json',JSON.stringify(result,null,2)+'\n');
 await browser.close();console.log('Selected-method offline browser checks passed');
})().catch(e=>{console.error(e);process.exit(1)});
