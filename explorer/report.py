import json
from pathlib import Path

from explorer.navigator import RepositoryTree


def save_report(repository: str, tree: RepositoryTree):
    Path("reports").mkdir(exist_ok=True)

    data = {
        "repository": repository,
        "folders": tree.folders,
        "files": tree.files,
    }

    Path("reports/repository-tree.json").write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Repository Tree",
        "",
        f"Repository: {repository}",
        "",
        "## Folders",
        *[f"- `{folder}`" for folder in tree.folders],
        "",
        "## Important Files",
        *[f"- `{file}`" for file in tree.files],
    ]

    Path("reports/repository-tree.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
