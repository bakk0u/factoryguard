const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const root=process.argv[2],base=process.argv[3]||'http://127.0.0.1:8766';
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));await page.goto(base);
 await page.waitForFunction(()=>typeof state!=='undefined'&&state);
 await page.locator('#reset').click();await page.waitForFunction(()=>!busy&&state.revealed===0);
 for(let i=0;i<8;i++){await page.locator('#step').click();await page.waitForFunction(()=>!busy);}
 await page.locator('#periodStop').fill('8');await page.locator('#note').fill('Engineering review: inspect operating context.');
 await page.locator('#saveNote').click();await page.waitForFunction(()=>!busy);
 if(!(await page.locator('#notes').innerText()).includes('Engineering review'))throw Error('Note not saved');
 const download=page.waitForEvent('download');await page.locator('#report').click();
 await (await download).saveAs(root+'/investigation-report.json');
 const report=JSON.parse(fs.readFileSync(root+'/investigation-report.json','utf8'));
 if(report.experiment!=='B01'||report.machine_generated_evidence.length!==8||!report.user_notes.length)throw Error('Report incorrect');
 await page.screenshot({path:root+'/investigation-desktop.png',fullPage:true});
 await page.reload();await page.waitForFunction(()=>typeof state!=='undefined'&&state);
 if(!(await page.locator('#notes').innerText()).includes('Engineering review'))throw Error('Reload lost notes');
 await page.locator('#reset').click();await page.waitForFunction(()=>!busy&&state.revealed===0);
 if(!(await page.locator('#notes').innerText()).includes('Engineering review'))throw Error('Reset lost notes');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:root+'/investigation-mobile.png',fullPage:true});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile overflow');
 if(errors.length)throw Error(errors.join(';'));
 await browser.close();console.log('Investigation browser workflow passed');
})().catch(e=>{console.error(e);process.exit(1)});
