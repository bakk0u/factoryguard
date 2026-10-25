"""Bounded, recorded development campaign and frozen final release artifact."""
from collections import Counter
from pathlib import Path
import importlib.metadata
import json
import platform
import time

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from factoryguard.models.forecast import ID, INPUTS, digest, load_table, clean
from factoryguard.models.selection import metrics, score, choose_inner
from factoryguard.pipelines.forecast import fresh
from factoryguard.pipelines.select_forecast import coverage, source_support, strata_rows, table_rows, ledger
from factoryguard.release import modeling as m


def write(path, value):
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n', encoding='utf-8')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def folds(frame, run):
    out = []
    for i, (a,b) in enumerate(((.4,.6),(.6,.8),(.8,1.))):
        n, end = int(len(frame)*a), int(len(frame)*b)
        out.append((m.prepare(frame,run,0,n), m.prepare(frame,run,n,end),
                    dict(fold=i, train_stop=n, validation_stop=end, purged_source=n-1,
                         validation_history_start=n, earliest_common_source=n+2)))
    return out


def audit_fit(model, block):
    return dict(training_source_ids=block.frame.loc[block.common,ID].tolist(),
                scaler_mean=(model.named_steps['scale'].mean_.tolist()
                             if model is not None and 'scale' in model.named_steps else None),
                scaler_scale=(model.named_steps['scale'].scale_.tolist()
                              if model is not None and 'scale' in model.named_steps else None))


def artifact(candidate, pipeline, blocks, config_hash):
    return dict(protocol='release-v3', candidate=candidate, pipeline=pipeline,
                training_runs=[b.run for b in blocks],
                training_sources={b.run:b.frame.loc[b.common,ID].tolist() for b in blocks},
                features=list(INPUTS[:2] if candidate['kind'] in ('persistence','smoothing')
                              else INPUTS if candidate['features']=='current' else m.ENRICHED),
                config_sha256=config_hash, gap_limit_s=24)


def save_artifact(path, a):
    joblib.dump(a,path)
    write(path.with_suffix('.json'), {k:v for k,v in a.items() if k!='pipeline'} |
          {'artifact_sha256':digest(path)})


