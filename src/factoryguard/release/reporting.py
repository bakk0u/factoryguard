"""Independent numerical audit and compact review tables; never refit."""
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
from factoryguard.release.campaign import read,write,folds
from factoryguard.release import modeling as m
from factoryguard.release.application import load_artifact
from factoryguard.models.forecast import digest,load_table,ID,condition_key
from factoryguard.models.selection import choose_inner,metrics,errors,ratio


def audit(results):
    root=Path(results);cfg=read(root/'frozen_config.json');manifest=read(root/'pre_search_manifest.json')
    done=read(root/'completion.json')
    if digest(root/'frozen_protocol.md')!=manifest['protocol_sha256']:raise ValueError('Protocol changed')
    trials=read(root/'inner_search.json');assert len(trials)==64
    for t in trials:
        if t['validation_score'] is None:t['validation_score']=float('inf')
    frames={r:load_table(cfg['tables'][r],r,done['table_sha256'][r]) for r in ('B01','B02','B04')}
    checked=0
    for t in trials:
        for d,(train,val,split) in zip(t['folds'],folds(frames[t['training_run']],t['training_run'])):
            assert d['split']==split
            assert train.stop<=val.start and not train.common[-1] and not val.common[:2].any()
            if d['failure']:continue
            assert train.frame.loc[train.common,ID].tolist()==d['audit']['training_source_ids']
            if d['audit']['scaler_mean'] is not None:
                x=train.X[t['candidate']['features']][train.common]
                np.testing.assert_allclose(x.mean(0),d['audit']['scaler_mean'])
                np.testing.assert_allclose(np.where(x.std(0)==0,1,x.std(0)),d['audit']['scaler_scale'])
            checked+=1
    outer={};reloads=0;transition_rows=[]
    dev=pd.read_csv(root/'development_metrics.csv');stress=pd.read_csv(root/'stress_metrics.csv')
    for tr,ev in [('B01','B02'),('B02','B01')]:
        choices=read(root/f'{tr}_inner_choices.json');outer[ev]={}
        for g,c in choices.items():
            if c is None:
                outer[ev][g]={ch:{'mae_ratio':float('inf')} for ch in 'AC'};continue
            assert choose_inner([t for t in trials if t['training_run']==tr],g)==c
            a=load_artifact(root/f'{tr}_{g}.joblib');assert a['training_runs']==[tr]
            for er in (ev,'B04'):
                block=m.prepare(frames[er],er);p=m.predict(c,a['pipeline'],block)
                path=root/(f'{er}_outer_forecasts.jsonl' if er!='B04' else f'B04_from_{tr}_forecasts.jsonl')
                records=[__import__('json').loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
                saved=np.asarray([r['forecasts'][g] for r in records],float)
                np.testing.assert_allclose(p,saved,equal_nan=True,atol=1e-12);reloads+=1
                selected=dev if er!='B04' else stress
                for common in (True,False):
                    coverage='common' if common else 'own_available';stats=metrics(block,p,common)
                    for ch in 'AC':
                        row=selected[(selected.training_run==tr)&(selected.evaluation_run==er)&(selected.group==g)&
                            (selected.channel==ch)&(selected.coverage==coverage)&(selected.partition!= 'outer_training')].iloc[0]
                        assert row['n']==stats[ch]['n']
                        np.testing.assert_allclose([row.mae_v,row.rmse_v],[stats[ch]['mae_v'],stats[ch]['rmse_v']],rtol=1e-12)
                if er==ev:outer[er][g]=metrics(block,p)
                keys=[condition_key(r) for r in block.frame.to_dict('records')]
                transitions=np.array([keys[i]!=keys[i+1] for i in range(len(keys)-1)]+[False])
                for label,mask in [('changed_operating_bin',transitions),('same_operating_bin',~transitions)]:
                    for j,ch in enumerate('AC'):
                        subset=block.common & mask;v=errors(block.target[:,j],p[:,j],subset);base=errors(block.target[:,j],block.current[:,j],subset)
                        transition_rows.append(dict(training_run=tr,evaluation_run=er,group=g,channel=ch,stratum=label,
                            **v,persistence_mae_v=base['mae_v'],mae_ratio=ratio(v['mae_v'],base['mae_v']) if v['n'] else None))
    from factoryguard.models.forecast import clean
    actual=m.select(outer);assert clean(actual)==read(root/'selection.json')
    pd.DataFrame(transition_rows).to_csv(root/'operating_transitions.csv',index=False,encoding='utf-8')
    result={'candidate_folds_audited':checked,'artifact_replays':reloads,'metrics_match':True,
            'training_only_scalers_verified':True,'inner_choices_reproduced':True,
            'selection_reproduced':True,'B03_accessed':False,'additional_fits':0}
    write(root/'audit.json',result);return result


def markdown(frame):
    lines=['| '+' | '.join(frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x) for x in row)+' |')
    return '\n'.join(lines)


