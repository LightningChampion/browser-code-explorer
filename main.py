import argparse
import asyncio

from explorer.browser import BrowserController
from explorer.github import normalize_repository
from explorer.navigator import GitHubNavigator
from explorer.report import save_report


async def run(repository_input: str):
    repository_url = normalize_repository(repository_input)
    browser = BrowserController()

    try:
        page = await browser.start()
        navigator = GitHubNavigator(page)

        print(f"Opening: {repository_url}")
        tree = await navigator.explore(repository_url)

        save_report(repository_url, tree)

        print(f"Folders found: {len(tree.folders)}")
        print(f"Important files found: {len(tree.files)}")
        print("Report: reports/repository-tree.md")
    finally:
        await browser.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    asyncio.run(run(args.repository))


if __name__ == "__main__":
    main()
