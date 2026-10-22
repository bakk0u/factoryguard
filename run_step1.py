"""Run this file directly in PyCharm, or use python run_step1.py."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from factoryguard.pipelines.prepare import run_step1

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="CSV matching docs/data_contract.md; default: synthetic demo")
    parser.add_argument("--output", type=Path, help="New or empty output directory")
    args = parser.parse_args()
    input_path = args.input or ROOT / "data/raw/demo_sensors.csv"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output or ROOT / "reports/local" / stamp
    try:
        result = run_step1(input_path, output, "synthetic-demo" if args.input is None else "user-provided")
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Loaded and validated {result['rows']} readings from {result['machines']} machines.")
    print(f"Source: {result['source_kind']}; no model trained.")
    print(f"Results: {output.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
