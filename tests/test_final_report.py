import json
from pathlib import Path

from explorer.final_report import FinalReport


def test_final_report_builds_summary(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()

    (reports / "repository-overview.md").write_text(
        "# Repository Overview\n\nExample project",
        encoding="utf-8",
    )
    (reports / "ai-summary.md").write_text(
        "# AI Repository Summary\n\nExample summary",
        encoding="utf-8",
    )
    (reports / "architecture.json").write_text(
        json.dumps(
            {
                "technologies": ["Python"],
                "architecture_patterns": ["src-based package layout"],
                "complexity_score": 3,
            }
        ),
        encoding="utf-8",
    )
    (reports / "code-analysis.json").write_text(
        json.dumps(
            {
                "app.py": {
                    "classes": ["App"],
                    "functions": ["main"],
                    "imports": [],
                }
            }
        ),
        encoding="utf-8",
    )
    (reports / "html-analysis.json").write_text(
        json.dumps({}),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    report = FinalReport().build()

    assert "Browser Code Explorer — Final Report" in report
    assert "Example project" in report
    assert "Python files analyzed: 1" in report
    assert "Classes found: 1" in report
    assert "Functions found: 1" in report
    assert "Python" in report