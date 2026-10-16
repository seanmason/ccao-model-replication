"""Offline checks: no CCAO data download or model binaries required."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TestRepository(unittest.TestCase):
    def test_pinned_source_is_present(self):
        for year,sha in (
            ("2025","f292e7b3a31cd01df5950b3b6bc54e848666a33c"),
            ("2026","39f112d8e194c008c93bd985aaf39a99c64c02e9"),
        ):
            base=ROOT/"upstream"/year
            self.assertTrue((base/"pipeline/01-train.R").exists())
            self.assertTrue((base/"pipeline/02-assess.R").exists())
            self.assertEqual((base/"PINNED_COMMIT").read_text().strip(),sha)

    def test_data_manifest(self):
        manifest=json.loads((ROOT/"config/public_inputs.json").read_text())
        self.assertEqual(set(manifest),{"2025","2026-february","2026-july"})
        for version,files in manifest.items():
            self.assertEqual({v["name"] for v in files},{
                "training_data.parquet","assessment_data.parquet",
                "complex_id_data.parquet","land_nbhd_rate_data.parquet"})
            for item in files:
                self.assertTrue(item["url"].startswith("https://ccao-data-public-us-east-1.s3.amazonaws.com/"))
                self.assertEqual(len(item["sha256"]),64)
                self.assertGreater(item["bytes"],1000)

    def test_trained_model_manifest(self):
        catalog=json.loads((ROOT/"models/MODEL_MANIFEST.json").read_text())
        self.assertEqual(set(catalog),{"2025","2026-february","2026-july"})
        self.assertEqual(sum(len(x) for x in catalog.values()),6)
        for models in catalog.values():
            self.assertEqual(set(models),{"full","evaluation"})
            for info in models.values():
                self.assertEqual(len(info["sha256"]),64)
                self.assertEqual(info["features"],95)
                self.assertGreater(info["bytes"],1000000)

    def test_no_private_case_metadata_in_harness(self):
        # Verify the harness/manifest text, not the independently authored upstream source.
        roots=[ROOT/"README.md",ROOT/"config/public_inputs.json",
               ROOT/"models/MODEL_MANIFEST.json",ROOT/"docs/PROVENANCE.md"]
        forbidden=("1825 greenwood","sean mason","1013419040","legal malpractice")
        for path in roots:
            body=path.read_text().lower()
            for text in forbidden:
                self.assertNotIn(text,body,f"{text!r} in {path}")

if __name__=="__main__":
    unittest.main()
