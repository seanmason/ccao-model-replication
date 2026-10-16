# Publishing the recovered pretrained binaries

The public source repository currently contains the official pipelines and a manifest of **six already-trained, independently recovered LightGBM models**, but the actual 303 MB of model binaries must be uploaded using Git LFS or GitHub Releases. The ChatGPT GitHub connector supports text commits, not file-system-to-LFS streaming.

## Recommended: Git LFS from a local machine

1. Download the separately supplied `ccao-model-replication-with-trained-models.zip` distribution to your machine.
2. Install Git LFS (`git lfs install`).
3. Clone the repository and import just the model subfolders from the distribution:

```bash
git clone https://github.com/seanmason/ccao-model-replication.git
cd ccao-model-replication
git lfs install
python scripts/import_pretrained.py /absolute/path/to/ccao-model-replication-with-trained-models.zip
python scripts/verify_pretrained.py
python -m pip install lightgbm
python scripts/verify_pretrained.py --load

git add .gitattributes pretrained/
git commit -m "Add six verified 2025/2026 LightGBM models and preprocessing artifacts via Git LFS"
git push origin main
```

Model weights are tracked with Git LFS in `.gitattributes`. The `import_pretrained.py` utility copies only `models/` files: it never commits input Parquet data, property-level prediction tables, or any unrelated context.

### Check artifact availability

To verify that model files are **really** published (not just Git LFS pointers):

```bash
git clone https://github.com/seanmason/ccao-model-replication.git fresh-ccao
cd fresh-ccao
git lfs pull
python scripts/verify_pretrained.py
```

Compare six SHA-256 checksums to `models/MODEL_MANIFEST.json`. A GitHub HTML view of a pointer is **not** proof that the actual weight file is available.

## Alternative: GitHub Release files

If LFS bandwidth or quotas are unsuitable, upload the six model files and corresponding encodings/recipes to a versioned GitHub release with their SHA-256 manifest. Downloaders must retrieve exact filenames and verify the hashes before use.

## Reproducibility qualifications

- The original 2025/2026 code is imported from pinned CCAO revisions.
- The models in the separate distribution were trained in prior sessions and verified using saved checksums and LightGBM load tests. They have **not been retrained in this repository's GitHub Actions CI**.
- Trained model predictions are not equal to the Assessor's final certified or Board-adjusted values.
- Saved R recipes and category mappings must accompany the LightGBM binaries.
- Running R in `work/<run>` can require the historical R package versions and compilation prerequisites specified upstream.
