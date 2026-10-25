import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import joblib
import numpy as np

from test_selection import fixture
from factoryguard.models.forecast import INPUTS, TIME
from factoryguard.release import modeling as m
from factoryguard.release.campaign import folds


def data(run='B01',n=100):
    f=fixture(run,n)
    for j,c in enumerate(m.DESCRIPTORS): f[c]=2+j+np.arange(n)*.001
    return f


class ReleaseModelingTests(unittest.TestCase):
    def test_budget_formulas_and_missing_policy(self):
        self.assertEqual(len(m.candidates()),32)
        self.assertEqual(len(m.ENRICHED),27)
        f=data();b=m.prepare(f,'B01')
        np.testing.assert_allclose(b.X['temporal'][2,14:16],b.current[:3].mean(0))
        np.testing.assert_allclose(b.X['temporal'][2,16:18],b.current[:3].std(0))
        self.assertFalse(b.common[:2].any())
        f.loc[5,m.DESCRIPTORS[0]]=np.nan;b=m.prepare(f,'B01')
        self.assertEqual(b.exclusion[5],'nonfinite_features_or_history')
        self.assertEqual(len(b.frame),100)

    def test_future_independence_all_families_and_formulations(self):
        tr=m.prepare(data(),'B01');f=data('B02');changed=f.copy()
        changed.loc[50:,list(INPUTS)+list(m.DESCRIPTORS)]=1e6
        a,b=m.prepare(f,'B02'),m.prepare(changed,'B02')
        for c in m.candidates():
            if c['rank']>0: continue
            model=m.fit(c,[tr])
            np.testing.assert_allclose(m.predict(c,model,a)[:50],m.predict(c,model,b)[:50],equal_nan=True)
        np.testing.assert_allclose(a.X['temporal'][:50],b.X['temporal'][:50],equal_nan=True)

    def test_split_dependencies_scaler_and_reload(self):
        f=data()
        for train,val,s in folds(f,'B01'):
            td={i+k for i in np.flatnonzero(train.common) for k in (-2,-1,0,1)}
            vd={val.start+i+k for i in np.flatnonzero(val.common) for k in (-2,-1,0,1)}
            self.assertFalse(td & vd)
            self.assertEqual(train.exclusion[-1],'pending_block_end')
            c=next(c for c in m.candidates() if c['id']=='ridge_temporal_delta_0')
            model=m.fit(c,[train]);mean=model.named_steps['scale'].mean_.copy()
            np.testing.assert_allclose(mean,train.X['temporal'][train.common].mean(0))
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'model.joblib';joblib.dump(model,p)
                np.testing.assert_allclose(m.predict(c,model,val),m.predict(c,joblib.load(p),val),equal_nan=True)
            np.testing.assert_array_equal(mean,model.named_steps['scale'].mean_)

    def test_boundary_gap_resets_and_reserved_run_rejected(self):
        f=data(n=6)
        f[TIME]=['19-Oct-2021 09:00:00','19-Oct-2021 09:00:18','19-Oct-2021 09:00:42',
                 '19-Oct-2021 09:01:07','19-Oct-2021 09:01:25','19-Oct-2021 09:01:43']
        b=m.prepare(f,'B01')
        self.assertEqual(b.exclusion[2],'expired_gap')
        self.assertTrue(b.history_ready[2]);self.assertFalse(b.history_ready[3]);self.assertTrue(b.history_ready[5])
        with self.assertRaises(ValueError): m.prepare(data('B03'),'B03')
        with self.assertRaises(ValueError): m.fit(m.candidates()[0],[m.prepare(data('B04'),'B04')])

    def test_direct_and_delta_are_explicit(self):
        tr=m.prepare(data(),'B01');ev=m.prepare(data('B02'),'B02')
        for formulation in ('direct','delta'):
            c=next(c for c in m.candidates() if c['id']==f'ridge_current_{formulation}_0')
            model=m.fit(c,[tr]);raw=model.predict(ev.X['current'])
            expected=raw+ev.current if formulation=='delta' else raw
            np.testing.assert_allclose(m.predict(c,model,ev),expected)
