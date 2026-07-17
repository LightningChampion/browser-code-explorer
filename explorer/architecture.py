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
            "Rust": any(path.endswith(".rs") for path in files),
            "Cargo": any(
                path.lower().endswith(("cargo.toml", "cargo.lock"))
                for path in files
            ),
            "Flask": "flask" in imports or "src/flask" in text,
            "Django": "django" in imports,
            "FastAPI": "fastapi" in imports,
            "Pytest": "pytest" in imports or "tests/" in text,
            "Docker": "dockerfile" in text or ".devcontainer" in text,
            "HTML": any(path.endswith(".html") for path in files),
            "CSS": any(path.endswith(".css") for path in files),
            "JavaScript": any(path.endswith((".js", ".jsx")) for path in files),
            "TypeScript": any(path.endswith((".ts", ".tsx")) for path in files),
            "GitHub Actions": ".github/workflows" in text,
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
        if ".github/workflows" in text:
            patterns.append("automated deployment or CI workflow")
        if any(path.endswith(".html") for path in files):
            patterns.append("static website structure")
        if any(path.endswith(".css") for path in files):
            patterns.append("separate styling layer")
        if any(path.endswith((".js", ".jsx")) for path in files):
            patterns.append("browser-side scripting")
        if any("blueprint" in path.lower() for path in files):
            patterns.append("modular routing with blueprints")
        if any("app.py" in path.lower() for path in files):
            patterns.append("application-centered architecture")

        complexity = min(
            10,
            1 + len(technologies) // 2 + len(patterns) // 3 + len(files) // 50,
        )

        return {
            "technologies": technologies,
            "architecture_patterns": patterns,
            "complexity_score": complexity,
        }
