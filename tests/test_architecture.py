from explorer.architecture import ArchitectureDetector


def test_detects_python_project():
    files = [
        "src/app.py",
        "tests/test_app.py",
        "Dockerfile",
    ]

    result = ArchitectureDetector().detect(files, {})

    assert "Python" in result["technologies"]
    assert "Pytest" in result["technologies"]
    assert "Docker" in result["technologies"]


def test_detects_static_website():
    files = [
        "index.html",
        "styles.css",
        ".github/workflows/deploy.yml",
    ]

    result = ArchitectureDetector().detect(files, {})

    assert "HTML" in result["technologies"]
    assert "CSS" in result["technologies"]
    assert "GitHub Actions" in result["technologies"]