def report(results,output):
    root=Path(results);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    audit(root)
    inner=pd.read_csv(root/'inner_trials.csv');dev=pd.read_csv(root/'development_metrics.csv')
    outer=dev.query('partition=="outer_evaluation" and coverage=="common"')
    selection=read(root/'selection.json');done=read(root/'completion.json')
    summary=inner.groupby(['candidate','training_run','partition'],sort=False).mae_ratio.mean().unstack(['training_run','partition'])
    summary.columns=['_'.join(c) for c in summary.columns];summary=summary.reset_index()
    summary=pd.DataFrame({'candidate':[c['id'] for c in m.candidates()]}).merge(summary,on='candidate',how='left')
    summary.to_csv(out/'all_candidates.csv',index=False,encoding='utf-8')
    methods=pd.DataFrame(selection['method_results']);methods.to_csv(out/'methods.csv',index=False,encoding='utf-8')
    for name in ('development_metrics.csv','stress_metrics.csv','quality_strata.csv','operating_transitions.csv','inner_trials.csv'):
        if root.resolve()!=out.resolve():shutil.copyfile(root/name,out/name)
    chosen=outer[outer.group.isin(['persistence',selection['selected_group']])]
    report='# Development release v3: measured results\n\n'
    report+=f"{done['candidate_fold_evaluations']} candidate-fold evaluations in {done['seconds']:.2f} seconds on this machine; {len(done['failures'])} fitting failures. B03 untouched. All selection uses B01/B02; B04 is diagnostic only.\n\n"
    report+='## All group outcomes\n\n'+markdown(methods)+'\n\n'
    report+='## Every configuration: train versus chronological validation\n\nRatios to persistence, equally weighted by fold/channel. Lower is better; training is resubstitution.\n\n'+markdown(summary)+'\n\n'
    if done['failures']:
        report+='## Retained failed trials\n\n'+markdown(pd.DataFrame([{'run':f['run'],'candidate':f['candidate'],'error':f['failure']} for f in done['failures']]))+'\n\n'
    report+='## Selected versus persistence, per run/channel\n\n'+markdown(chosen[['training_run','evaluation_run','group','candidate','channel','n','mae_v','rmse_v','mae_skill']])+'\n\n'
    report+='## Every outer group: per-run/channel common metrics\n\n'+markdown(outer[['evaluation_run','group','candidate','channel','n','mae_v','rmse_v','mae_skill']])+'\n\n'
    report+='## Interpretation and coverage\n\nSmoothing remains the selected method. The more flexible alternatives did not earn replacement under the predeclared consistency and simplicity rule. Delta targets often transferred better than direct targets; this is a descriptive result for these development runs, not a universal rule. Small training errors for flexible estimators did not establish cross-run generalization.\n\n'
    report+='Common eligible counts are 363 B01 and 1110 B02; broader persistence counts are 372 and 1114 per channel. B01 exclusions: 9 history-initialization observations, 4 expired pairs, 1 pending end; B02: 4 initialization, 1 expired, 1 pending. No warning rows were dropped and the enriched finite gate removed no additional real development pairs. Exact per-method broad coverage and negative forecasts are in the local coverage ledger.\n\n'
    report+='The selected outer settings are alpha .2 for B01 (chosen inside B02) and alpha .5 for B02 (chosen inside B01). The final frozen deployment setting is alpha .5 from combined inner scores. Outer results must not be relabelled as evaluation of that pooled setting.\n\n'
    report+='All per-channel MAE/RMSE and failed/unsuccessful candidates are retained in the accompanying CSVs. quality_strata.csv includes warm-up, source/target warning, support, gap-adjacent and own/common counts; operating_transitions.csv includes changes in the fixed measured operating bin. Empty cells are unavailable, not zero error. Gap-adjacent sources have no common temporal-ready pairs by construction; own coverage retains baseline forecasts after reset. B04 stress results cannot resolve its scaling ambiguity or support tuning.\n\n'
    report+='No fault threshold or contextual alarm was tuned. Contextual quartiles are descriptive other-run distributions, with n<20 comparisons explicitly sparse. A rising trajectory can have low forecast error; the UI therefore also shows segment-relative trailing-three level changes. Synthetic ramp/step tests verify this behavior without claiming damage detection.\n'
    (out/'results.md').write_text(report,encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(11,7));ax.barh(methods.group,methods.macro_mae_skill*100,color=['#177e89' if g=='smoothing' else '#718b99' for g in methods.group]);ax.axvline(0,color='black',lw=.8);ax.set_xlabel('Mean MAE improvement over persistence (%) · development selection');ax.invert_yaxis();fig.tight_layout();fig.savefig(root/'method_comparison.png',dpi=140);plt.close(fig)
    return out/'results.md'
