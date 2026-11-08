"""Explicit Python-owned validate/index/bundle workflows; no scheduler or fitting."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from factoryguard.assistant.evidence import EvidenceService, Selection
from factoryguard.assistant.retrieval import DocumentationIndex, ROOT, sha
from factoryguard.util import protect_output


def atomic_json(path, value):
    path = protect_output(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(value, out, allow_nan=False, indent=2); out.flush(); os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run_workflow(task, output, *, selection=None, embeddings=False):
    output = protect_output(output)
    service = EvidenceService()
    if task == 'validate':
        result = service.list_experiments()
    elif task == 'refresh':
        producer = sha((Path(__file__).with_name('evidence.py')).read_bytes())
        identity = sha(json.dumps([task, service.snapshot, producer], sort_keys=True).encode())
        path = output/'runs'/('refresh-'+identity+'.json')
        if path.exists():
            return {'record': path.name, 'unchanged': True, 'result': json.loads(path.read_text())['result']}
        records=[]
        for run, state in service.replay['states'].items():
            for channel in 'AC':
                s=Selection(experiment=run,channel=channel,start=1,stop=len(state['events']),as_of=len(state['events']),mode='retrospective',snapshot=service.snapshot)
                records.append(service.get_investigation_summary(s))
        result={'snapshot':service.snapshot,'producer_sha256':producer,'summaries':records}
        atomic_json(path,{'id':identity,'task':task,'completed_utc':datetime.now(timezone.utc).isoformat(),'result':result})
        return {'record':path.name,'result':result}
    elif task == 'index':
        result = DocumentationIndex(output/'docs.sqlite').refresh(embeddings)
    elif task == 'bundle':
        s = Selection.model_validate(selection)
        result = {'selection': s.model_dump(), 'summary': service.get_investigation_summary(s),
                  'quality': service.get_data_quality_report(s), 'measurements': service.get_measurements(s)}
    else:
        raise ValueError('Unknown workflow')
    recorded = {k: v for k, v in result.items() if k != 'unchanged'}
    identity = sha(json.dumps([task, recorded], sort_keys=True).encode())
    path = output / 'runs' / (task+'-'+identity+'.json')
    if not path.exists():
        atomic_json(path, {'id': identity, 'task': task, 'completed_utc': datetime.now(timezone.utc).isoformat(), 'result': recorded})
    return {'record': path.name, 'result': result}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('task', choices=['validate', 'refresh', 'index', 'bundle'])
    p.add_argument('--output', type=Path, default=ROOT/'reports/local/assistant')
    p.add_argument('--selection', help='JSON Selection, required for bundle')
    p.add_argument('--embeddings', action='store_true', help='Explicitly download/use local MIT BGE embedding weights')
    a = p.parse_args()
    print(json.dumps(run_workflow(a.task, a.output, selection=json.loads(a.selection) if a.selection else None,
                                  embeddings=a.embeddings), indent=2))
