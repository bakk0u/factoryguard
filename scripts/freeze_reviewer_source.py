import json, pathlib, hashlib, shutil
root=pathlib.Path(__file__).resolve().parents[1]; out=root/'site/source'; results=root/'reports/local/release-v3'
import sys
html=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); payload=json.loads(html.split('const embedded=',1)[1].split(';\nlet meta',1)[0])
for run,state in payload['states'].items():
    filename=f'{run}_outer_forecasts.jsonl' if run!='B04' else 'B04_from_B02_forecasts.jsonl'
    saved=[json.loads(s) for s in (results/filename).read_text().splitlines()]
    assert len(saved)==len(state['events'])
    for event,row in zip(state['events'],saved):
        assert event['observation']==row['observation'], (run,'observation')
        assert event['issued_v']==row['forecasts']['smoothing'],(run,'forecast')
    print(run,len(saved),'measurements and predictions match saved outputs')
(out/'replay.json').write_text(json.dumps(payload,allow_nan=False))
for name in ['development_metrics.csv','stress_metrics.csv','selection.json','audit.json','completion.json']:
    shutil.copyfile(results/name,out/name)
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
manifest={'source_run':'release-v3 explicitly selected complete development campaign; no mtime selection','result_code_commit':None,'result_generation_time':None,'missing_provenance':'Producing commit and generation timestamp were not recorded in the campaign artifacts. They are unknown, not inferred from CI or file times.','verified_software_commit':'d5be7be2f73889198aaf7c731510e224e2cbbf5a','reported_independent_ci':'https://github.com/bakk0u/factoryguard/actions/runs/40402759560','checks':'All exported observations and selected forecasts compared exactly to saved experiment forecast JSONL. Audit.json reports campaign metric and selection checks; CI independently reported by user.','experiments':['B01','B02','B04'],'B04':'diagnostic only, uncorrected','B03':'excluded, not accessed','files':files}
(root/'site/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
