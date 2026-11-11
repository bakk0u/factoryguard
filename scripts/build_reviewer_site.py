"""Build a server-free reviewer site from explicitly pinned derived results."""
import argparse
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
from factoryguard.release.application import html as dashboard

ROOT = Path(__file__).resolve().parents[1]

def build(output, alert_journal=None):
    if alert_journal and Path(alert_journal).resolve().is_relative_to(Path(output).resolve()):
        raise ValueError('Keep private alert databases outside browser assets')
    source = ROOT / 'site/source'
    manifest = json.loads((ROOT / 'site/source-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Source integrity failed: {name}')
    payload = json.loads((source / 'replay.json').read_text())
    manifest['website_build_commit'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,
        env={k:v for k,v in os.environ.items() if k!='OPENAI_API_KEY'}).strip()
    manifest['snapshot_id'] = manifest['files']['replay.json']
    payload['metadata']['reviewer_source_manifest'] = manifest
    with (source / 'development_metrics.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    with (source / 'stress_metrics.csv').open(newline='', encoding='utf-8') as stream:
        rows += list(csv.DictReader(stream))
    columns = ['training_run','evaluation_run','group','candidate','partition','coverage','channel','n','mae_v','rmse_v','mae_skill']
    cells = lambda row: ''.join('<td>'+html.escape(str(row[c]))+'</td>' for c in columns)
    evidence = '<details class="card" id="comparison"><summary>Full saved model-comparison results · all candidates</summary><p>Development selection results, not an independent final test. Negative skill means worse than persistence. Training and evaluation partitions and common-pair coverage are explicit. Historical direction-specific settings are preserved; final pooled alpha 0.5 is not substituted.</p><label>Filter results <input id="metricFilter" type="search" placeholder="e.g. smoothing or B04"></label><div class="scroll"><table><tr>'+''.join('<th>'+c+'</th>' for c in columns)+'</tr>'+''.join('<tr>'+cells(row)+'</tr>' for row in rows)+'</table></div></details>'
    page = dashboard(payload)
    page = page.replace('start().then(showNotes)', 'start()')
    page = page.replace('precomputed full replay embedded, no persistence or live connection.', 'precomputed results; browser-local notes; no live connection.')
    page = page.replace('let cursors={};','let cursors=Object.fromEntries(Object.entries(embedded.states).map(([r,s])=>[r,s.total]));')
    page = page.replace('<h1>FactoryGuard</h1>','<h1>FactoryGuard · Recorded experiment results</h1>')
    page = page.replace('<main>','<main><section class="card"><h2>Explore recorded bearing experiments</h2><p>A variable-speed, variable-load bearing test rig records vibration channels A/C and temperatures. Each experiment is a separate bearing run. Opening this page does not retrain models or connect to live equipment. Reset to replay sequentially; notes stay in this browser.</p><p>B01/B02 are development runs. B04 is an uncorrected diagnostic stress case. Measurement timestamps are provisional. Result generation time and producing code commit were not recorded and remain unknown. Software CI was independently reported for d5be7be; see provenance for evidence.</p></section>'+evidence,1)
    selection=json.loads((source/'selection.json').read_text())
    from factoryguard.alerts.evaluate_v2 import dashboard_bundle
    from factoryguard.alerts.journal import AlertJournal
    alerts=dashboard_bundle(payload,journal=AlertJournal(alert_journal) if alert_journal else None,snapshot=manifest['snapshot_id'])
    page=page.replace('</head>', '<style>'+''.join((ROOT/'site'/name).read_text(encoding='utf-8') for name in ('reviewer.css','layout3.css','alerts.css'))+'</style></head>')
    page=page.replace('</body>', '<script>const alertReplay='+json.dumps(alerts,ensure_ascii=False,allow_nan=False).replace('<','\\u003c')+';const reviewerMetrics='+json.dumps(rows)+';const savedSelection='+json.dumps(selection)+';</script><script>'+ (ROOT/'site/reviewer.js').read_text(encoding='utf-8')+'</script><script>'+(ROOT/'site/architecture.js').read_text(encoding='utf-8')+'</script><script>'+(ROOT/'site/alerts.js').read_text(encoding='utf-8')+'</script><script>'+(ROOT/'site/reviewer_experience.js').read_text(encoding='utf-8')+'</script></body>')
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    (output/'index.html').write_text(page,encoding='utf-8')
    (output/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (output/'.nojekyll').touch()
    return output

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='reports/local/reviewer-site')
    parser.add_argument('--alert-journal',help='Optional private SQLite journal, outside the public export directory')
    args=parser.parse_args()
    if args.alert_journal and Path(args.alert_journal).resolve().is_relative_to(Path(args.output).resolve()):
        parser.error('Keep the private alert database outside browser assets')
    print(build(args.output,args.alert_journal))
