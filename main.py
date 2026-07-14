import argparse
import asyncio
import json
from pathlib import Path

from explorer.analyzer import PythonAnalyzer
from explorer.browser import BrowserController
from explorer.github import normalize_repository
from explorer.navigator import GitHubNavigator
from explorer.reader import CodeReader
from explorer.report import save_report


async def run(repository_input: str):
    repository_url = normalize_repository(repository_input)
    browser = BrowserController()

    try:
        page = await browser.start()
        print(f"Opening: {repository_url}")

        navigator = GitHubNavigator(page)
        tree = await navigator.explore(repository_url)

        reader = CodeReader(page, max_files=15)
        contents = await reader.read_files(repository_url, tree.files)

        analyzer = PythonAnalyzer()
        analysis = analyzer.analyze_files(contents)

        save_report(repository_url, tree)

        Path("reports").mkdir(exist_ok=True)

        Path("reports/file-contents.json").write_text(
            json.dumps(contents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        Path("reports/code-analysis.json").write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"Folders found: {len(tree.folders)}")
        print(f"Important files found: {len(tree.files)}")
        print(f"Files read: {len(contents)}")
        print(f"Python files analyzed: {len(analysis)}")
        print("Report: reports/code-analysis.json")

    finally:
        await browser.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    asyncio.run(run(args.repository))


if __name__ == "__main__":
    main()
