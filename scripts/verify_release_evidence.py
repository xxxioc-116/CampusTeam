"""Validate the release and defense evidence required by issue #28."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASES = ("v0.1.0", "v0.2.0", "v1.0.0")
REQUIRED_SECTIONS = ("## Features", "## Bug Fixes", "## Known Limitations", "## Verification", "## Contributors")


def validate_release_evidence(root=ROOT):
    errors = []
    for version in RELEASES:
        path = root / "docs" / "releases" / f"{version}.md"
        if not path.is_file():
            errors.append(f"missing release notes: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{path.relative_to(root)} missing {section}")
        if "计划草案" in text or "发布草案" in text:
            errors.append(f"{path.relative_to(root)} still contains draft markers")

    required_files = (
        "docs/demo-script.md",
        "docs/evidence-index.md",
        "docs/contributions/README.md",
        "docs/e2e-defense-chain.md",
        "docs/performance-report.md",
        "docs/coverage.md",
    )
    for name in required_files:
        path = root / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(f"missing or empty evidence: {name}")
    return errors


def main():
    errors = validate_release_evidence()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("release evidence: OK (v0.1.0, v0.2.0, v1.0.0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
