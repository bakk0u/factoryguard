"""Download/verify ONLY the description and B01; extract outside the checkout.

Usage: .venv/bin/python scripts/prepare_paderborn.py /workspace/datasets/paderborn-10868257
"""
import argparse
import json
from pathlib import Path
import shutil
import urllib.request

from factoryguard.data.archive import extract_verified_zip, verify_file


BASE = "https://zenodo.org/api/records/10868257"
PDF = "LDM_UPB_Run-to-failure_data_set_of_ball_bearings.pdf"


def download(url: str, target: Path) -> None:
    partial = target.with_name(target.name + ".partial")
    if partial.exists():
        raise FileExistsError(f"Partial download exists; inspect it first: {partial}")
    with urllib.request.urlopen(url, timeout=120) as source, partial.open("xb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
    partial.rename(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = args.destination.resolve()
    checkout = Path(__file__).resolve().parents[1]
    if root == checkout or checkout in root.parents:
        parser.error("Raw data destination must be outside the Git checkout")
    root.mkdir(parents=True, exist_ok=True)
    metadata = root / "record.json"
    if not metadata.exists():
        download(BASE, metadata)
    record = json.loads(metadata.read_text())
    files = {item["key"]: item for item in record["files"]}
    for name in (PDF, "B01.zip"):
        item = files[name]
        target = root / name
        if not target.exists():
            if shutil.disk_usage(root).free < item["size"] + 512 * 1024**2:
                raise ValueError(f"Insufficient space to download {name}")
            download(item["links"]["self"], target)
        verify_file(target, item["size"], item["checksum"])
        print(f"Verified {name}: {item['size']} bytes, {item['checksum']}")
    item = files["B01.zip"]
    manifest = extract_verified_zip(
        root / "B01.zip", root / "raw", size=item["size"],
        checksum=item["checksum"], max_bytes=8 * 1024**3,
    )
    (root / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
