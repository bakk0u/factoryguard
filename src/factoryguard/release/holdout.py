"""Prepare a sealed plan; actual reserve execution requires later explicit approval.

Default CLI only shows the frozen procedure. Never run --execute in release-v3.
"""
import argparse
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import json
import shutil

import numpy as np
import pandas as pd

from factoryguard.release.campaign import read,write
from factoryguard.models.forecast import digest,_validate_frame_fields,condition_key
from factoryguard.models.selection import _prepare_validated,metrics,errors,ratio
from factoryguard.release import modeling as m
from factoryguard.pipelines.forecast import fresh

CHECKS=('review_complete','independent_documentation_review','units_volts_10g_per_v_0db',
        'documented_128khz_1p6s','warmup_and_command_ranges_match_frozen_policy',
        'ordinal_alignment_and_clock_limits_accepted','termination_not_used_as_label',
        'no_feature_or_outcome_inspection_for_model_selection')


def code_hashes():
    from factoryguard import release
    base=Path(release.__file__).parents[1]
    names=['data/paderborn.py','features/b01.py','pipelines/features_paderborn.py',
           'models/forecast.py','models/selection.py','release/modeling.py','release/holdout.py']
    return {n:digest(base/n) for n in names}


def freeze(results,output):
    root=Path(results);out=fresh(output)
    meta=read(root/'final.json')
    # Selected artifact is an inspectable state rule, requiring no pickle at reserve execution.
    if meta['candidate']['kind'] not in ('persistence','smoothing'):
        raise ValueError('Review a new reserve implementation before freezing a learned final method')
    plan={'protocol':'release-v3-reserve','status':'prepared; NOT executed on B03',
          'reserve_run':'B03','expected_bursts':614,'candidate':meta['candidate'],
          'development_runs':['B01','B02'],'gap_limit_s':24,'sample_rate_hz':128000,
          'samples_per_burst':204800,'published_archive_md5':'6c16eaa8d837b31da69fab1675521ddb',
          'primary':'common per-channel MAE/RMSE and skill versus persistence; equal-channel macro ratio',
          'secondary':'broad available coverage; quality/warm-up/gap/operating transitions/support strata',
          'validity_policy':'any inventory/grid/finite/meaning/checksum failure makes entire run unevaluable; retain range warnings',
          'missing_policy':'common finite 27-feature history intersection; baseline broader finite RMS pairs separately',
          'final_artifact_sha256':digest(root/'final.joblib'),
          'search_manifest_sha256':digest(root/'pre_search_manifest.json'),
          'required_attestations':list(CHECKS),'implementation_sha256':code_hashes()}
    cfg=read(root/'frozen_config.json');done=read(root/'completion.json');counts=Counter()
    from factoryguard.models.forecast import load_table
    from factoryguard.pipelines.select_forecast import source_support
    for r in ('B01','B02'):counts.update(source_support(m.prepare(load_table(cfg['tables'][r],r,done['table_sha256'][r]),r)))
    plan['development_support_counts']=dict(counts)
    write(out/'plan.json',plan)
    write(out/'attestation.template.json',{'reviewer':'REQUIRED','authorization':'REQUIRED after pipeline review',
         'documentation_evidence':'REQUIRED: per-run log pages and interpretation, no trend-driven corrections',
         'plan_sha256':digest(out/'plan.json'),**{k:False for k in CHECKS}})
    return out/'plan.json'


def gate(plan_path,attestation_path,approved):
    # Approval is checked before even looking at supplied attestation/raw paths.
    if not approved:raise ValueError('B03 remains sealed; later explicit review approval is required')
    plan=read(plan_path);a=read(attestation_path)
    if plan['implementation_sha256']!=code_hashes():raise ValueError('Frozen implementation changed; stop before reserve access')
    if (plan['protocol']!='release-v3-reserve' or plan['reserve_run']!='B03'
        or a.get('plan_sha256')!=digest(plan_path) or any(a.get(k) is not True for k in CHECKS)
        or any(not a.get(k) or str(a[k]).startswith('REQUIRED') for k in ('reviewer','authorization','documentation_evidence'))):
        raise ValueError('Blinded measurement-meaning review incomplete or plan mismatch')
    return plan


