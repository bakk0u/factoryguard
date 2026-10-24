"""Package the existing B01 replay as a standalone offline HTML demonstration."""
import argparse
import json
from pathlib import Path
import re

ADAPTER = r'''let offlineCursor=0;
async function api(route,body){
 if(route==='/api/reset'){
  if(body.run!=='B01')throw Error('This offline file contains B01 development replay only');
  offlineCursor=0;
 }else if(route==='/api/step'){
  offlineCursor=Math.min(offlineCursor+1,offlineEvents.length);
 }else throw Error('Unsupported offline operation');
 const events=offlineEvents.slice(0,offlineCursor);
 return {run:'B01',session:'offline-B01',revealed:offlineCursor,
         exhausted:offlineCursor===offlineEvents.length,events,
         pending:events.length?events[events.length-1].issued:null};
}'''


def build_html(events, template):
    if not events or any(e.get('observation',{}).get('provenance__experiment') != 'B01' for e in events):
        raise ValueError('Offline export accepts an existing B01 development replay only')
    pattern = r'async function api\(route,body\)\{[^\n]*\}'
    if len(re.findall(pattern,template)) != 1:
        raise ValueError('Dashboard API hook changed; review the offline adapter')
    data=json.dumps(events,separators=(',',':'),allow_nan=False).replace('<',r'\u003c')
    offline='const offlineEvents='+data+';\n'+ADAPTER
    result=re.sub(pattern,lambda match: offline,template,count=1)
    result=re.sub(r'<option value="B0[24]">[^<]*</option>','',result)
    result=result.replace('FACTORYGUARD / LOCAL PROTOTYPE','FACTORYGUARD / OFFLINE B01 REPLAY')
    result=result.replace('<main>','<main><div class="banner">Standalone B01 development replay. No server or network connection required. This file contains the complete precomputed replay; controls reveal it sequentially. Forecasts are unchanged saved outputs, with no fitting or new evaluation.</div>',1)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='reports/local/forecast-v1/dashboard-B01-offline.html')
    args=parser.parse_args()
    # Reuse verified derived outputs only. Do not inspect raw data or any B03 path.
    events=[json.loads(line) for line in Path('reports/local/forecast-v1/replay-B01/events.jsonl').read_text().splitlines()]
    template=Path('src/factoryguard/monitoring/dashboard.html').read_text()
    html=build_html(events,template)
    output=Path(args.output).resolve()
    source_storage=Path('/workspace/datasets/paderborn-10868257').resolve()
    if output==source_storage or source_storage in output.parents:
        raise ValueError('Keep exports outside source dataset storage')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream: stream.write(html)
    print(f'Saved {output} ({output.stat().st_size:,} bytes); {len(events)} precomputed B01 observations')


if __name__=='__main__': main()
