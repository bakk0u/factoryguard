from pathlib import Path
import json
import tempfile
import threading
import unittest
from urllib.request import urlopen,Request
from urllib.error import HTTPError

import numpy as np
from test_release_modeling import data
from factoryguard.models.forecast import INPUTS,TIME
from factoryguard.release import modeling as m
from factoryguard.release.context import reference,compare,notices
from factoryguard.release.store import Store
from factoryguard.release import application as app


def artifact():
    return {'candidate':next(c for c in m.candidates() if c['id']=='smoothing_0.5'),'pipeline':None}


class ReleaseAppTests(unittest.TestCase):
    def test_store_future_independence_persistence_and_reset(self):
        with tempfile.TemporaryDirectory() as d:
            f=data(n=10);changed=f.copy();changed.loc[6:,list(INPUTS)]=1e8
            stores=[Store(Path(d)/name) for name in ('one.sqlite','two.sqlite')]
            for s,frame in zip(stores,(f,changed)):s.initialize({'B01':frame},{'runs':['B01']})
            for _ in range(6):
                states=[s.step('B01',artifact(),{}) for s in stores]
                self.assertEqual(states[0]['events'],states[1]['events'])
            reopened=Store(stores[0].path)
            self.assertEqual(reopened.state('B01')['revealed'],6)
            self.assertEqual(len(reopened.state('B01')['events']),6)
            self.assertEqual(reopened.reset('B01')['events'],[])
            self.assertEqual(reopened.step('B01',artifact(),{})['events'][0]['issued_v'],f.iloc[0][list(INPUTS[:2])].tolist())
            with self.assertRaises(ValueError):reopened.state('B03')

    def test_context_counts_missing_and_sparse_not_broadened(self):
        ref=reference(data('B02',19),'B02');row=data(n=1).iloc[0].to_dict();r=compare(row,ref)
        self.assertEqual(r['status'],'sparse');self.assertEqual(r['n'],19)
        self.assertTrue(all(v['difference_from_median'] is None for v in r['measures'].values()))
        ref=reference(data('B02',21),'B02');r=compare(row,ref)
        self.assertEqual(r['status'],'supported')
        row[INPUTS[4]]=10000;self.assertEqual(compare(row,ref)['status'],'unseen')

    def test_gap_expiry_and_notice_categories(self):
        f=data(n=4);f[TIME]=['19-Oct-2021 09:00:00','19-Oct-2021 09:00:24','19-Oct-2021 09:01:00','19-Oct-2021 09:01:18']
        f['context__T1_c']=111.;f['quality__A_sensor_range_exceeded']=True
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'x.sqlite');s.initialize({'B01':f},{})
            s.step('B01',artifact(),{});e=s.step('B01',artifact(),{})['events'][-1]
            self.assertEqual(e['resolved']['status'],'scored')
            e=s.step('B01',artifact(),{})['events'][-1]
            self.assertEqual(e['resolved']['status'],'expired_gap')
            self.assertEqual(e['issued_v'],e['rms_v'])
            self.assertIsNone(e['rolling3_rms_v'])
            kinds={n['kind'] for n in e['notices']}
            self.assertTrue({'measurement','gap','temperature','context'}.issubset(kinds))
            self.assertNotIn('forecast',kinds)

    def test_gradual_change_survives_low_forecast_error(self):
        f=data(n=20);f[list(INPUTS[:2])]=np.arange(20)[:,None]*.001+np.array([[1.,2.]])
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'x.sqlite');s.initialize({'B01':f},{})
            for _ in range(20):state=s.step('B01',artifact(),{})
            last=state['events'][-1]
            self.assertGreater(last['level_change_from_segment_first3_v'][0],.015)
            self.assertLess(abs(last['resolved']['error_v'][0]),.003)
            f.loc[10:,list(INPUTS[:2])]+=1
            b=m.prepare(f,'B01');pred=m.predict(artifact()['candidate'],None,b)
            self.assertGreater(abs(b.target[9,0]-pred[9,0]),.9)

    def test_http_workflow_no_future_rows_and_foreign_origin(self):
        with tempfile.TemporaryDirectory() as d:
            f=data(n=5);out=app.create(Path(d)/'work',{'B01':f},{'B01':artifact()},{'B01':{}},{})
            server=app.server(out,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            try:
                self.assertEqual(json.load(urlopen(base+'/health'))['B03'],'sealed')
                self.assertEqual(json.load(urlopen(base+'/api/state?run=B01'))['events'],[])
                req=Request(base+'/api/step',data=b'{"run":"B01"}',headers={'Content-Type':'application/json'})
                state=json.load(urlopen(req));self.assertEqual(state['revealed'],1)
                self.assertEqual(len(state['events']),1);self.assertIsNone(state['events'][0]['resolved'])
                req.add_header('Origin','https://external.example')
                with self.assertRaises(HTTPError) as e:urlopen(req)
                self.assertEqual(e.exception.code,403)
                with self.assertRaises(HTTPError):urlopen(base+'/api/state?run=B03')
                exported=app.export(out,Path(d)/'offline.html')
                self.assertIn('precomputed full replay embedded',exported.read_text(encoding='utf-8'))
                self.assertEqual(Store(out/'replay.sqlite').state('B01')['revealed'],1)
            finally:server.shutdown();server.server_close();thread.join()

    def test_bundled_demo_contract(self):
        with tempfile.TemporaryDirectory() as d:
            out=app.demo(Path(d)/'démo')
            s=Store(out/'replay.sqlite');meta=s.metadata()
            self.assertEqual(s.state('B01')['total'],377)
            self.assertIn('CC BY',meta['license'])
            self.assertEqual(meta['models']['B01']['params']['alpha'],.2)
            with self.assertRaises(ValueError):app.demo(out)
