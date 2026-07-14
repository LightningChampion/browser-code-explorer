class ArchitectureDetector:
    def detect(self, files: list[str], analysis: dict[str, dict]) -> dict:
        text = "\n".join(files).lower()
        imports = {
            item
            for file_data in analysis.values()
            for item in file_data.get("imports", [])
        }

        technologies = []

        checks = {
            "Python": any(path.endswith(".py") for path in files),
            "Flask": "flask" in imports or "src/flask" in text,
            "Django": "django" in imports,
            "FastAPI": "fastapi" in imports,
            "Pytest": "pytest" in imports or "tests/" in text,
            "Docker": "dockerfile" in text or ".devcontainer" in text,
            "JavaScript": any(path.endswith((".js", ".jsx")) for path in files),
            "TypeScript": any(path.endswith((".ts", ".tsx")) for path in files),
        }

        for name, found in checks.items():
            if found:
                technologies.append(name)

        patterns = []

        if "src/" in text:
            patterns.append("src-based package layout")
        if "tests/" in text:
            patterns.append("separate test suite")
        if "docs/" in text:
            patterns.append("documentation-driven project")
        if "examples/" in text:
            patterns.append("example applications")
        if any("blueprint" in path.lower() for path in files):
            patterns.append("modular routing with blueprints")
        if any("app.py" in path.lower() for path in files):
            patterns.append("application-centered architecture")

        complexity = min(
            10,
            2
            + len(technologies)
            + len(patterns) // 2
            + len(files) // 25,
        )

        return {
            "technologies": technologies,
            "architecture_patterns": patterns,
            "complexity_score": complexity,
        }
