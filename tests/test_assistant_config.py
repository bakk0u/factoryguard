"""Launcher isolation uses synthetic credentials; never opens local dotenv files."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


class AssistantConfigTests(unittest.TestCase):
    def test_subprocess_environment_isolation(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/start_assistant.py'
        spec = importlib.util.spec_from_file_location('assistant_launcher', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-only',
                                      'FACTORYGUARD_LLM_MODEL': 'chosen-model'}):
            self.assertNotIn('OPENAI_API_KEY', module.child_environment())
            self.assertEqual(module.child_environment(True)['OPENAI_API_KEY'], 'synthetic-only')
            self.assertEqual(module.child_environment()['FACTORYGUARD_LLM_MODEL'], 'chosen-model')
