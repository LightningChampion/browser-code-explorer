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


def test_project_structure_does_not_automatically_mean_maximum_complexity():
    files = [
        "src/flask/app.py",
        "src/flask/blueprints.py",
        "tests/test_app.py",
        "docs/index.rst",
        "examples/tutorial/app.py",
        "Dockerfile",
    ] + [f"src/flask/module_{index}.py" for index in range(44)]

    result = ArchitectureDetector().detect(files, {})

    assert result["complexity_score"] < 10


def test_detects_rust_project():
    files = [
        "Cargo.toml",
        "src/main.rs",
        "src/lib.rs",
        "tests/integration.rs",
    ]

    result = ArchitectureDetector().detect(files, {})

    assert "Rust" in result["technologies"]
    assert "Cargo" in result["technologies"]
