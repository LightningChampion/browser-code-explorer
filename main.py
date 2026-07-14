import argparse
import asyncio
import json
from pathlib import Path

from explorer.analyzer import PythonAnalyzer
from explorer.architecture import ArchitectureDetector
from explorer.ai_summary import AISummaryGenerator
from explorer.browser import BrowserController
from explorer.dependency import DependencyGraph
from explorer.github import normalize_repository
from explorer.navigator import GitHubNavigator
from explorer.overview import RepositoryOverview
from explorer.reader import CodeReader
from explorer.report import save_report


async def run(repository_input: str):
    repository_url = normalize_repository(repository_input)
    browser = BrowserController()

    try:
        page = await browser.start()
        print(f"Opening: {repository_url}")

        overview_reader = RepositoryOverview(page)
        overview = await overview_reader.collect(repository_url)

        navigator = GitHubNavigator(page)
        tree = await navigator.explore(repository_url)

        reader = CodeReader(page, max_files=15)
        contents = await reader.read_files(repository_url, tree.files)

        analyzer = PythonAnalyzer()
        analysis = analyzer.analyze_files(contents)

        detector = ArchitectureDetector()
        architecture = detector.detect(tree.files, analysis)

        summary_generator = AISummaryGenerator()
        ai_summary = summary_generator.generate(
            repository_url,
            overview,
            architecture,
            analysis,
            tree.files,
        )

        dependency_builder = DependencyGraph()
        dependencies = dependency_builder.build(analysis)
        mermaid = dependency_builder.to_mermaid(dependencies)

        save_report(repository_url, tree, analysis)

        Path("reports").mkdir(exist_ok=True)

        Path("reports/ai-summary.md").write_text(
            ai_summary,
            encoding="utf-8",
        )

        Path("reports/repository-overview.md").write_text(
            "# Repository Overview\n\n"
            f"## Repository\n{repository_url}\n\n"
            f"## Purpose\n{overview['purpose']}\n\n"
            f"## Description\n{overview['description']}\n\n"
            "## Technologies\n"
            + "\n".join(f"- {item}" for item in architecture["technologies"])
            + "\n\n## Architecture\n"
            + "\n".join(
                f"- {item}" for item in architecture["architecture_patterns"]
            )
            + f"\n\n## Complexity\n{architecture['complexity_score']}/10\n",
            encoding="utf-8",
        )

        Path("reports/file-contents.json").write_text(
            json.dumps(contents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        Path("reports/code-analysis.json").write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        Path("reports/architecture.json").write_text(
            json.dumps(architecture, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        Path("reports/dependencies.json").write_text(
            json.dumps(dependencies, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        Path("reports/dependency-graph.md").write_text(
            "# Dependency Graph\n\n```mermaid\n"
            + mermaid
            + "\n```\n",
            encoding="utf-8",
        )

        print(f"Folders found: {len(tree.folders)}")
        print(f"Important files found: {len(tree.files)}")
        print(f"Files read: {len(contents)}")
        print(f"Python files analyzed: {len(analysis)}")
        print(f"Technologies detected: {', '.join(architecture['technologies'])}")
        print("Overview: reports/repository-overview.md")
        print("AI summary: reports/ai-summary.md")

    finally:
        await browser.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    asyncio.run(run(args.repository))


if __name__ == "__main__":
    main()
