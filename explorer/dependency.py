from pathlib import PurePosixPath


class DependencyGraph:
    def build(self, analysis: dict[str, dict]) -> dict[str, list[str]]:
        module_map = {
            self._module_name(path): path
            for path in analysis
            if path.endswith(".py")
        }

        graph: dict[str, list[str]] = {}

        for source_path, data in analysis.items():
            targets = []

            for imported in data.get("imports", []):
                target = self._match_import(imported, module_map)

                if target and target != source_path and target not in targets:
                    targets.append(target)

            graph[source_path] = targets

        return graph

    def to_mermaid(self, graph: dict[str, list[str]]) -> str:
        if not graph:
            return 'graph TD\n    empty["No Python dependencies detected"]'

        lines = ["graph TD"]

        for source, targets in graph.items():
            source_id = self._node_id(source)
            lines.append(f'    {source_id}["{source}"]')

            for target in targets:
                target_id = self._node_id(target)
                lines.append(f'    {target_id}["{target}"]')
                lines.append(f"    {source_id} --> {target_id}")

        return "\n".join(lines)

    def _module_name(self, path: str) -> str:
        file_path = PurePosixPath(path)

        if file_path.name == "__init__.py":
            parts = file_path.parent.parts
        else:
            parts = file_path.with_suffix("").parts

        if "src" in parts:
            parts = parts[parts.index("src") + 1 :]

        return ".".join(parts)

    def _match_import(
        self,
        imported: str,
        module_map: dict[str, str],
    ) -> str | None:
        imported = imported.lstrip(".")

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