class ArchitectureDetector:
    def detect(self, files: list[str], analysis: dict[str, dict]) -> dict:
        lower_files = [path.lower() for path in files]
        imports = {
            item.lower()
            for file_data in analysis.values()
            for item in file_data.get("imports", [])
            if item
        }

        def has_ext(*exts: str) -> bool:
            return any(path.endswith(exts) for path in lower_files)

        def has_file(*names: str) -> bool:
            return any(path in names for path in lower_files)

        def has_path_fragment(*fragments: str) -> bool:
            return any(
                any(fragment in path for fragment in fragments)
                for path in lower_files
            )

        technologies = []

        checks = [
            ("Python", has_ext(".py") or "pytest" in imports or "flask" in imports or "django" in imports or "fastapi" in imports),
            ("Go", has_ext(".go") or has_file("go.mod", "go.sum")),
            ("Rust", has_ext(".rs") or has_file("cargo.toml", "cargo.lock")),
            ("Cargo", has_file("cargo.toml", "cargo.lock")),
            ("JavaScript", has_ext(".js", ".jsx") or has_file("package.json")),
            ("TypeScript", has_ext(".ts", ".tsx") or has_file("tsconfig.json")),
            ("Java", has_ext(".java") or has_file("pom.xml", "build.gradle", "build.gradle.kts")),
            ("C/C++", has_ext(".c", ".h", ".cpp", ".hpp", ".cc", ".cxx") or has_file("cmakelists.txt")),
            ("Flask", "flask" in imports or has_path_fragment("src/flask")),
            ("Django", "django" in imports or has_path_fragment("django")),
            ("FastAPI", "fastapi" in imports),
            ("Pytest", "pytest" in imports or any(path.startswith("tests/") and path.endswith(".py") for path in lower_files)),
            ("Docker", has_file("dockerfile") or has_path_fragment(".devcontainer")),
            ("HTML", has_ext(".html", ".htm")),
            ("CSS", has_ext(".css")),
            ("GitHub Actions", has_path_fragment(".github/workflows/")),
        ]

        for name, found in checks:
            if found:
                technologies.append(name)

        patterns = []

        if has_path_fragment("src/"):
            patterns.append("src-based package layout")
        if has_path_fragment("tests/"):
            patterns.append("separate test suite")
        if has_path_fragment("docs/"):
            patterns.append("documentation-driven project")
        if has_path_fragment("examples/"):
            patterns.append("example applications")
        if has_path_fragment(".github/workflows/"):
            patterns.append("automated deployment or CI workflow")
        if has_ext(".html", ".htm"):
            patterns.append("static website structure")
        if has_ext(".css"):
            patterns.append("separate styling layer")
        if has_ext(".js", ".jsx"):
            patterns.append("browser-side scripting")
        if has_path_fragment("blueprint"):
            patterns.append("modular routing with blueprints")
        if has_path_fragment("app.py"):
            patterns.append("application-centered architecture")
        if has_file("go.mod"):
            patterns.append("go module project")
        if has_path_fragment("cmd/"):
            patterns.append("command-line tool layout")
        if has_file("pom.xml", "build.gradle", "build.gradle.kts"):
            patterns.append("java build-based project")
        if has_file("cmakelists.txt"):
            patterns.append("c/c++ native build")

        complexity = min(
            10,
            1 + len(technologies) // 2 + len(patterns) // 3 + len(files) // 50,
        )

        return {
            "technologies": technologies,
            "architecture_patterns": patterns,
            "complexity_score": complexity,
        }
