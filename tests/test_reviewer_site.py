import importlib.util
import json
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reviewer',ROOT/'scripts/build_reviewer_site.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ReviewerSiteTests(unittest.TestCase):
    def test_reviewer_sources_include_guidance_without_generation_and_scrub_build_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict('os.environ',{'OPENAI_API_KEY':'synthetic-build-secret'}), patch.object(module.subprocess,'check_output',return_value='fixture-commit\n') as git:
                module.build(tmp)
                self.assertNotIn('OPENAI_API_KEY',git.call_args.kwargs['env'])
            page=(Path(tmp)/'index.html').read_text()
            for text in ('Start here','Walk through an investigation','Guided walkthrough · deterministic guidance','Ask about these measurements','--midnight:#02070A','--blue:#0297DE','--orange:#FC734D'):
                self.assertIn(text,page)
            self.assertNotIn('synthetic-build-secret',page)
            self.assertNotIn('<script src="/assistant-ui.js">',page)

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
            exported=json.loads(page.split('const embedded=',1)[1].split(';\nlet meta',1)[0])
            self.assertEqual(exported['states'],payload['states'])
            self.assertEqual(exported['metadata']['models'],payload['metadata']['models'])
            self.assertEqual(sum(len(s['events']) for s in exported['states'].values()),2607)
            metrics=json.loads(page.split('const reviewerMetrics=',1)[1].split(';const savedSelection=',1)[0])
            expected=[]
            for name in ('development_metrics.csv','stress_metrics.csv'):
                expected.extend(csv.DictReader(io.StringIO((ROOT/'site/source'/name).read_text(encoding='utf-8'))))
            self.assertEqual(len(metrics),432)
            self.assertEqual(metrics,expected)
            self.assertIn('snapshot_id',exported['metadata']['reviewer_source_manifest'])
            self.assertEqual(len(payload['states']['B01']['events']),377)
            for state in payload['states'].values():
                self.assertNotIn('notes',state)
            self.assertTrue(any(e['interval_s'] and e['interval_s']>24 for e in payload['states']['B01']['events']))
