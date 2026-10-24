/* Optional browser acceptance check. Requires Playwright and Chromium; no data downloads. */
const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.FACTORYGUARD_URL||'http://127.0.0.1:8765';
 await page.goto(base);await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 await page.locator('#step').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='1 / 0');
 if(!await page.locator('#nextA').innerText()||await page.locator('#nextA').innerText()==='—')throw Error('Pending prediction missing');
 // Drive the exact same reset/step endpoints, then inject returned state into the UI renderer.
 // API never sends unrevealed rows. This avoids timing-dependent hundreds of button clicks.
 const progress=await page.evaluate(async()=>{
  stop();let response;
  for(let i=0;i<110;i++) response=await api('/api/step',{session});
  state=response;render();return {revealed:state.revealed,gaps:state.events.filter(e=>e.acquisition_gap).length,eligible:state.events.filter(e=>e.resolved?.status==='eligible').length};
 });
 if(progress.revealed!==111||progress.gaps<1)throw Error('Gap replay not retained');
 if(!await page.locator('#chartA path').count())throw Error('RMS SVG missing');
 await page.screenshot({path:'reports/local/forecast-v1/dashboard-B01.png',fullPage:true});
 await page.locator('#run').selectOption('B04');await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 await page.locator('#step').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='1 / 0');
 if(!(await page.locator('#role').innerText()).includes('unresolved'))throw Error('B04 warning missing');
 await page.locator('#play').click();await page.waitForFunction(()=>Number(document.querySelector('#counts').textContent.split('/')[0])>=3);await page.locator('#play').click();
 const before=await page.locator('#counts').innerText();await page.waitForTimeout(700);if(before!==await page.locator('#counts').innerText())throw Error('Pause failed');
 await page.locator('#reset').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='0 / 0');
 await page.setViewportSize({width:390,height:844});await page.locator('#step').click();await page.waitForFunction(()=>document.querySelector('#counts').textContent==='1 / 0');
 if(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth))throw Error('Mobile horizontal overflow');
 await page.screenshot({path:'reports/local/forecast-v1/dashboard-mobile.png',fullPage:true});
 if(errors.length)throw Error('Browser errors: '+errors.join('; '));
 fs.writeFileSync('reports/local/forecast-v1/browser-verification.json',JSON.stringify({passed:true,browser:await browser.version(),B01_replay:progress,checks:['step','pending forecast','gap history','SVG charts','B04 warning','play/pause','reset','mobile layout'],page_errors:errors},null,2)+'\n');
 await browser.close();console.log('Dashboard browser acceptance passed',progress);
})().catch(e=>{console.error(e);process.exit(1)});
