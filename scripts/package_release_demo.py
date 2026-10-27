"""Build the compact attributed demo from verified development outputs only."""
import argparse
from pathlib import Path
import shutil
from factoryguard.release.campaign import read,write
from factoryguard.release.context import reference
from factoryguard.models.forecast import load_table,digest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();root=Path(a.results);out=Path(a.output)
    if out.exists():raise ValueError('Fresh demo directory required')
    cfg=read(root/'frozen_config.json');done=read(root/'completion.json');g=read(root/'selection.json')['selected_group']
    artifact=read(root/f'B02_{g}.json')
    if artifact['candidate']['kind'] not in ('persistence','smoothing'):
        raise ValueError('This data-only demo packager requires an inspectable baseline artifact')
    frames={r:load_table(cfg['tables'][r],r,done['table_sha256'][r]) for r in ('B01','B02')}
    out.mkdir(parents=True)
    shutil.copyfile(cfg['tables']['B01'],out/'B01.csv')
    write(out/'reference.json',reference(frames['B02'],'B02'))
    write(out/'artifact.json',{k:v for k,v in artifact.items() if k not in ('artifact_sha256','training_sources')})
    write(out/'manifest.json',{
        'source':'Run-to-failure data set of ball bearings subjected to time-varying load and speed conditions',
        'creator':'Osarenren Kennedy Aimiyekagbon, Paderborn University',
        'doi':'10.5281/zenodo.10868257','record':'https://zenodo.org/records/10868257',
        'license':'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/',
        'citation':'Javanmardi et al. (2024), Remaining Useful Lifetime Estimation of Bearings Operating under Time-Varying Conditions, DOI 10.36001/phme.2024.v8i1.4101',
        'changes':'All 377 B01 recordings reduced to documented burst descriptors and flags; B02 summarized into fixed-bin reference quartiles. No raw waveforms redistributed. No endorsement implied.',
        'evaluation':'B01 out-of-run development selection replay; alpha selected inside B02. This sample is not an independent test.',
        'derived_csv_sha256':digest(out/'B01.csv'),
        'source_feature_sha256':{r:done['table_sha256'][r] for r in frames},
        'reference_sha256':digest(out/'reference.json'),'artifact_sha256':digest(out/'artifact.json'),
        'rows':len(frames['B01']),'B03_accessed':False})
    (out/'ATTRIBUTION.md').write_text(
        '# Attributed derived demonstration\n\n'
        'Source: Osarenren Kennedy Aimiyekagbon, Paderborn University, '
        '[dataset DOI 10.5281/zenodo.10868257](https://doi.org/10.5281/zenodo.10868257), '
        'licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).\n\n'
        'Cite Javanmardi et al. (2024), Remaining Useful Lifetime Estimation of Bearings Operating under '
        'Time-Varying Conditions, DOI 10.36001/phme.2024.v8i1.4101.\n\n'
        'Changes: raw waveforms reduced to centered RMS, crest factor and excess kurtosis; '
        'temperature/context/quality/provenance retained. B01 includes all 377 bursts; B02 is '
        'represented only by development-reference bin aggregates. No raw waveform included, '
        'no failure labels, no endorsement implied. Inspect manifest.json for source hashes and '
        'feature_definitions.md for exact formulas. This is real laboratory data, distinct from '
        'the legacy synthetic run_step1 demonstration.\n',encoding='utf-8')
    print(f'{sum(p.stat().st_size for p in out.iterdir())} bytes packaged')


if __name__=='__main__':main()
