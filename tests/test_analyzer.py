from explorer.analyzer import PythonAnalyzer


def test_python_analyzer_extracts_structure():
    files = {
        "example.py": """
import os
from pathlib import Path


class Example:
    def method(self):
        return True


def helper():
    return Path.cwd()
"""
    }

    result = PythonAnalyzer().analyze_files(files)
    analysis = result["example.py"]

    assert "os" in analysis["imports"]
    assert "pathlib" in analysis["imports"]
    assert "Example" in analysis["classes"]
    assert "method" in analysis["functions"]
    assert "helper" in analysis["functions"]