def execute(plan_path,attestation_path,raw_root,archive,output,*,approved=False):
    plan=gate(plan_path,attestation_path,approved)
    raw=Path(raw_root).resolve();out=Path(output).resolve()
    if out==raw or raw in out.parents:raise ValueError('Output must be outside raw storage')
    out=fresh(out)
    # A failed gate or structural validation is terminal, not a prompt to modify rules.
    write(out/'attempt.json',{'plan_sha256':digest(plan_path),'status':'started; no refitting permitted'})
    from hashlib import md5
    from factoryguard.data.paderborn import _read_recording,load_table,TEMPERATURE_COLUMNS,OPERATING_COLUMNS
    from factoryguard.pipelines.features_paderborn import raw_manifest,burst_rows
    from factoryguard.pipelines.select_forecast import coverage,strata_rows
    try:
        h=md5()
        with Path(archive).open('rb') as stream:
            for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
        if h.hexdigest()!=plan['published_archive_md5']:raise ValueError('Archive checksum mismatch')
        # Validate extracted bytes against archive contents before measurement processing.
        import zipfile,zlib
        with zipfile.ZipFile(archive) as z:
            members={i.filename:i for i in z.infolist() if not i.is_dir()}
            actual={p.relative_to(raw).as_posix():p for p in raw.rglob('*') if p.is_file()}
            # Published archives may carry a top-level run directory.
            if all(k.startswith('B03/') for k in members):members={k[4:]:v for k,v in members.items()}
            if set(members)!=set(actual):raise ValueError('Raw inventory differs from verified archive')
            for name,path in actual.items():
                crc=0;size=0
                if path.is_symlink():raise ValueError('Raw link refused')
                with path.open('rb') as stream:
                    for part in iter(lambda:stream.read(1024*1024),b''):crc=zlib.crc32(part,crc);size+=len(part)
                if size!=members[name].file_size or crc!=members[name].CRC:raise ValueError('Extracted raw checksum differs')
        before=raw_manifest(raw);n=plan['expected_bursts']
        temps=load_table(raw/'B03_meanTemperatures.csv',TEMPERATURE_COLUMNS)
        operating=load_table(raw/'B03_operatingConditions.csv',OPERATING_COLUMNS)
        if len(temps)!=n or not temps.source_time.equals(operating.source_time):raise ValueError('Reserve CSV count/alignment mismatch')
        paths=tuple(raw/'vibrationData'/f'data_B03_M{i:04d}.mat' for i in range(1,n+1))
        if set(paths)!=set((raw/'vibrationData').iterdir()):raise ValueError('Reserve waveform inventory mismatch')
        experiment=SimpleNamespace(root=raw,experiment='B03',temperatures=temps,operating=operating,paths=paths)
        def loader(path,*,experiment):return _read_recording(path,experiment)
        # One waveform at a time. No plotting or model choices between validation and scoring.
        frame=pd.DataFrame(burst_rows(experiment,before,record_loader=loader))
        if raw_manifest(raw)!=before:raise ValueError('Raw files changed during reserve extraction')
        _validate_frame_fields(frame,'B03');block=m.enrich(_prepare_validated(frame,'B03'))
        prediction=m.predict(plan['candidate'],None,block)
        baseline=m.predict(m.candidates()[0],None,block)
        frame.to_csv(out/'features.csv',index=False,encoding='utf-8')
        np.savez(out/'forecasts.npz',selected=prediction,persistence=baseline,target=block.target,common=block.common)
        rows=[]
        for g,pred in [('selected',prediction),('persistence',baseline)]:
            for common in (True,False):rows.extend(strata_rows(block,pred,plan['development_support_counts'],common,
                       training_run='B01+B02',evaluation_run='B03',group=g))
        pd.DataFrame(rows).to_csv(out/'quality_strata.csv',index=False,encoding='utf-8')
        keys=[condition_key(r) for r in frame.to_dict('records')]
        changed=np.array([keys[i]!=keys[i+1] for i in range(len(keys)-1)]+[False])
        transitions=[]
        for label,mask in [('changed_operating_bin',changed),('same_operating_bin',~changed)]:
            for j,ch in enumerate('AC'):
                subset=block.common & mask
                value=errors(block.target[:,j],prediction[:,j],subset)
                base=errors(block.target[:,j],baseline[:,j],subset)
                transitions.append({'stratum':label,'channel':ch,**value,'persistence_mae_v':base['mae_v'],
                    'mae_ratio':ratio(value['mae_v'],base['mae_v']) if value['n'] else None})
        pd.DataFrame(transitions).to_csv(out/'operating_transitions.csv',index=False,encoding='utf-8')
        selected_metrics=metrics(block,prediction)
        write(out/'result.json',{'status':'completed one reserve case study','plan_sha256':digest(plan_path),
              'selected_common':selected_metrics,'persistence_common':metrics(block,baseline),
              'equal_channel_macro_mae_ratio':float(np.mean([selected_metrics[c]['mae_ratio'] for c in 'AC'])),
              'selected_broad':metrics(block,prediction,False),'persistence_broad':metrics(block,baseline,False),
              'coverage':coverage(block,prediction),'raw_unchanged':True,'raw_sha256':before,
              'labels_created':False,'fitting_performed':False,'limitation':'One bearing is one laboratory case, not population/fault/RUL validation.'})
    except Exception as exc:
        write(out/'not_evaluable.json',{'reason':str(exc),'policy':'Do not change the frozen method/rules or substitute another run.'})
        raise
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True)
    p.add_argument('--execute-after-review-approval',action='store_true')
    p.add_argument('--attestation');p.add_argument('--raw-root');p.add_argument('--archive');p.add_argument('--output')
    a=p.parse_args()
    if not a.execute_after_review_approval:
        print(json.dumps(read(a.plan),indent=2));print('DRY RUN: no B03 path accessed.');return
    if not all((a.attestation,a.raw_root,a.archive,a.output)):p.error('Execution requires attestation, raw root, verified archive and fresh output')
    print(execute(a.plan,a.attestation,a.raw_root,a.archive,a.output,approved=True))


if __name__=='__main__':main()
