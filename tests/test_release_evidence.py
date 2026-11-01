import tempfile
import unittest
from pathlib import Path

from scripts.verify_release_evidence import REQUIRED_SECTIONS, RELEASES, validate_release_evidence


class ReleaseEvidenceTests(unittest.TestCase):
    def build_fixture(self, root):
        for version in RELEASES:
            path = root / "docs" / "releases" / f"{version}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {version}\n\n" + "\n\n".join(REQUIRED_SECTIONS), encoding="utf-8")
        for name in (
            "docs/demo-script.md", "docs/evidence-index.md", "docs/contributions/README.md",
            "docs/e2e-defense-chain.md", "docs/performance-report.md", "docs/coverage.md",
        ):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("verified\n", encoding="utf-8")

    def test_repository_release_evidence_is_complete(self):
        self.assertEqual(validate_release_evidence(), [])

    def test_missing_section_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build_fixture(root)
            path = root / "docs" / "releases" / "v1.0.0.md"
            path.write_text("# v1.0.0\n", encoding="utf-8")
            errors = validate_release_evidence(root)
            self.assertTrue(any("v1.0.0.md missing ## Features" in error for error in errors))

    def test_draft_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build_fixture(root)
            path = root / "docs" / "releases" / "v0.2.0.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n计划草案\n", encoding="utf-8")
            self.assertTrue(any("draft markers" in error for error in validate_release_evidence(root)))


if __name__ == "__main__":
    unittest.main()
