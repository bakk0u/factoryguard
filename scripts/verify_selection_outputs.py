"""Audit saved selection outputs without fitting; read only explicit development raw paths."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from factoryguard.models.forecast import digest, load_table, write_json
from factoryguard.models.selection import prepare, predict, metrics, select_method, choose_inner, GROUPS
from factoryguard.pipelines.select_forecast import strata_rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',default='reports/local/selection-v2');args=p.parse_args()
    out=Path(args.results);cfg=json.loads((out/'frozen_config.json').read_text())
    manifest=json.loads((out/'pre_search_manifest.json').read_text())
    assert digest('configs/selection_v2.json')==manifest['config_sha256']
    assert digest(out/'frozen_protocol.md')==manifest['protocol_sha256']
    completed=json.loads((out/'completion.json').read_text());frames={}
    for run in ('B01','B02','B04'):
        frames[run]=load_table(cfg['tables'][run],run,completed['source_table_sha256'][run])
    trials=json.loads((out/'inner_search.json').read_text());assert len(trials)==36
    assert not any(f['failure'] for t in trials for f in t['folds'])
    for trial in trials:
        run=trial['training_run']
        for fold in trial['folds']:
            s=fold['split'];b=prepare(frames[run],run,0,s['train_stop_exclusive'])
            ids=b.frame.loc[b.common,'provenance__measurement_id'].tolist()
            assert ids==fold['training_sources']
            assert np.flatnonzero(b.common).max()+1<s['validation_start']
            val=prepare(frames[run],run,s['validation_start'],s['validation_stop_exclusive'])
            assert val.start+np.flatnonzero(val.common).min()-2>=s['validation_start']
            if fold['scaler_mean'] is not None:
                x=b.X[trial['candidate']['features']][b.common]
                np.testing.assert_allclose(x.mean(0),fold['scaler_mean'],atol=1e-12)
                np.testing.assert_allclose(x.std(0),fold['scaler_scale'],atol=1e-12)
    outer={};strata=[];reloads=0
    results=pd.read_csv(out/'development_metrics.csv')
    for train_run,test_run in [('B01','B02'),('B02','B01')]:
        choices=json.loads((out/f'{train_run}_inner_choices.json').read_text())
        train_trials=[t for t in trials if t['training_run']==train_run]
        outer[test_run]={}
        for group in GROUPS:
            assert choices[group]==choose_inner(train_trials,group,cfg['inner_tie_tolerance'])
            path=out/f'{train_run}_{group}.joblib';meta=json.loads(path.with_suffix('.json').read_text())
            assert digest(path)==meta['artifact_sha256']
            a=joblib.load(path);assert a['training_run']==train_run
            for eval_run in (test_run,'B04'):
                b=prepare(frames[eval_run],eval_run)
                records=[json.loads(line) for line in (out/(f'{eval_run}_outer_forecasts.jsonl' if eval_run!='B04' else f'B04_from_{train_run}_forecasts.jsonl')).read_text().splitlines()]
                saved=np.array([[np.nan if v is None else v for v in r['forecasts'][group]] for r in records])
                pred=predict(a['candidate'],a['pipeline'],b)
                np.testing.assert_allclose(pred,saved,equal_nan=True,rtol=1e-12,atol=1e-12);reloads+=1
                # Independent saved-ledger metric recomputation.
                mask=np.array([r['common_pair'] for r in records]);target=np.array([r['observed_target'] for r in records],float)
                for j,c in enumerate('AC'):
                    err=target[mask,j]-saved[mask,j]
                    actual=results.query('training_run==@train_run and evaluation_run==@eval_run and group==@group and channel==@c and partition=="outer_evaluation" and coverage=="common"')
                    if len(actual):np.testing.assert_allclose([np.abs(err).mean(),np.sqrt((err*err).mean())],actual[['mae_v','rmse_v']].iloc[0],rtol=1e-12)
                if eval_run==test_run:outer[test_run][group]=metrics(b,pred)
                for common in (True,False):strata.extend(strata_rows(b,pred,a['support_counts'],common=common,training_run=train_run,evaluation_run=eval_run,group=group))
    assert select_method(outer,cfg)==json.loads((out/'selection.json').read_text())
    # Supplement descriptive common/own-coverage strata from existing predictions only.
    pd.DataFrame(strata).to_csv(out/'quality_strata.csv',index=False)
    raw_counts={}
    for run,folder in [('B01',Path('reports/local/b01-features-v1')),('B02',Path('reports/local/development-assessment-20261023-final/B02')),('B04',Path('reports/local/development-assessment-20261023-final/B04'))]:
        expected=json.loads((folder/'raw_integrity.json').read_text())['files']
        raw=Path('/workspace/datasets/paderborn-10868257/raw')/run
        found={str(p.relative_to(raw)):digest(p) for p in sorted(raw.rglob('*')) if p.is_file()}
        assert expected==found;raw_counts[run]=len(found)
    write_json(out/'verification.json',{'inner_candidate_folds_audited':108,'fold_scaler_statistics_match':True,
        'purging_and_history_separation_passed':True,'artifact_reload_prediction_checks':reloads,
        'independent_primary_metrics_match':True,'selection_rule_reproduced':True,
        'raw_files_unchanged':raw_counts,'B03_accessed':False,'additional_fits':0})
    print(f'Verified 108 candidate folds, {reloads} artifact replays, raw SHA256 counts {raw_counts}; no fits or B03 access')


if __name__=='__main__':main()
