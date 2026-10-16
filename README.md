# Cook County residential AVM reproduction

Independent, **property-agnostic** research repository for reproducing Cook County Assessor's Office (CCAO) residential valuation models. Not affiliated with, endorsed by, or maintained by the CCAO.

**Source code has been imported:** complete pinned upstream 2025 and 2026 modeling code lives in [upstream/2025](upstream/2025) and [upstream/2026](upstream/2026), including the original R / Tidymodels / LightGBM training pipeline, assessment transformations, renv lockfiles, and official documentation.

**Pretrained artifact status:** six independently recovered/verified native LightGBM models (2 for 2025, 4 for 2026) are available in the [separate complete distribution ZIP](docs/PUBLISH_PRETRAINED.md) but are **not in this Git repository yet**. The saved binaries are ~303 MB, so GitHub's ordinary file-write API cannot transmit them reliably; use Git LFS or Release assets. A manifest of their verified hashes is committed in [models/MODEL_MANIFEST.json](models/MODEL_MANIFEST.json). Do not mistake the manifests for actual model files.

## Quick start: reproduce the official source pipeline

Python 3.11+, R, Git, and enough disk/RAM (16 GB RAM recommended) are needed for full training. Prepare one independent working directory per published model input snapshot:

```bash
git clone https://github.com/seanmason/ccao-model-replication.git
cd ccao-model-replication
python3 -m venv .venv && . .venv/bin/activate

python scripts/prepare_run.py 2025
python scripts/download_public_inputs.py 2025
# Install R dependencies into work/2025/; see upstream/2025/README.md
cd work/2025
Rscript -e 'install.packages("renv"); renv::restore(prompt = FALSE)'
UPLOAD_ENABLE_OVERRIDE=false Rscript pipeline/01-train.R
UPLOAD_ENABLE_OVERRIDE=false Rscript pipeline/02-assess.R
```

Each stage uses CCAO's **actual code**, not a simplified model. The above is the baseline reproduction procedure, not a claim that it was successfully rerun on this GitHub host. Official source may require Linux build libraries, package archives, or configuration described in its README. Avoid cloud-only `ingest`, `upload`, and `export` stages without CCAO credentials.

For 2026, prepare **both** published snapshots independently, to avoid overwriting inputs:

```bash
python scripts/prepare_run.py 2026-february
python scripts/download_public_inputs.py 2026-february
python scripts/prepare_run.py 2026-july
python scripts/download_public_inputs.py 2026-july
```

Use `work/2026-february` and `work/2026-july` for training. They share pinned 2026 source code but **not** the input bytes.

## Working with pretrained models

The recovered bundle provides these variants:

| Version | Full model | Holdout model | Model trees | Predictors |
| --- | --- | --- | ---: | ---: |
| 2025 | `pretrained/2025/full.txt` | `pretrained/2025/evaluation.txt` | 1,575 | 95 |
| 2026 February | `pretrained/2026-february/full.txt` | `pretrained/2026-february/evaluation.txt` | 2,460 | 95 |
| 2026 July | `pretrained/2026-july/full.txt` | `pretrained/2026-july/evaluation.txt` | 2,460 | 95 |

When you have the complete distribution ZIP:

```bash
python scripts/import_pretrained.py /path/to/ccao-model-replication-with-trained-models.zip
python scripts/verify_pretrained.py
python -m pip install lightgbm numpy
python scripts/verify_pretrained.py --load
```

Each model requires its associated category encoding and/or saved R recipe for valid inference; **raw model text alone is insufficient**. Raw model output is not a final assessed value. Running the official CCAO `pipeline/02-assess.R` also applies multi-card, neighborhood, land, rounding, and other adjustments. See [publishing instructions](docs/PUBLISH_PRETRAINED.md).

## Provenance and exact input data

- 2025 official source commit: `f292e7b3a31cd01df5950b3b6bc54e848666a33c`
- 2026 official source commit: `39f112d8e194c008c93bd985aaf39a99c64c02e9`
- Public data files and SHA-256 digests are recorded in [config/public_inputs.json](config/public_inputs.json).
- Recovered model sizes, tree counts, and SHA-256 hashes are recorded in [models/MODEL_MANIFEST.json](models/MODEL_MANIFEST.json).
- Published assessments may diverge from model predictions because of non-model valuation steps, administrative corrections and appeals. Models are **not authenticated archived production deployments**.

This repository deliberately contains **no case-specific research, individual property examples, parcel identifiers, private records or communications**.

## Attribution and license

Original code copyright CCAO contributors, licensed AGPL-3.0. See [upstream/2025/LICENSE](upstream/2025/LICENSE), [upstream/2026/LICENSE](upstream/2026/LICENSE), and [CCAO's project](https://github.com/ccao-data/model-res-avm). This independent reproduction harness is distributed under AGPL-3.0. Public data may have separate licensing/usage terms.
