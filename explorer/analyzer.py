import ast


class PythonAnalyzer:
    def analyze_files(self, contents: dict[str, str]) -> dict[str, dict]:
        results = {}

        for path, content in contents.items():
            if not path.endswith(".py"):
                continue

            results[path] = self.analyze_file(content)

        return results

    def analyze_file(self, content: str) -> dict:
        try:
            tree = ast.parse(content)
        except SyntaxError as exc:
            return {
                "error": str(exc),
                "lines": len(content.splitlines()),
                "imports": [],
                "classes": [],
                "functions": [],
            }

        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

        return {
            "lines": len(content.splitlines()),
            "imports": sorted(set(imports)),
            "classes": sorted(set(classes)),
            "functions": sorted(set(functions)),
        }
