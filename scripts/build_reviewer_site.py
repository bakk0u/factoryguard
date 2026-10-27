"""Build a server-free reviewer site from explicitly pinned derived results."""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import subprocess
from factoryguard.release.application import html as dashboard

ROOT = Path(__file__).resolve().parents[1]

def build(output):
    source = ROOT / 'site/source'
    manifest = json.loads((ROOT / 'site/source-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Source integrity failed: {name}')
    payload = json.loads((source / 'replay.json').read_text())
    manifest['website_build_commit'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    payload['metadata']['reviewer_source_manifest'] = manifest
    with (source / 'development_metrics.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    with (source / 'stress_metrics.csv').open(newline='', encoding='utf-8') as stream:
        rows += list(csv.DictReader(stream))
    columns = ['training_run','evaluation_run','group','candidate','partition','coverage','channel','n','mae_v','rmse_v','mae_skill']
    cells = lambda row: ''.join('<td>'+html.escape(str(row[c]))+'</td>' for c in columns)
    evidence = '<details class="card"><summary>Saved model-comparison results · all candidates</summary><p>Development selection results, not an independent final test. Negative skill means worse than persistence. Training and evaluation partitions and common-pair coverage are explicit. Historical direction-specific settings are preserved; final pooled alpha 0.5 is not substituted.</p><div class="scroll"><table><tr>'+''.join('<th>'+c+'</th>' for c in columns)+'</tr>'+''.join('<tr>'+cells(row)+'</tr>' for row in rows)+'</table></div></details>'
    page = dashboard(payload)
    page = page.replace('precomputed full replay embedded, no persistence or live connection.', 'precomputed results; browser-local notes; no live connection.')
    page = page.replace('let cursors={};','let cursors=Object.fromEntries(Object.entries(embedded.states).map(([r,s])=>[r,s.total]));')
    page = page.replace('<h1>FactoryGuard</h1>','<h1>FactoryGuard · Recorded experiment results</h1>')
    page = page.replace('<main>','<main><section class="card"><h2>Explore recorded bearing experiments</h2><p>A variable-speed, variable-load bearing test rig records vibration channels A/C and temperatures. Each experiment is a separate bearing run. Opening this page does not retrain models or connect to live equipment. Reset to replay sequentially; notes stay in this browser.</p><p>B01/B02 are development runs. B04 is an uncorrected diagnostic stress case. Measurement timestamps are provisional. Result generation time and producing code commit were not recorded and remain unknown. Software CI was independently reported for d5be7be; see provenance for evidence.</p></section>'+evidence,1)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    (output/'index.html').write_text(page,encoding='utf-8')
    (output/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (output/'.nojekyll').touch()
    return output

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='reports/local/reviewer-site')
    print(build(parser.parse_args().output))
