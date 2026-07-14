class DependencyGraph:
    def build(self, analysis: dict[str, dict]) -> dict[str, list[str]]:
        return {path: [] for path in analysis}

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

    def _node_id(self, path: str) -> str:
        return "node_" + "".join(
            character if character.isalnum() else "_"
            for character in path
        )
