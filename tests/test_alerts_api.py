"""Local HTTP/SQLite integration with synthetic measurements, no model fitting."""
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from test_alerts import policy
from test_release_modeling import data
from test_release_application import artifact
from factoryguard.alerts.engine import ROOT, load_policy
from factoryguard.models.forecast import INPUTS
from factoryguard.release import application
from factoryguard.release.store import Store


class AlertAPITests(unittest.TestCase):
    def test_frozen_source_edits_fail_without_recalibrating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'configs').mkdir();(root/'docs').mkdir()
            for name in ('configs/investigation_alerts_v1.json','configs/investigation_alerts_v1.freeze.json','docs/investigation_alert_protocol.md'):
                (root/name).write_bytes((ROOT/name).read_bytes())
            self.assertEqual(load_policy(root).sha256,load_policy().sha256)
            p=root/'configs/investigation_alerts_v1.json';p.write_text(p.read_text().replace('0.99','0.5'))
            with self.assertRaisesRegex(ValueError,'Frozen alert policy changed'):load_policy(root)

    def test_authoritative_cursor_acknowledgment_foreign_origin_and_no_forecast_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=data(n=70);f[list(INPUTS[:2])]=1.;f.loc[31:,list(INPUTS[:2])]=3.
            f['quality__A_sensor_range_exceeded']=False;f['quality__C_sensor_range_exceeded']=False
            workspace=application.create(Path(tmp)/'work',{'B01':f},{'B01':artifact()},{'B01':{}},{})
            store=Store(workspace/'replay.sqlite')
            for _ in range(50):store.step('B01',artifact(),{},return_history=False)
            before=store.state('B01')['events']
            server=application.server(workspace,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            try:
                with patch('factoryguard.alerts.engine_v2.load_policy',return_value=__import__('test_alerts_v2').policy()):
                    result=json.load(urlopen(base+'/api/alerts?run=B01&channel=A&as_of=50'))
                    episode=result['episodes'][0]['id'];self.assertEqual(result['frames'][-1]['state'],'Active alert')
                    for suffix in ('as_of=51','as_of=not-a-number','channel=invalid'):
                        with self.assertRaises(HTTPError) as caught:urlopen(base+'/api/alerts?run=B01&'+suffix)
                        self.assertEqual(caught.exception.code,400)
                    body=json.dumps({'run':'B01','channel':'A','as_of':50,'episode_id':episode}).encode()
                    request=Request(base+'/api/alerts/acknowledge',data=body,headers={'Content-Type':'application/json','Origin':'https://foreign.invalid'})
                    with self.assertRaises(HTTPError) as caught:urlopen(request)
                    self.assertEqual(caught.exception.code,403)
                    request=Request(base+'/api/alerts/acknowledge',data=body,headers={'Content-Type':'application/json'})
                    ack=json.load(urlopen(request));self.assertEqual(len(ack['acknowledgments']),1)
                    self.assertEqual(ack['frames'],result['frames'])
                    self.assertEqual(store.state('B01')['events'],before)
                    old_stream=ack['journal_stream']
                    store.reset('B01');reset=json.load(urlopen(base+'/api/alerts?run=B01&channel=A'))
                    self.assertEqual(reset['frames'],[]);self.assertEqual(reset['acknowledgments'],[])
                    for _ in range(50):store.step('B01',artifact(),{},return_history=False)
                    replayed=json.load(urlopen(base+'/api/alerts?run=B01&channel=A&as_of=50'))
                    self.assertEqual(replayed['episodes'][0]['id'],episode)
                    self.assertNotEqual(replayed['journal_stream'],old_stream)
                    self.assertEqual(replayed['acknowledgments'],[],
                                     'Old acknowledgment must not follow a reset and replay')
                    request=Request(base+'/api/alerts/acknowledge',data=body,
                                    headers={'Content-Type':'application/json'})
                    again=json.load(urlopen(request))
                    self.assertEqual(len(again['acknowledgments']),1)
                    self.assertNotEqual(again['journal_stream'],old_stream)
                    self.assertEqual(store.state('B01')['events'],before)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=5)
