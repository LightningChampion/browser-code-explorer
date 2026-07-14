class ArchitectureDetector:
    def detect(self, files: list[str], analysis: dict[str, dict]) -> dict:
        text = "\n".join(files).lower()
        technologies = []

        if any(path.endswith(".py") for path in files):
            technologies.append("Python")
        if any(path.endswith(".html") for path in files):
            technologies.append("HTML")
        if any(path.endswith(".css") for path in files):
            technologies.append("CSS")
        if any(path.endswith((".js", ".jsx")) for path in files):
            technologies.append("JavaScript")
        if ".github/workflows" in text:
            technologies.append("GitHub Actions")

        patterns = []

        if ".github/workflows" in text:
            patterns.append("automated deployment or CI workflow")
        if any(path.endswith(".html") for path in files):
            patterns.append("static website structure")
        if any(path.endswith(".css") for path in files):
            patterns.append("separate styling layer")
        if any(path.endswith((".js", ".jsx")) for path in files):
            patterns.append("browser-side scripting")

        return {
            "technologies": technologies,
            "architecture_patterns": patterns,
            "complexity_score": max(1, min(10, 1 + len(technologies))),
        }
