"""Standalone replay packaging uses derived events only, without a live server."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('offline_dashboard',Path('scripts/export_b01_dashboard.py'))
export=importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class OfflineDashboardTests(unittest.TestCase):
    def test_standalone_embeds_only_declared_replay_and_removes_network_adapter(self):
        template=Path('src/factoryguard/monitoring/dashboard.html').read_text()
        event={'observation':{'provenance__experiment':'B01'},'issued':{'status':'pending'}}
        html=export.build_html([event],template)
        self.assertIn('const offlineEvents=',html)
        self.assertNotIn('await fetch(',html)
        self.assertNotIn('<option value="B04">',html)
        self.assertNotIn('<option value="B02">',html)
        self.assertIn('complete precomputed replay',html)
        self.assertIn('events[events.length-1].issued',html)

    def test_empty_or_other_experiment_is_rejected(self):
        for events in ([],[{'observation':{'provenance__experiment':'B03'}}],
                       [{'observation':{'provenance__experiment':'B02'}}]):
            with self.assertRaises(ValueError): export.build_html(events,'')

    def test_embedded_text_cannot_close_script_and_changed_template_is_rejected(self):
        events=[{'observation':{'provenance__experiment':'B01','note':'</script><script>bad()</script>'}}]
        template=Path('src/factoryguard/monitoring/dashboard.html').read_text()
        html=export.build_html(events,template)
        self.assertNotIn('</script><script>bad()',html)
        self.assertIn(r'\u003c/script>',html)
        with self.assertRaises(ValueError): export.build_html(events,'no API hook')
