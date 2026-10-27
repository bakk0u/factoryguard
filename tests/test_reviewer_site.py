import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reviewer',ROOT/'scripts/build_reviewer_site.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ReviewerSiteTests(unittest.TestCase):
    def test_pinned_build_and_safe_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            module.build(tmp)
            page=(Path(tmp)/'index.html').read_text(encoding='utf-8')
            self.assertIn('Recorded experiment results',page)
            self.assertIn('let cursors=Object.fromEntries',page)
            self.assertNotIn('https://cdn',page)
            self.assertNotIn('/workspace/',page)
            manifest=json.loads((Path(tmp)/'source-manifest.json').read_text())
            self.assertEqual(manifest['experiments'],['B01','B02','B04'])
            self.assertIsNone(manifest['result_code_commit'])
            payload=json.loads((ROOT/'site/source/replay.json').read_text())
            self.assertEqual(len(payload['states']['B01']['events']),377)
            for state in payload['states'].values():
                self.assertNotIn('notes',state)
            self.assertTrue(any(e['interval_s'] and e['interval_s']>24 for e in payload['states']['B01']['events']))
