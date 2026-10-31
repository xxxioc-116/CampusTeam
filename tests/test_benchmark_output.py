"""Security tests for the benchmark report output path (#24 review fix).

``scripts/benchmark_api.py`` writes its markdown report to disk. To rule out
path traversal / arbitrary file write (SonarCloud security hotspot), the
``--out`` argument must only accept a plain file name and always resolve
inside ``<repo>/artifacts/``.
"""

import importlib.util
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "benchmark_api_under_test", BASE_DIR / "scripts" / "benchmark_api.py")
benchmark_api = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(benchmark_api)


class OutputPathTests(unittest.TestCase):
    def test_plain_name_resolves_into_artifacts(self):
        resolved = benchmark_api.resolve_output_path("performance-report.md")
        self.assertEqual(resolved, BASE_DIR / "artifacts" / "performance-report.md")
        self.assertEqual(resolved.parent, benchmark_api.OUTPUT_DIR)

    def test_absolute_path_is_rejected(self):
        for raw in ("C:/Users/everyone/report.md", "/etc/passwd", "~/report.md"):
            with self.assertRaises(ValueError, msg=raw):
                benchmark_api.resolve_output_path(raw)

    def test_dotdot_escape_is_rejected(self):
        for raw in ("../report.md", "..\\report.md", "artifacts/../../report.md",
                    "..%2Freport.md".replace("%2F", "/")):
            with self.assertRaises(ValueError, msg=raw):
                benchmark_api.resolve_output_path(raw)

    def test_backslash_and_colon_are_rejected_on_any_platform(self):
        # On POSIX Path() sees a backslash as a regular character, so the
        # validator must reject it as a raw character, not via Path semantics.
        for raw in ("..\\report.md", "sub\\report.md", "C:report.md", "report:md"):
            with self.assertRaises(ValueError, msg=raw):
                benchmark_api.resolve_output_path(raw)

    def test_directory_components_are_rejected(self):
        for raw in ("docs/report.md", "sub/report.md", "./report.md", ".hidden/report.md"):
            with self.assertRaises(ValueError, msg=raw):
                benchmark_api.resolve_output_path(raw)

    def test_empty_and_dot_names_are_rejected(self):
        for raw in ("", ".", ".."):
            with self.assertRaises(ValueError, msg=raw):
                benchmark_api.resolve_output_path(raw)


if __name__ == "__main__":
    unittest.main()
