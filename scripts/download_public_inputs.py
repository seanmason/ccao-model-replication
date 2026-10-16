#!/usr/bin/env python3
"""Download official public Parquet training/assessment input snapshots.

Only accepts files that match previously recovered, pinned length/SHA-256.
Uses standard-library Python; no private credentials required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "public_inputs.json"
CHUNK = 1024 * 1024

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(CHUNK), b""):
            h.update(data)
    return h.hexdigest()

def verify(path: Path, item: dict) -> bool:
    return (path.is_file() and path.stat().st_size == item["bytes"]
            and digest(path) == item["sha256"])

def download(version: str) -> None:
    versions = json.loads(CATALOG.read_text())
    if version not in versions:
        raise ValueError(f"Unknown version {version!r}")
    target = ROOT / "work" / version / "input"
    if not target.is_dir():
        raise FileNotFoundError(f"Missing {target}; first run prepare_run.py {version}")
    for item in versions[version]:
        out = target / item["name"]
        if verify(out, item):
            print("Already verified:", out)
            continue
        if out.exists():
            raise ValueError(f"File differs from pinned public snapshot: {out}")
        temp = out.with_suffix(out.suffix + ".part")
        try:
            print("Downloading", item["url"], flush=True)
            req = urllib.request.Request(item["url"], headers={"User-Agent": "ccao-model-replication/1.0"})
            with urllib.request.urlopen(req, timeout=180) as response, temp.open("wb") as dest:
                while True:
                    data = response.read(CHUNK)
                    if not data:
                        break
                    dest.write(data)
            if not verify(temp, item):
                raise ValueError(f"Size or SHA-256 mismatch: {item['url']}")
            os.replace(temp, out)
            print("Verified", out.name, out.stat().st_size, digest(out))
        except BaseException:
            temp.unlink(missing_ok=True)
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=("2025","2026-february","2026-july"))
    args = parser.parse_args()
    download(args.version)
