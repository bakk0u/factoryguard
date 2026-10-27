"""Regression checks for deterministic resource cleanup and atomic replay."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from test_release_modeling import data
from test_release_application import artifact
from factoryguard.release.store import Store
from factoryguard.pipelines.assess_development import main
from factoryguard.pipelines.forecast import fresh
import contextlib
import io


class ReliabilityTests(unittest.TestCase):
    def test_configured_source_root_rejected_before_mkdir(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'source storage'
            with patch.dict('os.environ', {'FACTORYGUARD_RAW_ROOT':str(root)}):
                for output in (root,root/'raw'/'B01'/'derived',root/'raw'/'..'/'archives'):
                    with patch.object(Path,'mkdir',side_effect=AssertionError('Source write')):
                        with self.assertRaises(ValueError):fresh(output)
                        with patch('sys.argv',['assess_development','--output',str(output)]), contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit) as error:main()
                            self.assertEqual(error.exception.code,2)
                # A sibling sharing the prefix must remain usable.
                target=fresh(Path(directory)/'source storage-derived')
                self.assertTrue(target.is_dir())

    def test_connections_close_on_success_and_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory)/'replay.sqlite')
            for fail in (False,True):
                try:
                    with store.connect() as connection:
                        connection.execute('CREATE TABLE IF NOT EXISTS example (value INTEGER)')
                        if fail:raise RuntimeError('fixture')
                except RuntimeError:pass
                with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')

    def test_concurrent_steps_exhaustion_and_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory)/'replay.sqlite')
            store.initialize({'B01':data(n=8)},{})
            with patch('factoryguard.release.store.notices',side_effect=RuntimeError('fixture')):
                with self.assertRaises(RuntimeError):store.step('B01',artifact(),{})
            self.assertEqual(store.state('B01')['revealed'],0)
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda _:store.step('B01',artifact(),{}),range(12)))
            state=Store(store.path).state('B01')
            self.assertEqual(state['revealed'],8)
            self.assertEqual([e['measurement_id'] for e in state['events']],list(range(1,9)))
            self.assertEqual(store.step('B01',artifact(),{}),state)
            self.assertEqual(store.reset('B01')['events'],[])