def run(config_path, output):
    cfg=read(config_path)
    if (cfg['protocol']!='release-v3' or cfg['development_runs']!=['B01','B02']
        or cfg['stress_run']!='B04' or set(cfg['tables'])!={'B01','B02','B04'}
        or cfg['gap_limit_s']!=24 or cfg['expected_candidates']!=32
        or cfg['split_fractions']!=[[.4,.6],[.6,.8],[.8,1.]]
        or cfg['random_state']!=42 or cfg['budget_seconds']!=1800):
        raise ValueError('Not the frozen v3 protocol')
    out=fresh(output); started=time.monotonic()
    frames={r:load_table(cfg['tables'][r],r) for r in ('B01','B02')}
    splits={r:folds(f,r) for r,f in frames.items()}
    cs=m.candidates(); assert len(cs)==32
    protocol=Path('docs/release_protocol.md').read_text(encoding='utf-8')
    (out/'frozen_protocol.md').write_text(protocol,encoding='utf-8');write(out/'frozen_config.json',cfg)
    hashes={r:digest(cfg['tables'][r]) for r in frames}
    versions={p:importlib.metadata.version(p) for p in ('numpy','pandas','scipy','scikit-learn','joblib')}
    try: versions['xgboost-cpu']=importlib.metadata.version('xgboost-cpu')
    except importlib.metadata.PackageNotFoundError: versions['xgboost-cpu']='unavailable'
    write(out/'pre_search_manifest.json',dict(config_sha256=digest(config_path),
          protocol_sha256=digest(out/'frozen_protocol.md'),table_sha256=hashes,candidates=cs,
          splits={r:[s for _,_,s in fs] for r,fs in splits.items()},versions=versions,
          python=platform.python_version(), B03_accessed=False,
          source_sha256={p.relative_to(Path(__file__).parents[1]).as_posix():digest(p)
                         for p in Path(__file__).parents[1].rglob('*.py')}))
    trials=[]; rows=[]; inner_rows=[]; strata=[]; outer={}; artifacts={}; cov={}
    with threadpool_limits(limits=1):
        for train_run,eval_run in (('B01','B02'),('B02','B01')):
            run_trials=[]
            for candidate in cs:
                scores=[]; details=[]
                for train,val,split in splits[train_run]:
                    if time.monotonic()-started>cfg['budget_seconds']:
                        write(out/'aborted.json',{'reason':'predeclared compute budget exceeded'})
                        raise RuntimeError('Campaign aborted; partial trials retained, no selection')
                    tick=time.monotonic()
                    try:
                        model=m.fit(candidate,[train]); tp=m.predict(candidate,model,train); vp=m.predict(candidate,model,val)
                        ts,vs=metrics(train,tp),metrics(val,vp); scores.append(score(vs))
                        details.append(dict(split=split,training=ts,validation=vs,failure=None,
                            audit=audit_fit(model,train),train_coverage=coverage(train,tp),
                            validation_coverage=coverage(val,vp),seconds=time.monotonic()-tick))
                        for partition,stats in (('training',ts),('validation',vs)):
                            inner_rows.extend(table_rows(stats,training_run=train_run,candidate=candidate['id'],
                                  group=candidate['group'],fold=split['fold'],partition=partition))
                    except (ValueError,ImportError,RuntimeError) as exc:
                        scores.append(float('inf'));details.append(dict(split=split,failure=str(exc)))
                trial=dict(training_run=train_run,candidate=candidate,validation_score=float(np.mean(scores)),folds=details)
                run_trials.append(trial);trials.append(trial)
                write(out/'inner_search.json',trials)
                print(f'{train_run} {candidate["id"]}: inner ratio {trial["validation_score"]:.4f}',flush=True)
            choices={}
            for g in m.groups():
                try: choices[g]=choose_inner(run_trials,g)
                except ValueError: choices[g]=None
            write(out/f'{train_run}_inner_choices.json',choices)
            train=m.prepare(frames[train_run],train_run); test=m.prepare(frames[eval_run],eval_run)
            support=source_support(train); forecasts={};outer[eval_run]={};artifacts[train_run]={};cov[eval_run]={}
            for group,c in choices.items():
                if c is None:
                    outer[eval_run][group]={ch:{'mae_ratio':float('inf')} for ch in 'AC'}
                    continue
                model=m.fit(c,[train]); a=artifact(c,model,[train],digest(config_path))
                save_artifact(out/f'{train_run}_{group}.joblib',a); artifacts[train_run][group]=a
                p=m.predict(c,model,test);forecasts[group]=p;outer[eval_run][group]=metrics(test,p)
                # Reload is tested on actual evaluated features, never a different fitted model.
                reloaded=joblib.load(out/f'{train_run}_{group}.joblib')
                np.testing.assert_allclose(p,m.predict(c,reloaded['pipeline'],test),equal_nan=True)
                for part,b,pred in (('outer_training',train,m.predict(c,model,train)),('outer_evaluation',test,p)):
                    for common in (True,False):
                        rows.extend(table_rows(metrics(b,pred,common),training_run=train_run,evaluation_run=b.run,
                            group=group,candidate=c['id'],partition=part,coverage='common' if common else 'own_available'))
                cov[eval_run][group]=coverage(test,p)
                for common in (True,False):
                    strata.extend(strata_rows(test,p,support,common,training_run=train_run,evaluation_run=eval_run,group=group))
            ledger(test,forecasts,out/f'{eval_run}_outer_forecasts.jsonl',support)
        selection=m.select(outer);write(out/'selection.json',selection)
        pd.DataFrame(inner_rows).to_csv(out/'inner_trials.csv',index=False,encoding='utf-8')
        pd.DataFrame(rows).to_csv(out/'development_metrics.csv',index=False,encoding='utf-8')
        write(out/'development_coverage.json',cov)
        group=selection['selected_group'];options=[]
        for c in cs:
            if c['group']==group:
                options.append(dict(candidate=c,validation_score=float(np.mean([
                    t['validation_score'] for t in trials if t['candidate']['id']==c['id']]))))
        final=choose_inner(options,group)
        blocks=[m.prepare(frames[r],r) for r in ('B01','B02')]
        final_artifact=artifact(final,m.fit(final,blocks),blocks,digest(config_path))
        save_artifact(out/'final.joblib',final_artifact)
        # B04 begins only here, after all selection and final settings are fixed.
        stress=m.prepare(load_table(cfg['tables']['B04'],'B04'),'B04');stress_rows=[]
        for tr,group_artifacts in artifacts.items():
            forecasts={}
            for g,a in group_artifacts.items():
                p=m.predict(a['candidate'],a['pipeline'],stress);forecasts[g]=p
                for common in (True,False):
                    stress_rows.extend(table_rows(metrics(stress,p,common),training_run=tr,evaluation_run='B04',group=g,
                       candidate=a['candidate']['id'],partition='stress',coverage='common' if common else 'own_available'))
                    strata.extend(strata_rows(stress,p,source_support(m.prepare(frames[tr],tr)),common,
                                  training_run=tr,evaluation_run='B04',group=g))
            ledger(stress,forecasts,out/f'B04_from_{tr}_forecasts.jsonl',source_support(m.prepare(frames[tr],tr)))
        pd.DataFrame(stress_rows).to_csv(out/'stress_metrics.csv',index=False,encoding='utf-8')
        pd.DataFrame(strata).to_csv(out/'quality_strata.csv',index=False,encoding='utf-8')
    for r,h in hashes.items():
        if digest(cfg['tables'][r])!=h: raise ValueError('Development table changed')
    write(out/'completion.json',dict(candidate_fold_evaluations=sum(len(t['folds']) for t in trials),
        failures=[dict(candidate=t['candidate']['id'],run=t['training_run'],**d) for t in trials for d in t['folds'] if d['failure']],
        seconds=time.monotonic()-started, B03_accessed=False, final_candidate=final,
        table_sha256={**hashes,'B04':digest(cfg['tables']['B04'])}))
    return out
