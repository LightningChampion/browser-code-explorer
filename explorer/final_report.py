import json
from pathlib import Path


class FinalReport:
    def _join_items(self, items: list[str], empty: str = "- None detected") -> str:
        return "\n".join(f"- {item}" for item in items) or empty

    def _describe_repository(self, technologies: list[str], patterns: list[str]) -> str:
        parts = []

        if "Go" in technologies:
            parts.append("This is primarily a Go project.")
        if "Rust" in technologies:
            parts.append("Rust source files are present.")
        if "Python" in technologies:
            parts.append("Python source files are present.")
        if "JavaScript" in technologies or "TypeScript" in technologies:
            parts.append("It also includes JavaScript or TypeScript.")
        if "Docker" in technologies:
            parts.append("Docker is used for containerized workflows.")

        if "command-line tool layout" in patterns:
            parts.append("The code is organized around executables under cmd/.")
        if "go module project" in patterns:
            parts.append("The project uses Go modules.")
        if "separate test suite" in patterns:
            parts.append("It includes a separate test suite.")
        if "automated deployment or CI workflow" in patterns:
            parts.append("It has CI or deployment workflow support.")
        if "example applications" in patterns:
            parts.append("It also contains example or auxiliary applications.")
        if "src-based package layout" in patterns:
            parts.append("It follows a src-based package layout.")

        if not parts:
            return (
                "The available signals are not strong enough to describe the "
                "repository confidently."
            )

        return " ".join(parts)

    def build(self) -> str:
        reports = Path("reports")

        overview = (reports / "repository-overview.md").read_text(encoding="utf-8")
        summary = (reports / "ai-summary.md").read_text(encoding="utf-8")

        architecture = json.loads((reports / "architecture.json").read_text(encoding="utf-8"))
        code = json.loads((reports / "code-analysis.json").read_text(encoding="utf-8"))
        html = json.loads((reports / "html-analysis.json").read_text(encoding="utf-8"))

        source_files = len(code)
        classes = sum(len(data.get("classes", [])) for data in code.values())
        functions = sum(len(data.get("functions", [])) for data in code.values())

        technologies_list = architecture.get("technologies", [])
        patterns_list = architecture.get("architecture_patterns", [])

        technologies = self._join_items(technologies_list)
        patterns = self._join_items(patterns_list)
        repository_type = self._describe_repository(technologies_list, patterns_list)

        return f"""# Browser Code Explorer — Final Report

## Repository Overview

{overview}

---

## What this repository appears to be

{repository_type}

---

## Concise Summary

{summary}

---

## Statistics

- Analyzed source files: {source_files}`n- Python files analyzed: {source_files}
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
