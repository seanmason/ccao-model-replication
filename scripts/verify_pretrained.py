#!/usr/bin/env python3
"""Verify all six recovered model hashes, tree counts, and predictor counts.

Add --load to check models using LightGBM; otherwise only stdlib is needed.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def verify(load=False):
    catalog=json.loads((ROOT/"models/MODEL_MANIFEST.json").read_text())
    if load:
        import lightgbm as lgb
    checked=0
    for version, models in catalog.items():
        for variant, spec in models.items():
            p=ROOT/spec["relative_path"]
            if not p.is_file():
                raise FileNotFoundError(f"Missing pretrained model: {p} (see docs/PUBLISH_PRETRAINED.md)")
            if p.stat().st_size!=spec["bytes"] or sha256(p)!=spec["sha256"]:
                raise AssertionError(f"Invalid pretrained model checksum: {p}")
            if load:
                model=lgb.Booster(model_file=str(p))
                assert model.num_trees()==spec["trees"],(p,model.num_trees())
                assert model.num_feature()==spec["features"],(p,model.num_feature())
            print("PASS",version,variant,":",spec["sha256"])
            checked+=1
    if checked!=6:
        raise AssertionError(f"Expected six models; verified {checked}")
    print("Verified six models successfully")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--load",action="store_true",help="Also load models in LightGBM")
    args=parser.parse_args()
    verify(args.load)
