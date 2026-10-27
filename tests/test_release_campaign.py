"""Orchestration failure retention, using generated development tables only."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from test_release_modeling import data
from factoryguard.release import modeling as m
from factoryguard.release.campaign import run,read,write
from factoryguard.release.reporting import audit


class CampaignTests(unittest.TestCase):
    def test_unavailable_family_retained_and_disqualified(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);cfg=read('configs/release_v3.json');cfg['tables']={}
            for r in ('B01','B02','B04'):
                path=root/f'{r}.csv';data(r,40).to_csv(path,index=False,encoding='utf-8');cfg['tables'][r]=str(path)
            write(root/'config.json',cfg);original=m.fit
            def fit(candidate,blocks):
                if candidate['kind']=='xgb':raise ImportError('synthetic dependency failure')
                return original(candidate,blocks)
            with patch('factoryguard.release.modeling.fit',side_effect=fit),contextlib.redirect_stdout(io.StringIO()):
                run(root/'config.json',root/'out')
            done=read(root/'out/completion.json');self.assertEqual(done['candidate_fold_evaluations'],192)
            self.assertEqual(len(done['failures']),24)
            self.assertNotIn('xgb',read(root/'out/selection.json')['selected_group'])
            for r in ('B01','B02'):
                choices=read(root/'out'/f'{r}_inner_choices.json')
                self.assertTrue(all(c is None for g,c in choices.items() if g.startswith('xgb')))
            result=audit(root/'out')
            self.assertEqual(result['candidate_folds_audited'],168)
            self.assertFalse(result['B03_accessed'])
