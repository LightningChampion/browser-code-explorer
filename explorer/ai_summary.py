class AISummaryGenerator:
    def generate(
        self,
        repository_url: str,
        overview: dict,
        architecture: dict,
        analysis: dict[str, dict],
        files: list[str],
    ) -> str:
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

        classes = sum(
            len(item.get("classes", []))
            for item in analysis.values()
        )

        functions = sum(
            len(item.get("functions", []))
            for item in analysis.values()
        )

        technologies = ", ".join(
            architecture.get("technologies", [])
        ) or "Unknown"

        patterns = "\n".join(
            f"- {item}"
            for item in architecture.get("architecture_patterns", [])
        ) or "- No clear pattern detected"

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

## Codebase size

- Python files analyzed: {len(analysis)}
- Classes found: {classes}
- Functions found: {functions}

## Important files

{reading_order}

## Recommended learning order

{reading_order}

## Complexity

{architecture.get("complexity_score", "Unknown")}/10

## Beginner friendliness

{"Low" if architecture.get("complexity_score", 0) >= 8 else "Medium"}

## Explanation

This repository appears to be organized around its core source package.
The most important files should be read before examples and tests.
The architecture detector found the main technologies and structural patterns,
while the AST analyzer identified classes, functions, and imports.
"""
