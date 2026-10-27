from pathlib import Path
import tempfile
import unittest
import numpy as np
from test_release_modeling import data
from test_release_application import artifact
from factoryguard.release.modeling import prepare
from factoryguard.release.investigation import evidence
from factoryguard.release.store import Store
from factoryguard.models.forecast import INPUTS,TIME


class InvestigationTests(unittest.TestCase):
    def test_windows_missingness_and_transition_reset(self):
        f=data(n=12)
        e=evidence(prepare(f.iloc[:6],'B01'))
        self.assertEqual(e['status'],'available')
        expected=f.iloc[3:6][list(INPUTS)].mean()-f.iloc[:3][list(INPUTS)].mean()
        np.testing.assert_allclose(list(e['sustained'].values()),expected)
        f.loc[5,INPUTS[4]]=1000
        self.assertEqual(evidence(prepare(f.iloc[:6],'B01'))['same_bin_consecutive_n'],1)
        f=data(n=6);f.loc[4,INPUTS[0]]=np.nan
        e=evidence(prepare(f,'B01'));self.assertIsNone(e['sustained'][INPUTS[0]])
        self.assertEqual(e['status'],'unavailable')

    def test_future_and_gap_independence(self):
        f=data(n=12);before=evidence(prepare(f.iloc[:6],'B01'))
        f.loc[6:,list(INPUTS)]=9999
        self.assertEqual(before,evidence(prepare(f.iloc[:6],'B01')))
        f.loc[5,TIME]='19-Oct-2021 09:20:00'
        e=evidence(prepare(f.iloc[:6],'B01'))
        self.assertEqual(e['same_bin_consecutive_n'],1)
        self.assertTrue(all(v is None for v in e['sudden'].values()))

    def test_notes_survive_reset_restart_and_explicit_delete(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'db.sqlite');s.initialize({'B01':data(n=8)},{})
            with self.assertRaises(ValueError):s.notes('B01','save',{'start':1,'stop':2,'text':'future'})
            for _ in range(3):s.step('B01',artifact(),{})
            notes=s.notes('B01','save',{'start':1,'stop':3,'text':'Engineer observation'})
            s.reset('B01');s=Store(s.path)
            self.assertEqual(s.notes('B01'),notes)
            self.assertEqual(s.notes('B01','delete',{'id':notes[0]['id']}),[])
            self.assertEqual(s.state('B01')['events'],[])
