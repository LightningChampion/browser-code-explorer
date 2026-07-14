import json
from pathlib import Path

from explorer.navigator import RepositoryTree


def save_report(
    repository: str,
    tree: RepositoryTree,
    analysis: dict[str, dict] | None = None,
):
    Path("reports").mkdir(exist_ok=True)

    data = {
        "repository": repository,
        "folders": tree.folders,
        "files": tree.files,
        "analysis": analysis or {},
    }

    Path("reports/repository-data.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    languages = sorted(
        {
            path.rsplit(".", 1)[-1]
            for path in tree.files
            if "." in path
        }
    )

    total_classes = sum(
        len(item.get("classes", []))
        for item in (analysis or {}).values()
    )

    total_functions = sum(
        len(item.get("functions", []))
        for item in (analysis or {}).values()
    )

    lines = [
        "# Browser Code Explorer Report",
        "",
        f"Repository: {repository}",
        "",
        "## Summary",
        f"- Folders found: {len(tree.folders)}",
        f"- Important files found: {len(tree.files)}",
        f"- Python files analyzed: {len(analysis or {})}",
        f"- Classes found: {total_classes}",
        f"- Functions found: {total_functions}",
        f"- File types: {', '.join(languages) or 'Unknown'}",
        "",
        "## Important folders",
        *[f"- `{folder}`" for folder in tree.folders[:30]],
        "",
        "## Important files",
        *[f"- `{file}`" for file in tree.files[:30]],
    ]

    Path("reports/project-summary.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
