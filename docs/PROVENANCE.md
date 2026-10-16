# Data and model provenance

The original CCAO residential automated valuation model is openly documented at https://github.com/ccao-data/model-res-avm. Its license is AGPL-3.0.

## Official source revisions
| Year | Git commit | Published source |
|---|---|---|
| 2025 | `f292e7b3a31cd01df5950b3b6bc54e848666a33c` | `upstream/2025/` |
| 2026 | `39f112d8e194c008c93bd985aaf39a99c64c02e9` | `upstream/2026/` |

The official source was imported using `.github/workflows/import-official-sources.yml`, which pins both commits and preserves upstream attribution, dependencies, recipes, R training pipeline, and assessment transformations.

## Input datasets
The model input manifest in `config/public_inputs.json` records URLs, byte lengths and SHA-256 digests for **twelve** published files: training, assessment, complex ID and neighborhood land rates for the 2025 input release and each of the 2026 February and July input snapshots. Data files are downloaded at runtime and are not committed.

## Saved model binaries
The six recovered models have independent full/evaluation variants with exactly 95 features and either 1,575 (2025) or 2,460 (2026) trees. Their sizes and SHA-256 digests are pinned in `models/MODEL_MANIFEST.json`. Initial feature encodings and official saved R preprocessing recipes accompany these weights in the separate ZIP bundle.

The recovered weight binaries are a **research reproduction**, not proof of byte-identical production models. The published annual tax roll includes downstream adjustments and manual processes; parity with the mailed value does not establish parity with any CCAO archived raw prediction.

## Privacy
Only public or anonymized general-purpose code, structural schema information, and aggregate model descriptions belong in this repository. Never commit case notes, tax notices, personally identifiable records, parcel-level result exports, third-party private data, or credentials.
