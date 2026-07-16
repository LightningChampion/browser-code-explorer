from explorer.dependency import DependencyGraph


def test_dependency_graph_builds_internal_relationships():
    analysis = {
        "app.py": {
            "imports": ["config", "services"],
            "classes": [],
            "functions": [],
        },
        "config.py": {
            "imports": [],
            "classes": [],
            "functions": [],
        },
        "services.py": {
            "imports": ["config"],
            "classes": [],
            "functions": [],
        },
    }

    graph = DependencyGraph().build(analysis)

    assert graph["app.py"] == ["config.py", "services.py"]
    assert graph["services.py"] == ["config.py"]


def test_dependency_graph_creates_mermaid_output():
    graph = {
        "app.py": ["config.py"],
        "config.py": [],
    }

    mermaid = DependencyGraph().to_mermaid(graph)

    assert "graph TD" in mermaid
    assert "app.py" in mermaid
    assert "config.py" in mermaid
    assert "-->" in mermaid