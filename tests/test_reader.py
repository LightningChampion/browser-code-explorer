from explorer.reader import select_representative_files


def test_selects_representative_files_across_categories():
    paths = [
        "actions/harness/src/action.rs",
        "actions/harness/src/conductor.rs",
        "actions/harness/src/engine.rs",
        "README.md",
        "Cargo.toml",
        ".github/workflows/ci.yml",
        "tests/test_harness.rs",
        "docs/architecture.md",
        "src/main.rs",
        "src/lib.rs",
    ]

    selected = select_representative_files(paths, max_files=6)

    assert "README.md" in selected
    assert "Cargo.toml" in selected
    assert ".github/workflows/ci.yml" in selected
    assert "tests/test_harness.rs" in selected
    assert len(selected) == 6
