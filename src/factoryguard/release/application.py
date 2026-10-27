"""Portable bundle preparation and loopback-only offline replay API."""
from pathlib import Path
from importlib.resources import files
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import shutil
from urllib.parse import urlparse, parse_qs

import joblib
import pandas as pd

from factoryguard.models.forecast import digest, load_table, clean
from factoryguard.release.campaign import write, read
from factoryguard.release.context import reference
from factoryguard.release.store import Store
from factoryguard.pipelines.forecast import fresh


def load_artifact(path):
    path=Path(path)
    meta=read(path.with_suffix('.json'))
    if digest(path)!=meta['artifact_sha256']:raise ValueError('Artifact checksum mismatch')
    # Pickle artifacts are local trusted outputs only, never user uploads/API input.
    return joblib.load(path)


def demo(output):
    root=files('factoryguard.release').joinpath('demo')
    meta=json.loads(root.joinpath('manifest.json').read_text(encoding='utf-8'))
    csv=root.joinpath('B01.csv').read_bytes()
    from hashlib import sha256
    if sha256(csv).hexdigest()!=meta['derived_csv_sha256']:raise ValueError('Bundled demo integrity failed')
    for name,key in [('reference.json','reference_sha256'),('artifact.json','artifact_sha256')]:
        if sha256(root.joinpath(name).read_bytes()).hexdigest()!=meta[key]:raise ValueError('Bundled metadata integrity failed')
    import io
    frame=pd.read_csv(io.BytesIO(csv),encoding='utf-8')
    refs=json.loads(root.joinpath('reference.json').read_text(encoding='utf-8'))
    a=json.loads(root.joinpath('artifact.json').read_text(encoding='utf-8'));a['pipeline']=None
    return create(output,{'B01':frame},{'B01':a},{'B01':refs},meta)


def create(output,frames,artifacts,references,metadata):
    out=fresh(output)
    for run,a in artifacts.items():
        joblib.dump(a,out/f'{run}.joblib')
        write(out/f'{run}.json',{'artifact_sha256':digest(out/f'{run}.joblib')})
    write(out/'references.json',references)
    import importlib.metadata
    metadata={**metadata,'software_version':importlib.metadata.version('factoryguard'),
              'reference_sha256':digest(out/'references.json'),
              'runs':list(frames),'models':{r:a['candidate'] for r,a in artifacts.items()},
              'mode':'Offline recorded-data replay; no live sensor connection',
              'B03':'sealed','clock':'CSV clock proxy; ordinal alignment and timestamp meaning provisional'}
    Store(out/'replay.sqlite').initialize(frames,metadata)
    write(out/'workspace.json',{'protocol':'release-v3','database':'replay.sqlite'})
    return out


def full(results,output):
    results=Path(results);cfg=read(results/'frozen_config.json');done=read(results/'completion.json')
    selected=read(results/'selection.json')['selected_group']
    frames={r:load_table(cfg['tables'][r],r,done['table_sha256'][r]) for r in ('B01','B02','B04')}
    artifacts={r:load_artifact(results/f'{tr}_{selected}.joblib') for r,tr in [('B01','B02'),('B02','B01'),('B04','B02')]}
    refs={'B01':reference(frames['B02'],'B02'),'B02':reference(frames['B01'],'B01'),
          'B04':reference(frames['B02'],'B02')}
    return create(output,frames,artifacts,refs,{'source':'Paderborn University DOI 10.5281/zenodo.10868257; CC BY 4.0',
                  'evaluation':'B01/B02 out-of-run development selection replay; B04 post-selection diagnostic',
                  'source_hashes':done['table_sha256'],'selection':read(results/'selection.json')})


def html(payload=None):
    template=files('factoryguard.release').joinpath('dashboard.html').read_text(encoding='utf-8')
    # Escaping < prevents data text from closing a script element.
    return template.replace('/*PAYLOAD*/null',json.dumps(clean(payload),ensure_ascii=False,allow_nan=False).replace('<','\\u003c'))


def export(workspace,output):
    """Render from a temporary DB clone, preserving the user's persisted cursor."""
    import tempfile
    from factoryguard.util import protect_output
    output=protect_output(output)
    workspace=Path(workspace);store=Store(workspace/'replay.sqlite');meta=store.metadata()
    refs=read(workspace/'references.json');states={}
    with tempfile.TemporaryDirectory() as tmp:
        clone=Store(Path(tmp)/'replay.sqlite')
        with store.connect() as src, clone.connect() as dst:src.backup(dst)
        for r in meta['runs']:
            clone.reset(r);a=load_artifact(workspace/f'{r}.joblib')
            state=clone.state(r)
            events=[]
            while not state['exhausted']:
                state=clone.step(r,a,refs[r],return_history=False)
                events.extend(state['events'])
            state['events']=events
            states[r]=state
    output=Path(output)
    if output.exists():raise ValueError('Export path already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html({'metadata':meta,'states':states}),encoding='utf-8')
    return output


def server(workspace,port=8765):
    workspace=Path(workspace);store=Store(workspace/'replay.sqlite');meta=store.metadata()
    refs=read(workspace/'references.json');artifacts={r:load_artifact(workspace/f'{r}.joblib') for r in meta['runs']}
    actual_reference_hash=digest(workspace/'references.json')
    if meta.get('reference_sha256',actual_reference_hash)!=actual_reference_hash:
        raise ValueError('Fixed development references changed; restore the original workspace references')
    meta['reference_sha256']=actual_reference_hash
    class Handler(BaseHTTPRequestHandler):
        def reply(self,value,status=200,kind='application/json; charset=utf-8'):
            body=(value if isinstance(value,str) else json.dumps(clean(value),ensure_ascii=False,allow_nan=False)).encode('utf-8')
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
        def do_GET(self):
            try:
                route=urlparse(self.path)
                if route.path=='/':self.reply(html(),kind='text/html; charset=utf-8')
                elif route.path=='/health':self.reply({'status':'ok','mode':meta['mode'],'B03':'sealed'})
                elif route.path=='/api/meta':self.reply(meta)
                elif route.path=='/api/state':self.reply(store.state(parse_qs(route.query).get('run',['B01'])[0]))
                elif route.path=='/api/notes':self.reply(store.notes(parse_qs(route.query).get('run',['B01'])[0]))
                else:self.reply({'error':'not found'},404)
            except (ValueError,KeyError) as exc:self.reply({'error':str(exc)},400)
        def do_POST(self):
            try:
                # Same-origin local controls only; no uploads, path arguments or arbitrary model loading.
                origin=self.headers.get('Origin')
                if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
                    self.reply({'error':'foreign origin rejected'},403);return
                n=int(self.headers.get('Content-Length','0'))
                if n<1 or n>20000:raise ValueError('JSON control body exceeds size limit')
                if not self.headers.get('Content-Type','').startswith('application/json'):raise ValueError('JSON required')
                body=json.loads(self.rfile.read(n))
                if not isinstance(body,dict) or not isinstance(body.get('run'),str):raise ValueError('JSON object with string run required')
                run=body['run']
                if run not in artifacts:raise ValueError('Run unavailable; B03 sealed')
                if self.path=='/api/step':self.reply(store.step(run,artifacts[run],refs[run]))
                elif self.path=='/api/reset':self.reply(store.reset(run))
                elif self.path=='/api/notes/save':self.reply(store.notes(run,'save',body))
                elif self.path=='/api/notes/delete':self.reply(store.notes(run,'delete',body))
                else:self.reply({'error':'not found'},404)
            except (ValueError,KeyError,TypeError) as exc:self.reply({'error':str(exc)},400)
        def log_message(self,*args):pass
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
