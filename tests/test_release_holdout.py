"""Synthetic format fixtures only; no real reserve files accessed."""
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest
from hashlib import md5
import zipfile

import numpy as np
import pandas as pd
from scipy.io import savemat

from factoryguard.release.holdout import execute,gate,code_hashes,CHECKS
from factoryguard.release.campaign import write,read
from factoryguard.release.modeling import candidates
from factoryguard.data.paderborn import CHANNELS,SAMPLE_COUNT,SAMPLE_RATE_HZ,TEMPERATURE_COLUMNS,OPERATING_COLUMNS
from factoryguard.models.forecast import digest


class ReserveProcedureTests(unittest.TestCase):
    def test_denied_before_any_file_access(self):
        with patch('factoryguard.release.holdout.read',side_effect=AssertionError('Must not open')):
            with self.assertRaisesRegex(ValueError,'sealed'):gate('/not-read','/not-read',False)

    def test_synthetic_end_to_end_and_tamper_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);raw=root/'synthetic-reserve';raw.mkdir();(raw/'vibrationData').mkdir()
            times=['19-Oct-2021 09:00:00','19-Oct-2021 09:00:18','19-Oct-2021 09:00:36','19-Oct-2021 09:01:18']
            for name,cols,values in [('meanTemperatures',TEMPERATURE_COLUMNS,[30,31,20]),
                                   ('operatingConditions',OPERATING_COLUMNS,[800,800,3500,3500,2700,2700])]:
                f=pd.DataFrame({'Time':times})
                for c,v in zip(cols,values):f[c]=v
                f.to_csv(raw/f'B03_{name}.csv',index=False,encoding='utf-8')
            t=np.arange(SAMPLE_COUNT)/SAMPLE_RATE_HZ
            for i in range(1,5):savemat(raw/'vibrationData'/f'data_B03_M{i:04d}.mat',
                 {'measTime':t[:,None],CHANNELS[0]:(np.sin(2*np.pi*100*t)*i)[:,None],CHANNELS[1]:np.zeros((SAMPLE_COUNT,1))})
            archive=root/'synthetic.zip'
            with zipfile.ZipFile(archive,'w') as z:
                for path in raw.rglob('*'):
                    if path.is_file():z.write(path,path.relative_to(raw).as_posix())
            plan={'protocol':'release-v3-reserve','reserve_run':'B03','implementation_sha256':code_hashes(),
                  'expected_bursts':4,'published_archive_md5':md5(archive.read_bytes()).hexdigest(),
                  'candidate':next(c for c in candidates() if c['id']=='smoothing_0.5'),
                  'development_support_counts':{}}
            write(root/'plan.json',plan)
            attestation={'reviewer':'synthetic-test','authorization':'synthetic-only','documentation_evidence':'generated known schema',
                         'plan_sha256':digest(root/'plan.json'),**{k:True for k in CHECKS}}
            write(root/'attestation.json',attestation)
            execute(root/'plan.json',root/'attestation.json',raw,archive,root/'out',approved=True)
            result=read(root/'out'/'result.json')
            self.assertTrue(result['raw_unchanged']);self.assertFalse(result['fitting_performed'])
            self.assertEqual(result['coverage']['observations'],4)
            self.assertEqual(result['coverage']['exclusion_reasons']['expired_gap'],1)
            # Constant C => undefined moments; common coverage empty, broad C retained.
            self.assertEqual(result['selected_common']['C']['n'],0)
            self.assertEqual(result['selected_broad']['C']['n'],2)
            plan['implementation_sha256']['release/modeling.py']='changed';write(root/'plan.json',plan)
            with self.assertRaisesRegex(ValueError,'changed'):gate(root/'plan.json',root/'attestation.json',True)
