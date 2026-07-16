import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import Error as PlaywrightError

from explorer.ai_summary import AISummaryGenerator
from explorer.analyzer import PythonAnalyzer
from explorer.architecture import ArchitectureDetector
from explorer.browser import BrowserController
from explorer.dependency import DependencyGraph
from explorer.final_report import FinalReport
from explorer.github import normalize_repository
from explorer.html_analyzer import HtmlAnalyzer
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

        overview = await RepositoryOverview(page).collect(repository_url)

        tree = await GitHubNavigator(page).explore(repository_url)

        if not tree.folders and not tree.files:
            raise ValueError(
                "Repository not found, inaccessible, private, or empty."
            )

        contents = await CodeReader(page, max_files=15).read_files(
            repository_url,
            tree.files,
        )

        analysis = PythonAnalyzer().analyze_files(contents)

        html_analyzer = HtmlAnalyzer()
        html_analysis = {
            path: html_analyzer.analyze(content)
            for path, content in contents.items()
            if path.endswith(".html")
        }

        architecture = ArchitectureDetector().detect(tree.files, analysis)

        dependencies = DependencyGraph().build(analysis)
        mermaid = DependencyGraph().to_mermaid(dependencies)

        ai_summary = AISummaryGenerator().generate(
            repository_url,
            overview,
            architecture,
            analysis,
            tree.files,
            html_analysis,
        )

        save_report(repository_url, tree, analysis)
        Path("reports").mkdir(exist_ok=True)

        pages = "\n".join(
            f"- `{path}` — {data.get('title') or data.get('heading') or 'HTML page'}"
            for path, data in html_analysis.items()
        )

        purpose = overview["purpose"]
        if html_analysis:
            home = (
                html_analysis.get("index.html")
                or html_analysis.get("index.updated.html")
                or next(iter(html_analysis.values()))
            )
            purpose = home.get("summary") or home.get("heading") or purpose

        overview_report = (
            "# Repository Overview\n\n"
            f"## Repository\n{repository_url}\n\n"
            f"## Purpose\n{purpose}\n\n"
            f"## Description\n{overview['description']}\n\n"
            f"## Technologies\n"
            + "\n".join(
                f"- {item}" for item in architecture["technologies"]
            )
            + "\n\n## Architecture\n"
            + "\n".join(
                f"- {item}"
                for item in architecture["architecture_patterns"]
            )
        )

        if pages:
            overview_report += f"\n\n## Website pages\n{pages}"

        overview_report += (
            f"\n\n## Complexity\n"
            f"{architecture['complexity_score']}/10\n"
        )

        Path("reports/repository-overview.md").write_text(
            overview_report,
            encoding="utf-8",
        )
        Path("reports/ai-summary.md").write_text(ai_summary, encoding="utf-8")
        Path("reports/file-contents.json").write_text(
            json.dumps(contents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        Path("reports/code-analysis.json").write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        Path("reports/html-analysis.json").write_text(
            json.dumps(html_analysis, indent=2, ensure_ascii=False),
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
            f"# Dependency Graph\n\n```mermaid\n{mermaid}\n```\n",
            encoding="utf-8",
        )

        final_report = FinalReport().build()
        Path("reports/final-report.md").write_text(
            final_report,
            encoding="utf-8",
        )

        print(f"Folders found: {len(tree.folders)}")
        print(f"Important files found: {len(tree.files)}")
        print(f"Files read: {len(contents)}")
        print(f"Python files analyzed: {len(analysis)}")
        print(f"HTML files analyzed: {len(html_analysis)}")
        print(
            "Technologies detected: "
            + ", ".join(architecture["technologies"])
        )
        print("Overview: reports/repository-overview.md")
        print("AI summary: reports/ai-summary.md")
        print("Final report: reports/final-report.md")

    finally:
        await browser.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    try:
        asyncio.run(run(args.repository))
    except ValueError as exc:
        print(f"Invalid repository: {exc}")
        raise SystemExit(2)
    except PlaywrightError as exc:
        print(f"Browser or network error: {exc}")
        raise SystemExit(3)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        raise SystemExit(130)
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
