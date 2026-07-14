from pathlib import PurePosixPath


class DependencyGraph:
    def build(
        self,
        analysis: dict[str, dict],
    ) -> dict[str, list[str]]:
        module_map = {
            self._path_to_module(path): path
            for path in analysis
        }

        graph: dict[str, list[str]] = {}

        for path, data in analysis.items():
            source_module = self._path_to_module(path)
            dependencies = []

            for imported in data.get("imports", []):
                resolved = self._resolve_import(source_module, imported)
                matched = self._match_import(resolved, module_map)

                if matched and matched != path:
                    dependencies.append(matched)

            graph[path] = sorted(set(dependencies))

        return graph

    def to_mermaid(self, graph: dict[str, list[str]]) -> str:
        lines = ["graph TD"]

        for source, targets in graph.items():
            source_id = self._node_id(source)
            lines.append(f'    {source_id}["{source}"]')

            for target in targets:
                target_id = self._node_id(target)
                lines.append(f'    {target_id}["{target}"]')
                lines.append(f"    {source_id} --> {target_id}")

        return "\n".join(dict.fromkeys(lines))

    def _path_to_module(self, path: str) -> str:
        clean = path

        if clean.startswith("src/"):
            clean = clean[4:]

        if clean.endswith("/__init__.py"):
            clean = clean[:-12]
        elif clean.endswith(".py"):
            clean = clean[:-3]

        return clean.replace("/", ".")

    def _resolve_import(self, source_module: str, imported: str) -> str:
        if not imported.startswith("."):
            return imported

        dots = len(imported) - len(imported.lstrip("."))
        remainder = imported.lstrip(".")

        source_parts = source_module.split(".")

        if not source_module.endswith("__init__"):
            source_parts = source_parts[:-1]

        keep = max(0, len(source_parts) - dots + 1)
        base = source_parts[:keep]

        if remainder:
            base.extend(remainder.split("."))

        return ".".join(base)

    def _match_import(
        self,
        imported: str,
        module_map: dict[str, str],
    ) -> str | None:
        if imported in module_map:
            return module_map[imported]

        candidates = [
            (module, path)
            for module, path in module_map.items()
            if imported.startswith(module + ".")
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda item: len(item[0]))[1]

    def _node_id(self, path: str) -> str:
        return "node_" + "".join(
            character if character.isalnum() else "_"
            for character in path
        )
