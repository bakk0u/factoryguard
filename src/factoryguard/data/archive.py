"""Checksum-gated, bounded ZIP extraction into a new directory only."""
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile


def verify_file(path: Path, size: int, checksum: str) -> None:
    """Check exact published size and algorithm:digest without loading the file."""
    path = Path(path)
    if path.stat().st_size != size:
        raise ValueError("Archive size differs from published size")
    algorithm, expected = checksum.split(":", 1)
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected:
        raise ValueError("Archive checksum differs from published checksum")


def extract_verified_zip(path: Path, destination: Path, *, size: int,
                         checksum: str, max_bytes: int) -> dict:
    """Preflight every member, then extract; refuse links and existing targets.

    Raw bytes are copied without modification. ZIP CRCs are checked by zipfile
    as each member is read. A failed extraction leaves an explicitly incomplete
    directory for inspection, never a successfully renamed destination.
    """
    path, destination = Path(path), Path(destination)
    verify_file(path, size, checksum)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    staging = destination.with_name(destination.name + ".extracting")
    if staging.exists() or staging.is_symlink():
        raise FileExistsError(staging)
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        total = sum(item.file_size for item in members)
        if total > max_bytes:
            raise ValueError("Uncompressed ZIP exceeds extraction budget")
        if total + 512 * 1024**2 > shutil.disk_usage(destination.parent).free:
            raise ValueError("Insufficient disk space including 512 MiB margin")
        seen, files = set(), set()
        for item in members:
            name = item.filename.rstrip("/")
            parts = PurePosixPath(name).parts
            mode = item.external_attr >> 16
            if (not parts or name.startswith("/") or "\\" in name
                    or ":" in name or any(p in ("", ".", "..") for p in name.split("/"))
                    or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR))):
                raise ValueError(f"Unsafe ZIP member: {item.filename}")
            key = name.casefold()
            if key in seen:
                raise ValueError(f"Duplicate ZIP destination: {name}")
            seen.add(key)
            if not item.is_dir():
                files.add(key)
        for name in seen:
            if any(str(parent) in files for parent in PurePosixPath(name).parents
                   if str(parent) != "."):
                raise ValueError("ZIP file/directory collision")
        staging.mkdir()
        for item in members:
            target = staging / item.filename
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
        staging.rename(destination)
    return {"members": len(members), "uncompressed_bytes": total,
            "published_checksum": checksum, "compressed_bytes": size}
