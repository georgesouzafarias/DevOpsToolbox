import json
import pathlib
import tempfile

from typer.testing import CliRunner

from devopstoolbox.json_validator import app  # import your validator CLI app

runner = CliRunner()


def create_temp_file(content: str, suffix=".json"):
    """Helper to create a temporary file with given content"""
    tmp = tempfile.NamedTemporaryFile("w+", suffix=suffix, delete=False)
    tmp.write(content)
    tmp.flush()
    return tmp


def test_single_valid_file():
    tmp = create_temp_file(json.dumps({"key": "value"}))
    result = runner.invoke(app, [tmp.name])
    assert result.exit_code == 0
    assert "✔ Valid JSON" in result.output
    assert "Summary" in result.output


def test_single_invalid_file():
    tmp = create_temp_file("{ invalid json }")
    result = runner.invoke(app, [tmp.name])
    assert result.exit_code == 1
    assert "✖ Invalid JSON" in result.output
    assert "Error at line" in result.output
    assert "Summary" in result.output


def test_directory_with_mixed_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        valid_file = tmp / "valid.json"
        invalid_file = tmp / "invalid.json"

        valid_file.write_text(json.dumps({"ok": True}))
        invalid_file.write_text("{ invalid json }")

        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 1
        output = result.output
        assert "✔ Valid JSON" in output
        assert "✖ Invalid JSON" in output
        assert "Summary" in output


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(app, [tmpdir])
        assert result.exit_code == 0
        assert "⚠ No JSON files found" in result.output


def test_recursive_scan():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        subdir = tmp / "sub"
        subdir.mkdir()
        file1 = tmp / "file1.json"
        file2 = subdir / "file2.json"

        file1.write_text(json.dumps({"a": 1}))
        file2.write_text(json.dumps({"b": 2}))

        result = runner.invoke(app, [tmpdir, "--recursive"])
        assert result.exit_code == 0
        output = result.output
        assert output.count("✔ Valid JSON") == 2
        assert "Summary" in output
