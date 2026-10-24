"""Render frozen selection outputs; no fitting, searching or raw-data IO."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def markdown_table(frame):
    columns=list(frame.columns)
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(str(v) for v in row)+' |')
    return '\n'.join(lines)


def report(result_dir,document=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    root=Path(result_dir)
    decision=json.loads((root/'selection.json').read_text())
    inner=pd.read_csv(root/'inner_trials.csv');dev=pd.read_csv(root/'development_metrics.csv');stress=pd.read_csv(root/'stress_metrics.csv')
    comparisons=pd.DataFrame([{k:r[k] for k in ('group','macro_mae_ratio','macro_mae_skill','qualified')} for r in decision['method_results']])
    comparisons.to_csv(root/'method_comparison.csv',index=False)
    trials=inner.groupby(['candidate','group','training_run','partition'],sort=False).mae_ratio.mean().unstack(['training_run','partition'])
    trials.columns=['_'.join(col) for col in trials.columns];trials=trials.reset_index()
    trials.to_csv(root/'all_candidate_summary.csv',index=False)
    # Every grid trial, with train/chronological-validation results and no omitted losses.
    fig,axes=plt.subplots(1,2,figsize=(15,9),sharey=True)
    for ax,run in zip(axes,('B01','B02')):
        part=inner.query('training_run==@run').groupby(['candidate','partition'],sort=False).mae_ratio.mean().unstack()
        y=np.arange(len(part));ax.scatter(part.training,y,label='Training diagnostic',color='#007d79',s=25)
        ax.scatter(part.validation,y,label='Chronological validation',color='#7553c8',s=35,marker='x')
        ax.axvline(1,color='#b56d09',linestyle='--');ax.set_yticks(y,part.index,fontsize=8);ax.invert_yaxis()
        ax.set_title(f'Tune within {run} only · all 18 configurations');ax.set_xlabel('Mean MAE / persistence MAE (3 folds × 2 channels)');ax.grid(alpha=.15);ax.legend(fontsize=8)
    fig.suptitle('Training versus chronological validation · ratios below 1 beat persistence\nDependent bursts; no population confidence claim')
    fig.tight_layout();fig.savefig(root/'inner_train_validation.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,5))
    groups=comparisons.group.tolist();x=np.arange(len(groups));width=.36
    for offset,run,color in [(-width/2,'B01','#007d79'),(width/2,'B02','#7553c8')]:
        vals=[]
        for group in groups:
            part=dev.query('evaluation_run==@run and group==@group and partition=="outer_evaluation" and coverage=="common"')
            vals.append(100*(1-part.mae_ratio.mean()))
        ax.bar(x+offset,vals,width,label=f'{run} selection result',color=color)
    ax.axhline(0,color='#475569',lw=1);ax.set_xticks(x,groups,rotation=15,ha='right');ax.set_ylabel('Mean channel MAE improvement over persistence (%)')
    ax.set_title('Out-of-run development selection · common n=363 (B01), 1110 (B02)\nAll methods retained; these results selected the method');ax.legend();ax.grid(axis='y',alpha=.15)
    fig.tight_layout();fig.savefig(root/'development_comparison.png',dpi=140);plt.close(fig)
    group=decision['selected_group']
    for run in ('B01','B02','B04'):
        records=[json.loads(line) for line in (root/(f'{run}_outer_forecasts.jsonl' if run!='B04' else 'B04_from_B02_forecasts.jsonl')).read_text().splitlines()]
        t=pd.to_datetime([r['observation']['provenance__source_time'] for r in records],format='%d-%b-%Y %H:%M:%S')
        x=np.asarray((t-t[0]).total_seconds()/60)
        gap=np.r_[False,np.diff(x)*60>24]
        fig,axes=plt.subplots(3,1,figsize=(14,9),sharex=True)
        def broken(values):
            xx=[];yy=[]
            for i,v in enumerate(values):
                if gap[i]:xx.append(np.nan);yy.append(np.nan)
                xx.append(x[i]);yy.append(v)
            return xx,yy
        for j,c in enumerate('AC'):
            obs=np.array([r['observation'][f'feature__{c}_ac_rms_v'] for r in records])
            axes[j].plot(*broken(obs),color='#007d79',lw=1,label='Observed RMS')
            for method,color in [(group,'#7553c8'),('persistence','#b56d09')]:
                pred=np.full(len(x),np.nan)
                for i in range(1,len(x)):
                    if not gap[i]:pred[i]=records[i-1]['forecasts'][method][j]
                axes[j].plot(*broken(pred),color=color,alpha=.8,lw=.8,label=method)
                axes[2].plot(*broken(obs-pred),color=color,alpha=.65,lw=.7,ls='-' if j==0 else '--',label=f'{c} {method}')
            warm=np.array([r['observation']['quality__documented_warmup_setpoints'] for r in records],bool)
            ranges=np.array([r['observation'][f'quality__{c}_sensor_range_exceeded'] for r in records],bool)
            axes[j].scatter(x[warm],obs[warm],s=9,color='#1679aa',label='Warm-up setpoints')
            axes[j].scatter(x[ranges],obs[ranges],s=35,facecolors='none',edgecolors='#b56d09',label='Sensor range')
            axes[j].set_ylabel(f'{c} RMS (V)');axes[j].legend(ncol=5,fontsize=8)
        axes[2].set_ylabel('Observed − forecast (V)');axes[2].legend(ncol=4,fontsize=8)
        for ax in axes:
            for xx in x[gap]:ax.axvline(xx,color='#b73538',ls=':',alpha=.6)
            ax.grid(alpha=.15)
        axes[-1].set_xlabel('Minutes from first provisional CSV clock; not operating time')
        fig.suptitle(f'{run} · {group} and persistence · '+('post-selection stress; context unresolved' if run=='B04' else 'development selection result')+'\nAll available forecasts shown; selection metrics use the smaller common-history intersection')
        fig.tight_layout();fig.savefig(root/f'{run}_selected_history.png',dpi=140);plt.close(fig)
    if document:
        table=dev.query('partition=="outer_evaluation" and coverage=="common"').copy()
        table['MAE / RMSE (V)']=table.apply(lambda r:f'{r.mae_v:.6f} / {r.rmse_v:.6f}',axis=1)
        table['MAE skill']=table.mae_skill.map(lambda v:f'{100*v:+.2f}%')
        table=table[['training_run','evaluation_run','group','candidate','channel','n','MAE / RMSE (V)','MAE skill']]
        inner_table=trials.copy()
        for c in inner_table.columns[2:]:inner_table[c]=inner_table[c].map(lambda v:f'{v:.6f}')
        stress_table=stress.query('coverage=="common"').copy()
        stress_table['MAE / RMSE (V)']=stress_table.apply(lambda r:f'{r.mae_v:.6f} / {r.rmse_v:.6f}',axis=1)
        stress_table['MAE skill']=stress_table.mae_skill.map(lambda v:f'{100*v:+.2f}%')
        text='# Selection-v2: complete candidate results\n\nGenerated from `'+str(root)+'`; no fitting occurs in this report command. These are development **selection** results, not unbiased final performance. The frozen protocol is in selection_protocol.md; explanation and conclusions are in model_selection_explained.md.\n\n'
        text+='## All 18 candidate configurations\n\nEach value is the mean MAE/persistence-MAE ratio, with equal weights for three chronological folds and two channels. Training values are diagnostics; validation values alone choose settings inside that run. All 108 candidate-fold evaluations completed without a failure. Smaller is better; 1 is persistence.\n\n'+markdown_table(inner_table)+'\n\n'
        text+='## Outer development selection, common pairs\n\nB01→B02 and B02→B01. Each group uses its inner-selected settings only. Common n=363/1110 for B01/B02; all methods use the same pairs. Broad persistence n=372/1114 is retained separately in development_metrics.csv (own_available).\n\n'+markdown_table(table)+'\n\n'
        text+='## Post-selection B04 diagnostic\n\nB04 was first loaded after selection.json was written. No B04 result changes selection or settings. Two separately frozen outer artifacts are shown; do not choose a preferred B04 variant from this table. Common n=1111; broad persistence n=1113. Reported context scaling remains unresolved, with no corrections.\n\n'+markdown_table(stress_table[['training_run','group','candidate','channel','n','MAE / RMSE (V)','MAE skill']])+'\n\n'
        text+='## Further outputs\n\n`inner_search.json` retains split indices, source IDs, fold-local scaler statistics, train/validation metrics, coverage and failures for every trial. `development_metrics.csv` also includes full outer-training diagnostics and own-available metrics. `quality_strata.csv` includes common and own-available coverage, including sparse/unseen bins and range warnings. Prediction ledgers preserve every original observation/flag and each exclusion. Empty strata are missing-valued, not zero error. No B03 data was accessed.\n'
        Path(document).write_text(text)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',required=True);p.add_argument('--document');a=p.parse_args();report(a.results,a.document)
