"""Generated fixtures exercise leakage boundaries; no real reserve access."""
import copy
from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd

from factoryguard.models.forecast import INPUTS, TIME, ID, RUN, WARM
from factoryguard.models.selection import (FiniteGate, candidates, prepare, splits, fit_candidate,
    predict, metrics, choose_inner, select_method, GROUPS, TEMPORAL_NAMES)
from factoryguard.pipelines.select_forecast import validate_config, coverage, run


def config(): return json.loads(Path('configs/selection_v2.json').read_text())


def fixture(run='B01', n=100):
    rng=np.random.default_rng(9)
    t=datetime(2021,10,19,9)
    f=pd.DataFrame({RUN:[run]*n,ID:range(1,n+1),TIME:[(t+timedelta(seconds=18*i)).strftime('%d-%b-%Y %H:%M:%S') for i in range(n)],WARM:[False]*n})
    for j,c in enumerate(INPUTS): f[c]=j+np.arange(n)*.01+rng.normal(0,.002,n)
    return f


def candidate(group): return next(c for c in candidates(config()) if c['group']==group)


class SelectionTests(unittest.TestCase):
    def test_frozen_budget_and_feature_allowlist(self):
        cfg=config();validate_config(cfg)
        self.assertEqual(len(candidates(cfg)),18)
        self.assertEqual(len(TEMPORAL_NAMES),14)
        self.assertFalse(any(k.startswith(('quality__','provenance__')) for k in TEMPORAL_NAMES))
        with self.assertRaises(ValueError): validate_config(dict(cfg,ridge_alpha=[1,10,100,1000]))

    def test_temporal_formulas_and_history_readiness(self):
        f=fixture();b=prepare(f,'B01')
        self.assertFalse(b.history_ready[:2].any());self.assertTrue(b.history_ready[2:].all())
        x=b.X['temporal'][2]
        np.testing.assert_array_equal(x[7:9],b.current[1])
        np.testing.assert_allclose(x[9:11],b.current[2]-b.current[1])
        np.testing.assert_allclose(x[11:],f.iloc[:3][list(INPUTS[4:])].mean())
        self.assertEqual(b.exclusion[-1],'pending_block_end')

    def test_future_data_and_quality_independence(self):
        train=prepare(fixture(),'B01');future=fixture('B02');changed=future.copy()
        changed.loc[50:,list(INPUTS)]=1000000
        changed['quality__any_warning']=True
        a,b=prepare(future,'B02'),prepare(changed,'B02')
        for g in GROUPS:
            c=candidate(g);model=fit_candidate(c,train)
            np.testing.assert_allclose(predict(c,model,a)[:50],predict(c,model,b)[:50],equal_nan=True)
        np.testing.assert_allclose(a.X['temporal'][:50],b.X['temporal'][:50],equal_nan=True)
        self.assertNotEqual(a.target[49,0],b.target[49,0])

    def test_gap_and_experiment_resets_and_exact_boundary(self):
        f=fixture(n=6)
        f[TIME]=['19-Oct-2021 09:00:00','19-Oct-2021 09:00:18','19-Oct-2021 09:00:42','19-Oct-2021 09:01:07','19-Oct-2021 09:01:25','19-Oct-2021 09:01:43']
        b=prepare(f,'B01')
        self.assertTrue(b.history_ready[2]);self.assertFalse(b.history_ready[3]);self.assertFalse(b.history_ready[4]);self.assertTrue(b.history_ready[5])
        self.assertEqual(b.exclusion[2],'expired_gap')
        c=candidate('smoothing');p=predict(c,None,b)
        np.testing.assert_allclose(p[3],b.current[3])
        separate=prepare(fixture('B02',6),'B02')
        np.testing.assert_allclose(predict(c,None,separate)[0],separate.current[0])

    def test_expanding_splits_purge_all_dependency_overlap(self):
        f=fixture()
        for train,val,s in splits(f,'B01',config()):
            train_dependencies=set()
            for i in np.flatnonzero(train.common): train_dependencies.update(range(train.start+i-2,train.start+i+2))
            val_dependencies=set()
            for i in np.flatnonzero(val.common): val_dependencies.update(range(val.start+i-2,val.start+i+2))
            self.assertFalse(train_dependencies & val_dependencies)
            self.assertLess(max(train_dependencies),min(val_dependencies))
            self.assertEqual(train.stop,s['validation_start'])
            self.assertEqual(train.exclusion[-1],'pending_block_end')
            self.assertFalse(val.history_ready[:2].any())
            self.assertNotIn(s['purged_cross_boundary_source_index'],np.flatnonzero(train.common))

    def test_fold_scaler_isolation_and_pipeline_gate(self):
        f=fixture();train,val,_=splits(f,'B01',config())[0]
        c=candidate('ridge_temporal');m=fit_candidate(c,train)
        np.testing.assert_allclose(m.named_steps['scale'].mean_,train.X['temporal'][train.common].mean(0))
        mean=m.named_steps['scale'].mean_.copy();coef=m.named_steps['estimate'].coef_.copy()
        altered=fixture('B02');altered[list(INPUTS)]=1e9
        predict(c,m,prepare(altered,'B02'))
        np.testing.assert_array_equal(mean,m.named_steps['scale'].mean_)
        np.testing.assert_array_equal(coef,m.named_steps['estimate'].coef_)
        with self.assertRaises(ValueError):m.predict(np.full((1,14),np.nan))

    def test_nonfinite_coverage_no_imputation_or_record_drop(self):
        f=fixture(n=12);f.loc[5,INPUTS[2]]=np.nan
        b=prepare(f,'B01');self.assertEqual(len(b.frame),12)
        self.assertEqual(b.exclusion[5],'nonfinite_features_or_history')
        c=candidate('ridge_current');m=fit_candidate(c,b);p=predict(c,m,b)
        self.assertTrue(np.isnan(p[5]).all())
        cov=coverage(b,p)
        self.assertEqual(cov['channels']['A']['broad_persistence_pairs'],11)
        self.assertEqual(cov['channels']['A']['candidate_unavailable_on_broad'],1)
        self.assertEqual(cov['common_pairs'],8)
        self.assertTrue(np.isnan(b.frame.loc[5,INPUTS[2]]))

    def test_smoothing_formula_missing_reset_and_no_targets(self):
        b=prepare(fixture(n=10),'B01');c=candidate('smoothing');p=predict(c,None,b)
        np.testing.assert_allclose(p[1],.8*b.current[1]+.2*b.current[0])
        before=p.copy();b.target[:]=1e9
        np.testing.assert_allclose(predict(c,None,b),before)
        b.current[3,0]=np.nan;p=predict(c,None,b)
        self.assertTrue(np.isnan(p[3,0]));self.assertEqual(p[4,0],b.current[4,0])

    def test_experiment_roles_rejected_before_fit(self):
        with self.assertRaises(ValueError): prepare(fixture('B03'),'B03')
        with self.assertRaises(ValueError): fit_candidate(candidate('ridge_current'),prepare(fixture('B04'),'B04'))
        mixed=fixture();mixed.loc[5,RUN]='B02'
        with self.assertRaises(ValueError): prepare(mixed,'B01')

    def test_tree_channels_fit_independently_and_reload(self):
        b=prepare(fixture(),'B01');c=candidate('tree_temporal');m=fit_candidate(c,b)
        self.assertEqual(len(m.named_steps['estimate'].estimators_),2)
        other=copy.deepcopy(b);other.target[:,1]*=1000;other.current[:,1]*=1000
        other.X=b.X  # Keep inputs fixed, change C's target task only.
        m2=fit_candidate(c,other)
        np.testing.assert_allclose(m.predict(b.X['temporal'][b.common])[:,0],m2.predict(b.X['temporal'][b.common])[:,0])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'pipeline.joblib';joblib.dump(m,p);loaded=joblib.load(p)
            np.testing.assert_array_equal(predict(c,m,b),predict(c,loaded,b))

    def test_inner_tie_preference_and_empty_fold_rejection(self):
        c=[c for c in candidates(config()) if c['group']=='ridge_current']
        trials=[{'candidate':x,'validation_score':s} for x,s in zip(c,[.905,.9,.899])]
        self.assertEqual(choose_inner(trials,'ridge_current')['params']['alpha'],100)
        for t in trials:t['validation_score']=float('inf')
        with self.assertRaises(ValueError):choose_inner(trials,'ridge_current')

    def test_selection_equal_cells_consistency_and_simple_ties(self):
        outer={r:{g:{c:{'mae_ratio':1.0} for c in 'AC'} for g in GROUPS} for r in ('B01','B02')}
        self.assertEqual(select_method(outer,config())['selected_group'],'persistence')
        for r in outer:
            for c in 'AC':
                outer[r]['smoothing'][c]['mae_ratio']=.95
                outer[r]['tree_temporal'][c]['mae_ratio']=.94
        self.assertEqual(select_method(outer,config())['selected_group'],'smoothing')
        outer['B01']['smoothing']['A']['mae_ratio']=1.1
        self.assertEqual(select_method(outer,config())['selected_group'],'tree_temporal')
        with self.assertRaises(ValueError):select_method({**outer,'B04':outer['B01']},config())

    def test_common_pairs_identical_and_broad_persistence_retained(self):
        b=prepare(fixture(),'B01')
        counts=[]
        for g in GROUPS:
            c=candidate(g);p=predict(c,fit_candidate(c,b),b)
            counts.append(metrics(b,p)['A']['n'])
        self.assertEqual(set(counts),{97})
        self.assertEqual(metrics(b,b.current,False)['A']['n'],99)

    def test_full_fixture_search_freezes_before_fit_and_stress_after_selection(self):
        import contextlib,io
        import factoryguard.pipelines.select_forecast as cli
        original_fit=cli.fit_candidate;original_load=cli.load_table
        with tempfile.TemporaryDirectory() as d,contextlib.redirect_stdout(io.StringIO()):
            root=Path(d);cfg=config();out=root/'result'
            for r in ('B01','B02','B04'):
                path=root/f'{r}.csv';fixture(r,60).to_csv(path,index=False);cfg['tables'][r]=str(path)
            cp=root/'config.json';cp.write_text(json.dumps(cfg))
            def checked_fit(*args,**kwargs):
                self.assertTrue((out/'pre_search_manifest.json').exists())
                return original_fit(*args,**kwargs)
            def checked_load(path,r,*args,**kwargs):
                if r=='B04':self.assertTrue((out/'selection.json').exists())
                self.assertNotEqual(r,'B03')
                return original_load(path,r,*args,**kwargs)
            with patch.object(cli,'fit_candidate',side_effect=checked_fit),patch.object(cli,'load_table',side_effect=checked_load):run(cp,out)
            completion=json.loads((out/'completion.json').read_text())
            self.assertEqual(completion['learned_pipeline_fits'],92)
            self.assertFalse(completion['pooled_final_fit_executed'])
            self.assertEqual(len(json.loads((out/'inner_search.json').read_text())),36)
            self.assertEqual(len(pd.read_csv(out/'inner_trials.csv')),432)
            self.assertEqual(len((out/'B01_outer_forecasts.jsonl').read_text().splitlines()),60)
            self.assertTrue((out/'proposed_final_config.json').exists())


if __name__=='__main__':unittest.main()
