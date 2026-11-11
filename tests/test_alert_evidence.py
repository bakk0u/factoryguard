import copy
import unittest

from factoryguard.assistant.evidence import EvidenceService, Selection


class AlertEvidenceTests(unittest.TestCase):
    def test_current_alert_method_is_retrievable_but_retrospective_annotation_audit_is_not(self):
        import tempfile
        from pathlib import Path
        from factoryguard.assistant.retrieval import DocumentationIndex, passages
        source='docs/investigation_alert_protocol.md'
        audit=[p for p in passages() if p['source']['path']==source and p['source']['section']=='What is and is not labelled']
        self.assertTrue(audit);self.assertTrue(all(p['availability']=='retrospective' for p in audit))
        with tempfile.TemporaryDirectory() as tmp:
            index=DocumentationIndex(Path(tmp)/'docs.sqlite');index.refresh()
            found=index.search('Explain investigation alert activation persistence hysteresis and clearance',replay=True,limit=4)
            self.assertTrue(any(p['source']['path']==source for p in found['records']))
            self.assertTrue(all(p['availability']=='pre_replay_method' for p in found['records']))
            found=index.search('investigation alert fault annotations 13:32 18:26',replay=True,limit=6)
            self.assertFalse(any(p['source']['path']==source and p['source']['section']=='What is and is not labelled' for p in found['records']))

    def test_pre_calibration_evidence_does_not_expose_future_scales_or_transitions(self):
        service=EvidenceService()
        s=Selection(experiment='B01',channel='A',start=1,stop=3,as_of=3,snapshot=service.snapshot)
        record=next(r for r in service.get_investigation_summary(s)['records'] if r['kind']=='alert')
        d=record['data'];self.assertEqual(d['position'],3);self.assertEqual(d['availability'],'unavailable')
        self.assertEqual(d['state'],'No active alert');self.assertIsNone(d['calibration_sha256'])
        self.assertEqual(d['transitions'],[])
        self.assertTrue(all(v['activation_v'] is None for v in d['signals'].values()))
        self.assertEqual(record['source']['snapshot_sha256'],service.snapshot)
        altered=copy.deepcopy(service)
        for e in altered.replay['states']['B01']['events'][3:]:e['rms_v'][0]=999999.
        self.assertEqual(record,next(r for r in altered.get_investigation_summary(s)['records'] if r['kind']=='alert'))

    def test_alert_citations_are_channel_and_period_specific(self):
        service=EvidenceService();ids=[]
        for ch in ('A','C'):
            s=Selection(experiment='B01',channel=ch,start=2,stop=3,as_of=3,snapshot=service.snapshot)
            r=next(r for r in service.get_investigation_summary(s)['records'] if r['kind']=='alert')
            self.assertEqual(r['data']['channel'],ch)
            self.assertTrue(all(2<=t['position']<=3 for t in r['data']['transitions']))
            ids.append(r['id'])
        self.assertNotEqual(*ids)
