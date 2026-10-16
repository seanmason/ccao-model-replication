#!/usr/bin/env python3
"""Prepare isolated, pinned working source for a CCAO model run.

Does not download datasets, install dependencies or change upstream sources.
"""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ("2025", "2026-february", "2026-july")

def prepare(version: str, overwrite: bool = False) -> Path:
    if version not in VERSIONS:
        raise ValueError("Unknown model version: " + version)
    year = version[:4]
    src = ROOT / "upstream" / year
    dest = ROOT / "work" / version
    if not (src / "pipeline/01-train.R").is_file():
        raise FileNotFoundError("Official model source not imported: " + str(src))
    if dest.exists():
        if not overwrite:
            raise FileExistsError(f"{dest} already exists (use --overwrite to replace it)")
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    (dest / "input").mkdir(exist_ok=True)
    # CCAO's DVC pipeline writes to these output paths. Prepare them in advance
    # so individual R stages may be run without AWS or the ingest stage.
    import re
    dvc = (dest / "dvc.yaml").read_text()
    for name in sorted(set(re.findall(r"output/[A-Za-z0-9_./-]+", dvc))):
        (dest / name).parent.mkdir(parents=True, exist_ok=True)
    print(f"Prepared {version}: {dest}")
    return dest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=VERSIONS)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    prepare(args.version, args.overwrite)
