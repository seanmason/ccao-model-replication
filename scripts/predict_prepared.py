#!/usr/bin/env python3
"""Predict initial card-level fair-market values from 95 prepared CCAO features.

Not a final assessed value. Run official pipeline/02-assess.R for PIN-level
valuation rules, including multi-card, rounding and land adjustments.
"""
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ("2025", "2026-february", "2026-july")

def predict(version, input_path, output_path, variant="full", threads=4):
    import numpy as np
    import pandas as pd
    import lightgbm as lgb

    if version not in VERSIONS or variant not in ("full", "evaluation"):
        raise ValueError("Unrecognized version or model variant")
    models = ROOT / "pretrained" / version
    weights = models / (variant + ".txt")
    codes = models / (variant + "_encoding.json")
    if not (weights.is_file() and codes.is_file()):
        raise FileNotFoundError("Weights and category encodings must be imported; see docs/PUBLISH_PRETRAINED.md")
    frame = pd.read_parquet(input_path) if str(input_path).endswith(".parquet") else pd.read_csv(input_path)
    model = lgb.Booster(model_file=str(weights))
    features = model.feature_name()
    missing = sorted(set(features).difference(frame.columns))
    if missing:
        raise ValueError(f"Missing {len(missing)} prepared features: {missing[:12]}")
    encodings = json.loads(codes.read_text())
    x = frame.loc[:, features].copy()
    for col in features:
        if col in encodings:
            levels = encodings[col]
            key = {value:i for i,value in enumerate(levels)}
            strings = x[col].astype("string")
            x[col] = strings.map(key).fillna(len(levels)-2).where(strings.notna(),len(levels)-1).astype("int32")
        else:
            x[col] = pd.to_numeric(x[col],errors="raise").astype("float64")
    raw = model.predict(x, num_threads=threads)
    if not np.isfinite(raw).all():
        raise ArithmeticError("Nonfinite model predictions")
    out = frame.copy()
    out["pred_initial_model_output"] = raw
    # All six recovered models were trained against dollar-scale prices.
    # Do NOT exponentiate: native LightGBM predictions are already dollars.
    out["pred_initial_fmv_dollars"] = raw
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix == ".parquet":
        out.to_parquet(dest, index=False)
    else:
        out.to_csv(dest, index=False)
    print(f"Scored {len(out):,} prepared card rows; no PIN-level adjustments applied")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, choices=VERSIONS)
    parser.add_argument("--variant", default="full", choices=("full","evaluation"))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=4)
    a = parser.parse_args()
    predict(a.version, a.input, a.output, a.variant, a.threads)
