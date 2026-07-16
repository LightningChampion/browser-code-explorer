import json
from pathlib import Path


class FinalReport:
    def build(self) -> str:
        reports = Path("reports")

        overview = (reports / "repository-overview.md").read_text(
            encoding="utf-8"
        )
        summary = (reports / "ai-summary.md").read_text(
            encoding="utf-8"
        )

        architecture = json.loads(
            (reports / "architecture.json").read_text(encoding="utf-8")
        )
        code = json.loads(
            (reports / "code-analysis.json").read_text(encoding="utf-8")
        )
        html = json.loads(
            (reports / "html-analysis.json").read_text(encoding="utf-8")
        )

        classes = sum(len(data.get("classes", [])) for data in code.values())
        functions = sum(len(data.get("functions", [])) for data in code.values())

        technologies = "\n".join(
            f"- {item}" for item in architecture.get("technologies", [])
        ) or "- None detected"

        patterns = "\n".join(
            f"- {item}"
            for item in architecture.get("architecture_patterns", [])
        ) or "- None detected"

        return f"""# Browser Code Explorer — Final Report

{overview}

---

## Concise Summary

{summary}

---

## Statistics

- Python files analyzed: {len(code)}
- HTML files analyzed: {len(html)}
- Classes found: {classes}
- Functions found: {functions}
- Complexity: {architecture.get("complexity_score", "Unknown")}/10

## Technologies

{technologies}

## Architecture Patterns

{patterns}

## Detailed Reports

- `code-analysis.json`
- `html-analysis.json`
- `architecture.json`
- `dependencies.json`
- `dependency-graph.md`
- `file-contents.json`
"""
