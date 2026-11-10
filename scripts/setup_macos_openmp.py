"""Install the pinned public libomp bottle locally; no Homebrew/system changes.

Download the archive using the command in docs/assistant.md, then pass its path.
This helper is optional development setup, never application startup or training.
"""
import argparse
import hashlib
from pathlib import Path
import platform
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
SHA256 = '64eacbcd08fbec3ebb7076be89466a53d5548a7dbee3542d756b788047277589'
MEMBER = 'libomp/23.1.5/lib/libomp.dylib'


def install(archive):
    if sys.platform != 'darwin' or platform.machine() != 'arm64':
        raise ValueError('This pinned bottle is for macOS arm64 only')
    archive = Path(archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError('libomp archive checksum mismatch')
    # Read only a known regular member; never extract paths or symlinks from tar.
    with tarfile.open(archive) as bundle:
        member = bundle.getmember(MEMBER)
        if not member.isfile():
            raise ValueError('Expected regular libomp library member')
        data = bundle.extractfile(member).read()
    target = ROOT / '.tools/native/libomp-23.1.5/libomp.dylib'
    link = Path(sys.base_prefix) / 'lib/libomp.dylib'
    # This no-Homebrew path is intentionally restricted to a repo-local interpreter.
    if not link.parent.resolve().is_relative_to((ROOT / '.tools').resolve()):
        raise ValueError('Use a repository-local .tools Python, or install libomp with Homebrew')
    if link.exists() or link.is_symlink():
        if link.resolve() != target.resolve():
            raise ValueError('Existing OpenMP library will not be replaced')
    if target.exists() and target.read_bytes() != data:
        raise ValueError('Existing local libomp differs; refusing overwrite')
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)
        target.chmod(0o755)
    if not link.is_symlink():
        link.symlink_to(target)
    print('Pinned libomp installed in .tools; repository-local Python link ready.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        install(args.archive)
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.exit(1, f'{error}\n')
