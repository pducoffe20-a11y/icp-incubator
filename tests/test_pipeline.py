import json
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_sample_generates_drafts_and_holds_missing_email(self):
        with tempfile.TemporaryDirectory() as tmp:
            outbox = Path(tmp) / "outbox"
            code = run_pipeline.run(
                Path(__file__).resolve().parents[1] / "examples" / "sample-accounts.csv",
                outbox,
                hold_if_no_signal=False,
            )
            self.assertEqual(code, 0)
            drafts = json.loads((outbox / "drafts.json").read_text(encoding="utf-8"))
            self.assertEqual(len(drafts), 3)
            self.assertTrue((outbox / "briefs" / "wisconsin-hospital-association.md").exists())
            self.assertTrue(all(draft["body_format"] == "text" for draft in drafts))
            self.assertTrue(all(draft["review"] is False for draft in drafts))

    def test_thin_evidence_is_flagged_for_review(self):
        row = run_pipeline.AccountRow(
            line=2,
            account_name="Example Association",
            contact_name="Taylor Green",
            contact_title="Director of Education",
            contact_email="taylor@example.org",
            website="example.org",
            vertical="association",
            state="MI",
            signal="",
            priority="low",
        )
        draft = run_pipeline.draft_for(row)
        self.assertEqual(draft["evidence"], "Thin")
        self.assertTrue(draft["review"])
        self.assertIn("do not want to assume", draft["body"])


if __name__ == "__main__":
    unittest.main()
