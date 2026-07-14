from pathlib import PurePosixPath


class DependencyGraph:
    def build(
        self,
        analysis: dict[str, dict],
    ) -> dict[str, list[str]]:
        module_map = {}

        for path in analysis:
            module = self._path_to_module(path)
            module_map[module] = path

        graph: dict[str, list[str]] = {}

        for path, data in analysis.items():
            dependencies = []

            for imported in data.get("imports", []):
                matched = self._match_import(imported, module_map)

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

    def _match_import(
        self,
        imported: str,
        module_map: dict[str, str],
    ) -> str | None:
        imported = imported.lstrip(".")

        for module, path in module_map.items():
            if imported == module or imported.startswith(module + "."):
                return path

        return None

    def _node_id(self, path: str) -> str:
        return (
            "node_"
            + "".join(
                character if character.isalnum() else "_"
                for character in path
            )
        )
