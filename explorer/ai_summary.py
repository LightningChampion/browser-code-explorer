class AISummaryGenerator:
    def generate(
        self,
        repository_url: str,
        overview: dict,
        architecture: dict,
        analysis: dict[str, dict],
        files: list[str],
        html_analysis: dict[str, dict],
    ) -> str:
        technologies = ", ".join(
            architecture.get("technologies", [])
        ) or "Unknown"

        patterns = "\n".join(
            f"- {item}"
            for item in architecture.get("architecture_patterns", [])
        ) or "- No clear pattern detected"

        if html_analysis:
            home = (
                html_analysis.get("index.html")
                or html_analysis.get("index.updated.html")
                or next(iter(html_analysis.values()))
            )

            purpose = home.get("summary") or home.get("heading") or overview.get("purpose", "")
            page_lines = "\n".join(
                f"- `{path}` — {data.get('title') or data.get('heading') or 'HTML page'}"
                for path, data in html_analysis.items()
            )

            reading_order = "\n".join(
                f"{index}. `{path}`"
                for index, path in enumerate(
                    [
                        path
                        for path in (
                            "README.md",
                            "index.html",
                            "Styles.css",
                            "services.html",
                            "gallery.html",
                            "contact.html",
                        )
                        if path in files
                    ],
                    start=1,
                )
            )

            return f"""# AI Repository Summary

## Repository

{repository_url}

## What is this project?

{purpose}

## Main technologies

{technologies}

## Architecture

{patterns}

## Main pages

{page_lines}

## Recommended learning order

{reading_order or "No reading order detected."}

## Complexity

{architecture.get("complexity_score", "Unknown")}/10

## Beginner friendliness

High

## Explanation

This repository is a static website. The HTML pages define the content and navigation,
the CSS files control the design, and GitHub Actions is used for automated deployment.
"""

        important_files = [
            path for path in files
            if path.endswith((
                "app.py",
                "main.py",
                "cli.py",
                "config.py",
                "ctx.py",
                "helpers.py",
                "blueprints.py",
                "__init__.py",
            ))
        ][:10]

        reading_order = "\n".join(
            f"{index}. `{path}`"
            for index, path in enumerate(important_files, start=1)
        ) or "No reading order detected."

        return f"""# AI Repository Summary

## Repository

{repository_url}

## What is this project?

{overview.get("purpose", "Purpose could not be determined.")}

## Main technologies

{technologies}

## Architecture

{patterns}

## Recommended learning order

{reading_order}

## Complexity

{architecture.get("complexity_score", "Unknown")}/10
"""
