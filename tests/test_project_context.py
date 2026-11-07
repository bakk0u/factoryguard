"""Context integrity and raw-storage isolation without installing Graphify."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_context', ROOT / 'scripts/project_context.py')
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)


class ProjectContextTests(unittest.TestCase):
    def test_reinstall_deduplicates_own_hook_and_preserves_unrelated_hooks(self):
        own = {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'graphify hook-check'}]}
        other = {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'user-custom-check'}]}
        value = {'hooks': {'PreToolUse': [own, json.loads(json.dumps(own)), other]}}
        first = json.dumps(context.normalize_hooks(value), sort_keys=True)
        self.assertEqual(len(value['hooks']['PreToolUse']), 2)
        self.assertIn(other, value['hooks']['PreToolUse'])
        self.assertEqual(first, json.dumps(context.normalize_hooks(value), sort_keys=True))

    def test_fingerprint_detects_changes_additions_deletions_and_excludes_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for name in ('src/module.py', 'data/raw/never-read.py', 'site/source/private.json'):
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text('test fixture', encoding='utf-8')
            before = context.source_hashes(root)
            self.assertEqual(set(before), {'src/module.py'})
            (root / 'src/module.py').write_text('changed', encoding='utf-8')
            self.assertNotEqual(before, context.source_hashes(root))
            (root / 'src/new.py').write_text('new', encoding='utf-8')
            self.assertIn('src/new.py', context.source_hashes(root))
            (root / 'src/module.py').unlink()
            self.assertNotIn('src/module.py', context.source_hashes(root))

    def test_fingerprint_refuses_source_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'src').mkdir()
            try:
                (root / 'src/unsafe.py').symlink_to(root / 'data/raw/unopened.py')
            except OSError:
                self.skipTest('OS does not permit creating test symlinks')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                context.source_hashes(root)

    def test_committed_graph_has_real_locations_and_relationships(self):
        graph = json.loads((ROOT / 'graphify-out/graph.json').read_text(encoding='utf-8'))
        self.assertGreater(context.verify_graph(graph)['nodes'], 100)
        graph['nodes'][0]['source_file'] = 'data/raw/private.py'
        with self.assertRaisesRegex(ValueError, 'Excluded'):
            context.verify_graph(graph)

    def test_status_rejects_stale_sources_and_graph_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            original = (ROOT / 'graphify-out/graph.json').read_bytes()
            (out / 'graph.json').write_bytes(original)
            record = {'source_sha256': {'src/a.py': 'old'},
                      'graph_sha256': context.digest(out / 'graph.json'),
                      'graphify_version': context.VERSION}
            (out / 'provenance.json').write_text(json.dumps(record), encoding='utf-8')
            with patch.object(context, 'OUTPUT', out), patch.object(context, 'source_hashes', return_value={'src/a.py': 'old'}):
                self.assertEqual(context.status(), 0)
                with patch.object(context, 'source_hashes', return_value={'src/a.py': 'new'}):
                    self.assertEqual(context.status(), 1)
                (out / 'graph.json').write_text('{}', encoding='utf-8')
                self.assertEqual(context.status(), 1)

    def test_backend_is_disabled_even_with_inherited_provider_settings(self):
        with patch.dict(context.os.environ, {'GRAPHIFY_BACKEND': 'openai'}):
            self.assertEqual(context.environment()['GRAPHIFY_BACKEND'], 'none')
            self.assertEqual(context.environment()['GRAPHIFY_QUERY_LOG_DISABLE'], '1')
