"""No real new-run observations: generated fixtures test integrity-only scope."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
import pandas as pd
from scipy.io import savemat


spec=importlib.util.spec_from_file_location('selected_acquisition',Path(__file__).resolve().parents[1]/'scripts/acquire_selected_paderborn.py')
acquisition=importlib.util.module_from_spec(spec)
spec.loader.exec_module(acquisition)


class SelectedAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'raw').mkdir()
        (self.root/'record.json').write_text('{}')

    def test_existing_verified_archive_never_downloaded_again(self):
        path=self.root/'B02.zip'
        path.write_bytes(b'generated archive stand-in')
        item={'key':path.name,'size':path.stat().st_size,
              'checksum':'md5:'+hashlib.md5(path.read_bytes()).hexdigest(),
              'links':{'self':'https://zenodo.org/not-requested'}}
        with patch.object(acquisition,'ROOT',self.root), patch.object(acquisition,'load_plan',return_value=({'roles':{'B02':'development'}},item)), \
             patch.object(acquisition.subprocess,'run',side_effect=AssertionError('Unexpected network request')) as network, \
             contextlib.redirect_stdout(io.StringIO()):
            acquisition.download('B02')
        network.assert_not_called()
        receipt=json.loads((self.root/'B02.download.json').read_text())
        self.assertTrue(receipt['reused_existing_archive'])
        self.assertTrue(receipt['published_checksum_verified'])
        before=(self.root/'B02.download.json').read_bytes()
        with patch.object(acquisition,'ROOT',self.root), patch.object(acquisition,'load_plan',return_value=({'roles':{'B02':'development'}},item)), \
             patch.object(acquisition.subprocess,'run',side_effect=AssertionError('Unexpected network request')), \
             contextlib.redirect_stdout(io.StringIO()):
            acquisition.download('B02')
        self.assertEqual((self.root/'B02.download.json').read_bytes(),before)

    def test_heldout_validation_reads_headers_not_signal_values(self):
        archive=self.root/'B03.zip'
        times=['19-Oct-2021 08:00:00','19-Oct-2021 08:00:12']
        tables={
            'meanTemperatures':pd.DataFrame({'Time':times,'Mean Abs. Temp. T1 / °C':[1.,2.],
                                             'Mean Abs. Temp. T2 / °C':[1.,2.],'Mean Room Temp. / °C':[1.,2.]}),
            'operatingConditions':pd.DataFrame({'Time':times,**{c:[1.,2.] for c in [
                'setDynLoad / N','peak_dynLoad / N','setStatLoad / N','meanAbs_statLoad / N','setSpeed / rpm','meanAbs_speed / rpm']}})}
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as stream:
            for suffix,frame in tables.items():
                stream.writestr(f'B03/B03_{suffix}.csv',frame.to_csv(index=False))
            # Deliberately nonfinite values: header-only validation must make no
            # claim that MAT values are finite and never compute descriptors.
            for n in [1,2]:
                buffer=io.BytesIO()
                savemat(buffer,{name:np.full((204800,1),np.nan) for name in ['accHorizRear_A','accHorizFrontal_C','measTime']})
                stream.writestr(f'B03/vibrationData/data_B03_M{n:04d}.mat',buffer.getvalue())
        item={'key':archive.name,'size':archive.stat().st_size,
              'checksum':'md5:'+hashlib.md5(archive.read_bytes()).hexdigest()}
        with patch.object(acquisition,'ROOT',self.root), patch.object(acquisition,'EXPECTED',{'B03':2}), \
             patch.object(acquisition,'load_plan',return_value=({'roles':{'B03':'held_out_reserve_integrity_structure_only'}},item)), \
             patch('scipy.io.loadmat',side_effect=AssertionError('Held-out waveform values requested')), \
             contextlib.redirect_stdout(io.StringIO()):
            acquisition.validate('B03')
        report=json.loads((self.root/'B03.structure.json').read_text())
        self.assertTrue(report['structural_checks_passed'])
        self.assertFalse(report['signal_values_inspected'])
        self.assertFalse(report['feature_distributions_computed'])
        self.assertEqual(report['mat_files_checked'],2)
        self.assertTrue(any('values/finiteness/time grids not loaded' in warning for warning in report['limitations']))
