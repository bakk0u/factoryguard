"""Run the frozen, bounded selection-v2 experiment; never access B03."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn

from factoryguard.models.forecast import (ID, RUN, TIME, WARM, condition_key, clean,
                                          digest, load_table, write_json)
from factoryguard.models.selection import (GROUPS, INPUTS, TEMPORAL_NAMES, candidates,
    prepare, splits, fit_candidate, predict, metrics, score, choose_inner, select_method)
from factoryguard.pipelines.forecast import fresh


def validate_config(cfg):
    required={'protocol':'selection-v2','development_runs':['B01','B02'],'stress_run':'B04',
              'gap_limit_s':24,'history_bursts':3,'split_fractions':[[.4,.6],[.6,.8],[.8,1.]],
              'ridge_alpha':[100.,10.,1.],'smoothing_alpha':[.8,.5,.2],
              'tree_grid':[{'max_depth':2,'min_samples_leaf':30},{'max_depth':2,'min_samples_leaf':10},
                           {'max_depth':4,'min_samples_leaf':30},{'max_depth':4,'min_samples_leaf':10}],
              'random_state':42,'inner_tie_tolerance':.01,'selection_min_macro_improvement':.02,
              'selection_max_run_ratio':1.,'selection_max_channel_ratio':1.05,'selection_simplicity_tolerance':.02,
              'complexity_order':list(GROUPS)}
    if any(cfg.get(k)!=v for k,v in required.items()) or set(cfg['tables']) != {'B01','B02','B04'}:
        raise ValueError('Configuration differs from frozen selection-v2 protocol')
    if len(candidates(cfg)) != 18:
        raise ValueError('Bounded grid exceeded')


def table_rows(stats, **context):
    return [{**context, 'channel': c, **s, 'mae_skill':1-s['mae_ratio'], 'rmse_skill':1-s['rmse_ratio']} for c,s in stats.items()]


def coverage(block, prediction):
    result={'observations':len(block.frame),'common_pairs':int(block.common.sum()),
            'exclusion_reasons':dict(Counter(block.exclusion)), 'channels':{}}
    for j,c in enumerate('AC'):
        broad=block.arrival & np.isfinite(block.current[:,j]) & np.isfinite(block.target[:,j])
        result['channels'][c]={'broad_persistence_pairs':int(broad.sum()),
            'candidate_available_pairs':int((broad & np.isfinite(prediction[:,j])).sum()),
            'candidate_unavailable_on_broad':int((broad & ~np.isfinite(prediction[:,j])).sum()),
            'negative_forecasts_issued':int((prediction[:,j]<0).sum())}
    return result


def source_support(block):
    return dict(Counter(condition_key(block.frame.iloc[i]) for i in np.flatnonzero(block.common)))


def strata_rows(block, prediction, support, common=True, **context):
    f=block.frame
    warm=f[WARM].to_numpy(bool)
    next_warm=np.r_[warm[1:],False]
    warning=f.get('quality__any_warning',pd.Series(False,index=f.index)).to_numpy(bool)
    support_n=np.array([support.get(condition_key(r),0) for r in f.to_dict('records')])
    rows=[]
    for j,c in enumerate('AC'):
        ranges=f.get(f'quality__{c}_sensor_range_exceeded',pd.Series(False,index=f.index)).to_numpy(bool)
        masks={'all':np.ones(len(f),bool),'source_warmup':warm,'loaded_both':~warm & ~next_warm,
               'warmup_transition':warm != next_warm,'range_warning_either':ranges | np.r_[ranges[1:],False],
               'local_warning_either':warning | np.r_[warning[1:],False],
               'gap_adjacent':block.gaps>24,'supported':support_n>=20,
               'sparse':(support_n>0)&(support_n<20),'unseen':support_n==0}
        for name,mask in masks.items():
            from factoryguard.models.selection import errors, ratio
            base=block.common if common else block.arrival & np.isfinite(block.current[:,j]) & np.isfinite(block.target[:,j]) & np.isfinite(prediction[:,j])
            subset=base & mask
            a=errors(block.target[:,j],prediction[:,j],subset)
            b=errors(block.target[:,j],block.current[:,j],subset)
            rows.append({**context,'channel':c,'stratum':name,**a,'persistence_mae_v':b['mae_v'],
                         'persistence_rmse_v':b['rmse_v'],'mae_ratio':ratio(a['mae_v'],b['mae_v']) if a['n'] else None,
                         'coverage':'common' if common else 'own_available',
                         'context_interpretation_unresolved':block.run=='B04'})
    return rows


def ledger(block, forecasts, path, support):
    """Every source row, including expired/pending, retains original observation/flags."""
    with Path(path).open('w', encoding='utf-8') as stream:
        for i,row in enumerate(block.frame.to_dict('records')):
            source={'run':block.run,'source_index':block.start+i,'source_id':row[ID],
                    'observation':row,'target_id':None if i==len(block.frame)-1 else int(block.frame.iloc[i+1][ID]),
                    'observed_target':block.target[i],'target_interval_s':block.target_interval[i],
                    'common_pair':bool(block.common[i]),'common_exclusion':block.exclusion[i],
                    'history_start_index':int(block.history_start[i]),'history_ready':bool(block.history_ready[i]),
                    'training_bin_count':support.get(condition_key(row),0),
                    'context_interpretation_unresolved':block.run=='B04',
                    'forecasts':{g:p[i] for g,p in forecasts.items()}}
            stream.write(json.dumps(clean(source),allow_nan=False)+'\n')


def run(config_path, output):
    cfg=json.loads(Path(config_path).read_text());validate_config(cfg)
    out=fresh(output)
    frames={r:load_table(cfg['tables'][r],r) for r in ('B01','B02')}
    folds={r:splits(frames[r],r,cfg) for r in frames}
    protocol=Path('docs/selection_protocol.md').read_text()
    write_json(out/'frozen_config.json',cfg)
    (out/'frozen_protocol.md').write_text(protocol)
    hashes={r:digest(cfg['tables'][r]) for r in frames}
    write_json(out/'pre_search_manifest.json',{'config_sha256':digest(config_path),
        'protocol_sha256':sha256(protocol.encode()).hexdigest(),'development_table_sha256':hashes,
        'candidates':candidates(cfg),'splits':{r:[s for _,_,s in f] for r,f in folds.items()},
        'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__},
        'B03_accessed':False,'B04_loaded_before_selection':False})
    all_trials,inner_rows,outer_rows,strata,coverages=[],[],[],[],{}
    outer_stats,artifacts,outer_predictions={}, {}, {}
    fit_count=0
    for train_run,test_run in [('B01','B02'),('B02','B01')]:
        trials=[]
        for candidate in candidates(cfg):
            fold_scores,details=[],[]
            for train,val,split in folds[train_run]:
                try:
                    model=fit_candidate(candidate,train,cfg['random_state'])
                    fit_count += int(model is not None)
                    train_stats=metrics(train,predict(candidate,model,train))
                    val_stats=metrics(val,predict(candidate,model,val))
                    fold_scores.append(score(val_stats))
                    detail={'split':split,'training':train_stats,'validation':val_stats,'failure':None,
                            'training_sources':train.frame.loc[train.common,ID].tolist(),
                            'scaler_mean':model.named_steps['scale'].mean_.tolist() if model is not None and 'scale' in model.named_steps else None,
                            'scaler_scale':model.named_steps['scale'].scale_.tolist() if model is not None and 'scale' in model.named_steps else None,
                            'train_coverage':coverage(train,predict(candidate,model,train)),
                            'validation_coverage':coverage(val,predict(candidate,model,val))}
                    for partition,stats in [('training',train_stats),('validation',val_stats)]:
                        inner_rows.extend(table_rows(stats,training_run=train_run,candidate=candidate['id'],group=candidate['group'],fold=split['fold'],partition=partition,params=json.dumps(candidate['params'],sort_keys=True)))
                except (ValueError, FloatingPointError) as exc:
                    fold_scores.append(float('inf'));detail={'split':split,'failure':str(exc)}
                details.append(detail)
            trial={'training_run':train_run,'candidate':candidate,'validation_score':float(np.mean(fold_scores)),
                   'folds':details}
            trials.append(trial);all_trials.append(trial)
        selected={g:choose_inner(trials,g,cfg['inner_tie_tolerance']) for g in GROUPS}
        # Freeze this direction's inner choices before any evaluation-run prediction.
        write_json(out/f'{train_run}_inner_choices.json',selected)
        train=prepare(frames[train_run],train_run);test=prepare(frames[test_run],test_run)
        supports=source_support(train);outer_stats[test_run]={};outer_predictions[test_run]={};artifacts[train_run]={}
        coverages[test_run]={}
        for group,candidate in selected.items():
            model=fit_candidate(candidate,train,cfg['random_state']);fit_count+=int(model is not None)
            artifact={'protocol':'selection-v2','candidate':candidate,'training_run':train_run,
                      'training_source_ids':train.frame.loc[train.common,ID].tolist(),
                      'features':list(INPUTS[:2] if candidate['kind'] in ('persistence','smoothing') else INPUTS if candidate['features']=='current' else TEMPORAL_NAMES),
                      'pipeline':model,'support_counts':supports,'table_sha256':hashes,
                      'config_sha256':digest(config_path)}
            joblib.dump(artifact,out/f'{train_run}_{group}.joblib')
            metadata={k:v for k,v in artifact.items() if k!='pipeline'}
            metadata['artifact_sha256']=digest(out/f'{train_run}_{group}.joblib')
            write_json(out/f'{train_run}_{group}.json',metadata)
            artifacts[train_run][group]=artifact
            p=predict(candidate,model,test);outer_predictions[test_run][group]=p
            for partition,block,pred in [('outer_training',train,predict(candidate,model,train)),('outer_evaluation',test,p)]:
                stats=metrics(block,pred)
                outer_rows.extend(table_rows(stats,training_run=train_run,evaluation_run=block.run,group=group,candidate=candidate['id'],partition=partition,coverage='common'))
                if partition=='outer_evaluation':
                    outer_stats[test_run][group]=stats
                    outer_rows.extend(table_rows(metrics(block,pred,common=False),training_run=train_run,evaluation_run=block.run,group=group,candidate=candidate['id'],partition=partition,coverage='own_available'))
            coverages[test_run][group]=coverage(test,p)
            for common in (True,False):
                strata.extend(strata_rows(test,p,supports,common=common,training_run=train_run,evaluation_run=test_run,group=group))
        ledger(test,outer_predictions[test_run],out/f'{test_run}_outer_forecasts.jsonl',supports)
    selection=select_method(outer_stats,cfg)
    write_json(out/'selection.json',selection)  # selection is locked before B04 is loaded
    write_json(out/'inner_search.json',all_trials)
    pd.DataFrame(inner_rows).to_csv(out/'inner_trials.csv',index=False)
    pd.DataFrame(outer_rows).to_csv(out/'development_metrics.csv',index=False)
    write_json(out/'development_coverage.json',coverages)
    chosen_group=selection['selected_group']
    final_options=[]
    for candidate in candidates(cfg):
        if candidate['group']==chosen_group:
            vals=[t['validation_score'] for t in all_trials if t['candidate']['id']==candidate['id']]
            final_options.append({'candidate':candidate,'validation_score':float(np.mean(vals))})
    final=choose_inner(final_options,chosen_group,cfg['inner_tie_tolerance'])
    write_json(out/'proposed_final_config.json',{'status':'proposal only; pooled fit and B03 evaluation NOT executed',
        'protocol':'selection-v2','candidate':final,'training_runs':['B01','B02'],
        'feature_names':list(INPUTS[:2] if final['kind'] in ('persistence','smoothing') else INPUTS if final['features']=='current' else TEMPORAL_NAMES),
        'gap_limit_s':24,'history_reset':'experiment/gap; three bursts for temporal; smoothing initializes per segment',
        'preprocessing':('none; per-channel observed RMS state, no fitted scaler or imputer' if final['kind'] in ('persistence','smoothing') else 'finite gate and training-only StandardScaler for Ridge inside Pipeline; no imputation'),
        'B03':'sealed; later separate authorization and blind predefined validity pass required',
        'development_config_sha256':digest(config_path)})
    # B04 can neither fit nor select. Report each already frozen outer-fit candidate.
    stress=prepare(load_table(cfg['tables']['B04'],'B04'),'B04')
    stress_rows=[];stress_coverage={}
    for train_run in ('B01','B02'):
        forecasts={};stress_coverage[train_run]={}
        for group,artifact in artifacts[train_run].items():
            p=predict(artifact['candidate'],artifact['pipeline'],stress);forecasts[group]=p
            stress_rows.extend(table_rows(metrics(stress,p),training_run=train_run,evaluation_run='B04',group=group,candidate=artifact['candidate']['id'],partition='post_selection_stress',coverage='common'))
            stress_rows.extend(table_rows(metrics(stress,p,False),training_run=train_run,evaluation_run='B04',group=group,candidate=artifact['candidate']['id'],partition='post_selection_stress',coverage='own_available'))
            stress_coverage[train_run][group]=coverage(stress,p)
            for common in (True,False):
                strata.extend(strata_rows(stress,p,artifact['support_counts'],common=common,training_run=train_run,evaluation_run='B04',group=group))
        ledger(stress,forecasts,out/f'B04_from_{train_run}_forecasts.jsonl',source_support(prepare(frames[train_run],train_run)))
    pd.DataFrame(stress_rows).to_csv(out/'stress_metrics.csv',index=False)
    pd.DataFrame(strata).to_csv(out/'quality_strata.csv',index=False)
    write_json(out/'stress_coverage.json',stress_coverage)
    if fit_count!=92:
        raise ValueError(f'Unexpected learned pipeline fit count {fit_count}; inspect failed trials')
    for r,h in hashes.items():
        if digest(cfg['tables'][r])!=h: raise ValueError('Source feature table changed')
    write_json(out/'completion.json',{'candidate_fold_evaluations':108,'learned_pipeline_fits':fit_count,
        'selected_group':chosen_group,'B03_accessed':False,'B04_loaded_after_selection':True,
        'pooled_final_fit_executed':False,'source_table_sha256':{**hashes,'B04':digest(cfg['tables']['B04'])}})
    print(json.dumps(selection,indent=2));print(f'Outputs: {out}')
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='configs/selection_v2.json')
    parser.add_argument('--output',required=True)
    args=parser.parse_args();run(args.config,args.output)


if __name__=='__main__': main()
