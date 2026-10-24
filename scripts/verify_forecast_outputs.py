"""Independent numerical/output audit; read-only checks of explicit development raw paths."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from factoryguard.models.forecast import digest, load_artifact, write_json


def main():
    root = Path('reports/local/forecast-v1')
    artifact = load_artifact(root/'model/model.json')
    summary = json.loads((root/'evaluation/summary.json').read_text())
    checks = {}
    locations = {
        'B01': Path('reports/local/b01-features-v1'),
        'B02': Path('reports/local/development-assessment-20261023-final/B02'),
        'B04': Path('reports/local/development-assessment-20261023-final/B04'),
    }
    for run, directory in locations.items():
        source = Path(artifact['config']['tables'][run])
        assert digest(source) == artifact['table_sha256'][run]
        table = pd.read_csv(source)
        ledger = [json.loads(line) for line in (root/f'evaluation/{run}.forecasts.jsonl').read_text().splitlines()]
        assert len(ledger) == len(table)
        assert ledger[-1]['status'] == 'pending'
        expected = {'B01': (372,4), 'B02': (1114,1), 'B04': (1113,0)}[run]
        assert (summary[run]['eligible'], summary[run]['expired']) == expected
        for j, channel in enumerate('AC'):
            eligible = [r for r in ledger if r['status']=='eligible']
            for model in ('persistence','ridge'):
                err=np.array([r['observed'][j]-r[model][j] for r in eligible])
                stats=summary[run]['channels'][channel]['all'][model]
                np.testing.assert_allclose([stats['mae_v'],stats['rmse_v']], [np.abs(err).mean(),np.sqrt((err*err).mean())],rtol=1e-13)
        baseline=json.loads((directory/'raw_integrity.json').read_text())['files']
        raw=Path('/workspace/datasets/paderborn-10868257/raw')/run
        # No parent traversal or held-out source access. Exact development inventories only.
        actual={str(p.relative_to(raw)):digest(p) for p in sorted(raw.rglob('*')) if p.is_file()}
        assert actual == baseline, f'{run} raw checksum mismatch'
        checks[run]={'unchanged_raw_files':len(actual),'feature_table_sha256':digest(source),
                     'eligible':expected[0],'expired':expected[1],'pending':1,'metrics_independently_recomputed':True}
    # Training preprocessing and coefficients against direct independent matrix calculation.
    t=pd.read_csv(artifact['config']['tables']['B02'])
    columns=artifact['config']['inputs']
    ids=set(artifact['training_source_ids'])
    source=t[t.provenance__measurement_id.isin(ids)]
    x=source[columns].to_numpy()
    np.testing.assert_allclose(x.mean(0),artifact['input_mean'],rtol=1e-13)
    np.testing.assert_allclose(x.std(0),artifact['input_scale'],rtol=1e-13)
    idx=source.index.to_numpy()
    current=source[list(artifact['config']['targets'])].to_numpy()
    delta=t.iloc[idx+1][list(artifact['config']['targets'])].to_numpy()-current
    z=(x-x.mean(0))/x.std(0)
    augmented=np.vstack([z,np.sqrt(10)*np.eye(len(columns))])
    rhs=np.vstack([delta-delta.mean(0),np.zeros((len(columns),2))])
    reference=np.linalg.lstsq(augmented,rhs,rcond=None)[0]
    np.testing.assert_allclose(reference,artifact['coefficients'],rtol=1e-10,atol=1e-12)
    np.testing.assert_allclose(delta.mean(0),artifact['delta_intercept'],rtol=1e-13)
    write_json(root/'verification.json',{'checks':checks,'B03_accessed':False,'training_scaler_independently_recomputed':True,'ridge_augmented_lstsq_reference_passed':True,'total_development_raw_files_unchanged':sum(v['unchanged_raw_files'] for v in checks.values())})
    print(json.dumps(checks,indent=2))


if __name__=='__main__': main()
