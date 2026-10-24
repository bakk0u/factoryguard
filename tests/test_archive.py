"""Small generated archives, never copies of dataset data."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from factoryguard.data.archive import extract_verified_zip, verify_file


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make(self, names):
        archive = self.root / "test.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            for name in names:
                stream.writestr(name, b"fixture")
        return archive, {"size": archive.stat().st_size,
                         "checksum": "md5:" + hashlib.md5(archive.read_bytes()).hexdigest(),
                         "max_bytes": 1000}

    def test_extract_and_preserve(self):
        archive, kwargs = self.make(["B01/a.txt"])
        before = archive.read_bytes()
        result = extract_verified_zip(archive, self.root / "raw", **kwargs)
        self.assertEqual(result["uncompressed_bytes"], 7)
        self.assertEqual((self.root / "raw/B01/a.txt").read_bytes(), b"fixture")
        self.assertEqual(archive.read_bytes(), before)
        with self.assertRaises(FileExistsError):
            extract_verified_zip(archive, self.root / "raw", **kwargs)

    def test_unsafe_members_rejected_before_writing(self):
        for names in [["../escape"], ["/escape"], ["B01\\escape"],
                      ["B01/a", "B01/A"], ["B01/a", "B01/a/b"]]:
            with self.subTest(names=names):
                archive, kwargs = self.make(names)
                with self.assertRaises(ValueError):
                    extract_verified_zip(archive, self.root / "raw", **kwargs)
                self.assertFalse((self.root / "raw.extracting").exists())

    def test_size_checksum_and_budget(self):
        archive, kwargs = self.make(["file"])
        with self.assertRaises(ValueError):
            verify_file(archive, 0, kwargs["checksum"])
        with self.assertRaises(ValueError):
            verify_file(archive, kwargs["size"], "md5:" + "0" * 32)
        kwargs["max_bytes"] = 1
        with self.assertRaises(ValueError):
            extract_verified_zip(archive, self.root / "raw", **kwargs)

    def test_symlink_rejected(self):
        archive, kwargs = self.make([])
        with zipfile.ZipFile(archive, "a") as stream:
            link = zipfile.ZipInfo("link")
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            stream.writestr(link, "outside")
        kwargs.update(size=archive.stat().st_size,
                      checksum="md5:" + hashlib.md5(archive.read_bytes()).hexdigest())
        with self.assertRaises(ValueError):
            extract_verified_zip(archive, self.root / "raw", **kwargs)

    def test_crc_failure_never_publishes_destination(self):
        archive, kwargs = self.make(["file"])
        data = archive.read_bytes().replace(b"fixture", b"damaged", 1)
        archive.write_bytes(data)
        kwargs["checksum"] = "md5:" + hashlib.md5(data).hexdigest()
        with self.assertRaises(zipfile.BadZipFile):
            extract_verified_zip(archive, self.root / "raw", **kwargs)
        self.assertFalse((self.root / "raw").exists())
        self.assertTrue((self.root / "raw.extracting").exists())
