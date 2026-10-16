#!/usr/bin/env python3
"""Import verified pretrained model files from the prior complete distribution ZIP.

Do not unpack or commit raw parcel-level result files. Only model files are read.
No inputs are uploaded to any service by this script.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ccao-model-replication/"
MAP = {
 "ccao_2025/models/":"2025",
 "ccao_2026/runs/february/models/":"2026-february",
 "ccao_2026/runs/july/models/":"2026-july",
}
EXT = {".txt", ".rds", ".json"}

def import_models(archive_path: Path) -> int:
    catalog = json.loads((ROOT/"models/MODEL_MANIFEST.json").read_text())
    copied = 0
    with zipfile.ZipFile(archive_path) as z:
        for src in z.namelist():
            if not src.startswith(PREFIX):
                continue
            name = src[len(PREFIX):]
            for before, version in MAP.items():
                if not name.startswith(before):
                    continue
                part = name[len(before):]
                if "/" in part or Path(part).suffix.lower() not in EXT:
                    continue
                dest = ROOT/"pretrained"/version/part
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():
                    raise FileExistsError(f"Refusing to replace existing artifact: {dest}")
                with z.open(src) as inp, dest.open("wb") as out:
                    h=hashlib.sha256()
                    total=0
                    while True:
                        b=inp.read(1024*1024)
                        if not b: break
                        out.write(b); h.update(b); total += len(b)
                v = catalog.get(version,{}).get(dest.stem)
                if v and (v["bytes"] != total or v["sha256"] != h.hexdigest()):
                    dest.unlink(missing_ok=True)
                    raise ValueError(f"Model checksum does not match pinned artifact: {dest}")
                copied += 1
                print(f"Imported: {dest.relative_to(ROOT)} ({total:,} bytes)")
    if copied < 6:
        raise RuntimeError("Expected at least six trained model files")
    return copied

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive",type=Path,help="Path to complete trained-model distribution ZIP")
    args = parser.parse_args()
    print("Imported",import_models(args.archive),"files")
