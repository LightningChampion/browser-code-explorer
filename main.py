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


async def run(repository_input: str, max_files: int) -> None:
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

        contents = await CodeReader(
            page,
            max_files=max_files,
        ).read_files(
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

        architecture = ArchitectureDetector().detect(
            tree.files,
            analysis,
        )

        dependency_builder = DependencyGraph()
        dependencies = dependency_builder.build(analysis)
        mermaid = dependency_builder.to_mermaid(dependencies)

        ai_summary = AISummaryGenerator().generate(
            repository_url,
            overview,
            architecture,
            analysis,
            tree.files,
            html_analysis,
        )

        reports_directory = Path("reports")
        reports_directory.mkdir(exist_ok=True)

        save_report(repository_url, tree, analysis)

        pages = "\n".join(
            (
                f"- `{path}` — "
                f"{data.get('title') or data.get('heading') or 'HTML page'}"
            )
            for path, data in html_analysis.items()
        )

        purpose = overview["purpose"]

        if html_analysis:
            home = (
                html_analysis.get("index.html")
                or html_analysis.get("index.updated.html")
                or next(iter(html_analysis.values()))
            )
            purpose = (
                home.get("summary")
                or home.get("heading")
                or purpose
            )

        technologies = "\n".join(
            f"- {item}"
            for item in architecture["technologies"]
        )

        architecture_patterns = "\n".join(
            f"- {item}"
            for item in architecture["architecture_patterns"]
        )

        overview_report = (
            "# Repository Overview\n\n"
            f"## Repository\n{repository_url}\n\n"
            f"## Purpose\n{purpose}\n\n"
            f"## Description\n{overview['description']}\n\n"
            f"## Technologies\n{technologies}\n\n"
            f"## Architecture\n{architecture_patterns}"
        )

        if pages:
            overview_report += f"\n\n## Website pages\n{pages}"

        overview_report += (
            "\n\n## Complexity\n"
            f"{architecture['complexity_score']}/10\n"
        )

        (reports_directory / "repository-overview.md").write_text(
            overview_report,
            encoding="utf-8",
        )
        (reports_directory / "ai-summary.md").write_text(
            ai_summary,
            encoding="utf-8",
        )
        (reports_directory / "file-contents.json").write_text(
            json.dumps(
                contents,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (reports_directory / "code-analysis.json").write_text(
            json.dumps(
                analysis,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (reports_directory / "html-analysis.json").write_text(
            json.dumps(
                html_analysis,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (reports_directory / "architecture.json").write_text(
            json.dumps(
                architecture,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (reports_directory / "dependencies.json").write_text(
            json.dumps(
                dependencies,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (reports_directory / "dependency-graph.md").write_text(
            f"# Dependency Graph\n\n```mermaid\n{mermaid}\n```\n",
            encoding="utf-8",
        )

        final_report = FinalReport().build()
        (reports_directory / "final-report.md").write_text(
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


def positive_integer(value: str) -> int:
    number = int(value)

    if number < 1:
        raise argparse.ArgumentTypeError(
            "must be a positive integer"
        )

    return number


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a public GitHub repository and generate reports."
        )
    )
    parser.add_argument(
        "repository",
        help="GitHub owner/repository or complete repository URL.",
    )
    parser.add_argument(
        "--max-files",
        type=positive_integer,
        default=15,
        help="Maximum number of repository files to read. Default: 15.",
    )

    args = parser.parse_args()

    try:
        asyncio.run(
            run(
                repository_input=args.repository,
                max_files=args.max_files,
            )
        )
    except ValueError as exc:
        print(f"Invalid repository: {exc}")
        raise SystemExit(2) from exc
    except PlaywrightError as exc:
        print(f"Browser or network error: {exc}")
        raise SystemExit(3) from exc
    except KeyboardInterrupt as exc:
        print("\nCancelled by user.")
        raise SystemExit(130) from exc
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()