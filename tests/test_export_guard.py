from pathlib import Path
import tempfile
import unittest

from factoryguard.release.export_guard import validate_export_directory


class ReviewerOutputGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.output = self.base / 'export'

    def validate(self, output=None):
        return validate_export_directory(
            self.output if output is None else output, repository_root=self.repo)

    def test_new_destination_is_allowed_without_creating_it(self):
        self.assertEqual(self.validate(), self.output)
        self.assertFalse(self.output.exists())

    def test_empty_and_previous_generated_exports_are_allowed(self):
        self.output.mkdir()
        self.validate()
        for name in ('index.html', 'source-manifest.json', '.nojekyll'):
            (self.output / name).write_text('previous generated content')
        self.validate()

    def test_mixed_private_files_are_preserved_and_rejected(self):
        self.output.mkdir()
        for name in ('.env', 'private.sqlite', 'notes.json', 'old.html'):
            with self.subTest(name=name):
                private = self.output / name
                private.write_bytes(b'private sentinel')
                with self.assertRaisesRegex(ValueError, 'choose a clean output'):
                    self.validate()
                self.assertEqual(private.read_bytes(), b'private sentinel')
                self.assertFalse((self.output / 'index.html').exists())
                private.unlink()

    def test_nested_directory_is_rejected_even_with_a_generated_name(self):
        self.output.mkdir()
        nested = self.output / 'index.html'
        nested.mkdir()
        (nested / 'private.txt').write_text('keep this')
        with self.assertRaises(ValueError):
            self.validate()
        self.assertEqual((nested / 'private.txt').read_text(), 'keep this')

    def test_output_file_is_not_overwritten(self):
        self.output.write_text('keep this')
        with self.assertRaisesRegex(ValueError, 'must be a directory'):
            self.validate()
        self.assertEqual(self.output.read_text(), 'keep this')

    def test_repository_root_and_its_parent_are_rejected(self):
        for path in (self.repo, self.base):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'repository root'):
                self.validate(path)

    def test_source_and_data_destinations_are_rejected_before_creation(self):
        for name in ('src', 'site', 'assistant', 'configs', 'tests', 'scripts',
                     '.git', '.github', 'graphify-out', 'data'):
            target = self.repo / name / 'new-export'
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'outside source'):
                self.validate(target)
            self.assertFalse(target.exists())

    def test_standard_local_and_pages_destinations_are_allowed(self):
        for name in ('reports/local/reviewer-site', 'public'):
            self.validate(self.repo / name)

    def make_symlink(self, link, destination, *, directory=False):
        try:
            link.symlink_to(destination, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f'OS does not permit symlinks: {error}')

    def test_symlinked_output_cannot_redirect_writes(self):
        other = self.base / 'other'
        other.mkdir()
        self.make_symlink(self.output, other, directory=True)
        with self.assertRaisesRegex(ValueError, 'symbolic link'):
            self.validate()
        self.assertEqual(list(other.iterdir()), [])

    def test_dangling_output_symlink_is_rejected(self):
        self.make_symlink(self.output, self.base / 'missing', directory=True)
        with self.assertRaisesRegex(ValueError, 'symbolic link'):
            self.validate()

    def test_generated_file_symlinks_cannot_overwrite_private_targets(self):
        self.output.mkdir()
        private = self.base / 'private.txt'
        private.write_text('keep this')
        for name in ('index.html', 'source-manifest.json', '.nojekyll'):
            with self.subTest(name=name):
                link = self.output / name
                self.make_symlink(link, private)
                with self.assertRaises(ValueError):
                    self.validate()
                self.assertEqual(private.read_text(), 'keep this')
                link.unlink()

    def test_parent_symlink_cannot_bypass_source_directory_guard(self):
        (self.repo / 'site').mkdir()
        alias = self.base / 'alias'
        self.make_symlink(alias, self.repo / 'site', directory=True)
        with self.assertRaisesRegex(ValueError, 'outside source'):
            self.validate(alias / 'new-export')


if __name__ == '__main__':
    unittest.main()
