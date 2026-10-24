"""Standalone selected-method replay from frozen development prediction ledgers."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re

from factoryguard.models.forecast import clean, guard_run


OFFLINE = '''let offlineCursor=0,offlineRun='B01';
async function api(route,body){
 if(route==='/api/reset'){
  if(!Object.hasOwn(offlineReplays,body.run))throw Error('Only B01/B02/B04 development replays are available');
  offlineRun=body.run;offlineCursor=0;
 }else if(route==='/api/step'){
  offlineCursor=Math.min(offlineCursor+1,offlineReplays[offlineRun].length);
 }else throw Error('Unsupported offline operation');
 const events=offlineReplays[offlineRun].slice(0,offlineCursor);
 return {run:offlineRun,session:'offline-selection',revealed:offlineCursor,
   exhausted:offlineCursor===offlineReplays[offlineRun].length,events,
   pending:events.length?events[events.length-1].issued:null};
}'''


def events_from_ledger(records, group):
    if len({r['run'] for r in records})>1:
        raise ValueError('Replay records must belong to one experiment')
    events=[]
    for i,r in enumerate(records):
        guard_run(r['run'])
        row=r['observation'];quality={k:v for k,v in row.items() if k.startswith('quality__')}
        warning_names=[k.removeprefix('quality__') for k,v in quality.items() if isinstance(v,bool) and v and k not in ('quality__documented_warmup_setpoints','quality__any_warning')]
        n=r['training_bin_count']
        issued={'source_id':r['source_id'],'source_time':row['provenance__source_time'],
                'target_id':None,'status':'pending','selected':r['forecasts'][group],
                'persistence':r['forecasts']['persistence'],'support_n':n,
                'support':'supported' if n>=20 else 'sparse' if n else 'unseen',
                'source_warmup':row['quality__documented_warmup_setpoints'],
                'source_warnings':warning_names,'source_quality':quality,
                'history_ready':r['history_ready'],'context_interpretation_unresolved':r['run']=='B04'}
        resolved=None
        if i:
            previous=records[i-1]
            expired=previous['common_exclusion']=='expired_gap'
            resolved={**events[-1]['issued'],'status':'expired' if expired else 'eligible',
                'target_id':r['source_id'],'target_time':row['provenance__source_time'],
                'observed':previous['observed_target'],'elapsed_csv_s':previous['target_interval_s'],
                'comparison_common':previous['common_pair'],'comparison_exclusion':previous['common_exclusion']}
        temperature={k:row[k] for k in ('context__T1_c','context__T2_c') if row.get(k) is not None and row[k]>=110}
        events.append({'observation':row,'issued':issued,'resolved':resolved,
                       'acquisition_gap':bool(resolved and resolved['status']=='expired'),
                       'temperature_reference_notices':temperature})
    return events


def build(result_dir):
    result_dir=Path(result_dir)
    decision=json.loads((result_dir/'selection.json').read_text());group=decision['selected_group']
    replays={};roles={};training={}
    for run,trained in [('B01','B02'),('B02','B01'),('B04','B02')]:
        path=result_dir/(f'{run}_outer_forecasts.jsonl' if run!='B04' else 'B04_from_B02_forecasts.jsonl')
        records=[json.loads(line) for line in path.read_text().splitlines()]
        if not records or any(r['run']!=run for r in records):raise ValueError('Unexpected replay run identity')
        replays[run]=events_from_ledger(records,group)
        chosen=json.loads((result_dir/f'{trained}_inner_choices.json').read_text())[group]
        training[run]=trained
        description=(f"Exponential smoothing: current-observation weight α={chosen['params']['alpha']}; tuned only on {trained}" if group=='smoothing' else f"{group}; settings {chosen['params']}; chosen inside {trained} only")
        roles[run]=(f'{run} · Development selection result, not unbiased final performance. '+description if run!='B04' else f'B04 · Post-selection stress only. {description}. Operating-context interpretation remains unresolved; all measurements are as recorded.')
    template=Path(__file__).with_name('dashboard.html').read_text()
    template=template.replace('ridge','selected').replace('Ridge forecast','Selected method').replace('Ridge purple','Selected method purple')
    template=template.replace('FACTORYGUARD / LOCAL PROTOTYPE','FACTORYGUARD / DEVELOPMENT SELECTION')
    template=template.replace('B01 · development validation','B01 · selection replay').replace('B02 · training replay (optimistic)','B02 · selection replay')
    template=template.replace('Observed bursts / eligible forecasts','Observed bursts / common scored pairs')
    template=template.replace('Current training-condition support','Tuning-run condition coverage')
    template=template.replace('Frozen forecast-v1 · B02-only fitted scaler and selected (α=10) · no imputation, clipping or refitting.',
        f'Selection-v2 · selected family: {group}. Direction-specific settings are shown above; the final combined-development configuration remains a proposal. No imputation or clipping.')
    template=template.replace("r&&r.status==='eligible'&&r.observed[j]", "r&&r.status==='eligible'&&r.comparison_common&&r.observed[j]")
    template=template.replace("eligible=resolved.filter(r=>r.status==='eligible')", "eligible=resolved.filter(r=>r.status==='eligible'&&r.comparison_common)")
    template=template.replace('B02 training sources in current bin:', '${trainingRuns[run]} common training sources in current bin:')
    # Replace the old fixed-run descriptions; there is no training-resubstitution curve here.
    template='\n'.join("$('role').className='banner'+(run==='B04'?' warning':'');$('role').textContent=selectionRoles[run];" if line.startswith("$('role').className=") else line for line in template.splitlines())
    payload=('const offlineReplays='+json.dumps(clean(replays),separators=(',',':'),allow_nan=False).replace('<',r'\u003c')+';\n'
             +'const selectionRoles='+json.dumps(roles)+';\nconst trainingRuns='+json.dumps(training)+';\n'+OFFLINE)
    pattern=r'async function api\(route,body\)\{[^\n]*\}'
    if len(re.findall(pattern,template))!=1:raise ValueError('Dashboard API hook changed')
    template=re.sub(pattern,lambda _:payload,template,count=1)
    template=template.replace('<main>','<main><div class="banner">Selected method: '+('exponential smoothing' if group=='smoothing' else group)+'. Standalone precomputed development replay; no server or network required. The full B01/B02/B04 predictions are embedded; controls reveal observations sequentially. Charts retain all available forecasts. Common-pair metrics exclude history initialization and gaps under the frozen selection protocol. B03 remains sealed.</div>',1)
    return template,replays


def export(result_dir,output):
    output=Path(output).resolve()
    raw=Path('/workspace/datasets/paderborn-10868257').resolve()
    if output==raw or raw in output.parents:raise ValueError('Export must be outside dataset source storage')
    html,_=build(result_dir)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as stream:stream.write(html)
    return output


def serve(path,port):
    path=Path(path).resolve()
    if not path.is_file():raise ValueError('Export the selected dashboard first')
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path=='/':
                body=path.read_bytes();kind='text/html; charset=utf-8';status=200
            elif self.path=='/health':
                body=b'{"status":"ok","protocol":"selection-v2","B03":"sealed","mode":"standalone-replay"}';kind='application/json';status=200
            else:body=b'Not found';kind='text/plain';status=404
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'Selected-method dashboard ready inside this machine: http://127.0.0.1:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    e=sub.add_parser('export');e.add_argument('--results',required=True);e.add_argument('--output',required=True)
    s=sub.add_parser('serve');s.add_argument('--html',required=True);s.add_argument('--port',type=int,default=8765)
    args=p.parse_args()
    if args.command=='export':print(export(args.results,args.output))
    else:serve(args.html,args.port)


if __name__=='__main__':main()
