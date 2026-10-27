import pandas as pd, numpy as np
from pathlib import Path
from factoryguard.release import modeling as m
from factoryguard.release.application import load_artifact
from factoryguard.release.campaign import read
from factoryguard.models.forecast import load_table
from factoryguard.models.selection import metrics
r=Path('reports/local/release-v3');cfg=read(r/'frozen_config.json');done=read(r/'completion.json')
blocks={run:m.prepare(load_table(cfg['tables'][run],run,done['table_sha256'][run]),run) for run in ('B01','B02','B04')}
df=pd.concat([pd.read_csv(r/'development_metrics.csv'),pd.read_csv(r/'stress_metrics.csv')]);count=0
for (tr,ev,group),rows in df.groupby(['training_run','evaluation_run','group']):
 a=load_artifact(r/f'{tr}_{group}.joblib');p=m.predict(a['candidate'],a['pipeline'],blocks[ev])
 for coverage,rr in rows.groupby('coverage'):
  stats=metrics(blocks[ev],p,coverage=='common')
  for _,row in rr.iterrows():
   s=stats[row.channel];assert row['n']==s['n']
   for key in ('mae_v','rmse_v','persistence_mae_v','persistence_rmse_v','mae_ratio','rmse_ratio'):
    np.testing.assert_allclose(row[key],s[key],rtol=1e-12)
   count+=1
print('Verified',count,'saved metric rows; no fits')
