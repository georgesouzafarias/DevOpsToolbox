"""Tests for devopstoolbox.validate module."""

import pytest
from typer.testing import CliRunner

from devopstoolbox.main import app as main_app
from devopstoolbox.validate import validate_yaml_file

runner = CliRunner()

VALID_YAML = """
key: value
list:
  - item1
  - item2
"""

INVALID_YAML = """
key: value
  bad indent: here
"""

MULTI_DOC_YAML = """
---
key1: value1
---
key2: value2
"""

EMPTY_YAML = ""

SIMPLE_YAML = "key: value\n"


@pytest.fixture
def valid_yaml_file(tmp_path):
    """Create a valid YAML file."""
    yaml_file = tmp_path / "valid.yaml"
    yaml_file.write_text(VALID_YAML)
    return yaml_file


@pytest.fixture
def invalid_yaml_file(tmp_path):
    """Create an invalid YAML file."""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(INVALID_YAML)
    return yaml_file


@pytest.fixture
def directory_with_valid_files(tmp_path):
    """Create a directory with valid YAML files."""
    (tmp_path / "valid1.yaml").write_text(SIMPLE_YAML)
    (tmp_path / "valid2.yml").write_text("name: test\n")
    return tmp_path


@pytest.fixture
def directory_with_mixed_files(tmp_path):
    """Create a directory with valid and invalid YAML files."""
    (tmp_path / "valid.yaml").write_text(SIMPLE_YAML)
    (tmp_path / "invalid.yaml").write_text(INVALID_YAML)
    return tmp_path


@pytest.fixture
def nested_directory(tmp_path):
    """Create a nested directory structure with YAML files."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "root.yaml").write_text("level: root\n")
    (subdir / "nested.yaml").write_text("level: nested\n")
    return tmp_path


class TestValidateYamlFile:
    def test_valid_yaml(self, valid_yaml_file):
        is_valid, error = validate_yaml_file(valid_yaml_file)
        assert is_valid is True
        assert error == ""

    def test_invalid_yaml(self, invalid_yaml_file):
        is_valid, error = validate_yaml_file(invalid_yaml_file)
        assert is_valid is False
        assert "Line" in error
        assert "Column" in error

    def test_multi_document_yaml(self, tmp_path):
        yaml_file = tmp_path / "multi.yaml"
        yaml_file.write_text(MULTI_DOC_YAML)
        is_valid, error = validate_yaml_file(yaml_file)
        assert is_valid is True
        assert error == ""

    def test_empty_yaml(self, tmp_path):
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text(EMPTY_YAML)
        is_valid, error = validate_yaml_file(yaml_file)
        assert is_valid is True
        assert error == ""


class TestValidateYamlCommand:
    def test_validate_single_valid_file(self, valid_yaml_file):
        result = runner.invoke(main_app, ["validate", "yaml", "-f", str(valid_yaml_file)])
        assert result.exit_code == 0
        assert "Valid" in result.stdout
        assert "1 valid, 0 invalid" in result.stdout

    def test_validate_single_invalid_file(self, invalid_yaml_file):
        result = runner.invoke(main_app, ["validate", "yaml", "-f", str(invalid_yaml_file)])
        assert result.exit_code == 1
        assert "Invalid" in result.stdout
        assert "0 valid, 1 invalid" in result.stdout

    def test_validate_directory(self, directory_with_valid_files):
        result = runner.invoke(main_app, ["validate", "yaml", "-d", str(directory_with_valid_files)])
        assert result.exit_code == 0
        assert "2 valid, 0 invalid" in result.stdout

    def test_validate_directory_mixed_results(self, directory_with_mixed_files):
        result = runner.invoke(main_app, ["validate", "yaml", "-d", str(directory_with_mixed_files)])
        assert result.exit_code == 1
        assert "1 valid, 1 invalid" in result.stdout

    def test_validate_empty_directory(self, tmp_path):
        result = runner.invoke(main_app, ["validate", "yaml", "-d", str(tmp_path)])
        assert result.exit_code == 0
        assert "No YAML files found" in result.stdout

    def test_no_file_or_directory_provided(self):
        result = runner.invoke(main_app, ["validate", "yaml"])
        assert result.exit_code == 1
        assert "You must provide either a file or a directory" in result.stdout

    def test_both_file_and_directory_provided(self, valid_yaml_file):
        result = runner.invoke(main_app, ["validate", "yaml", "-f", str(valid_yaml_file), "-d", str(valid_yaml_file.parent)])
        assert result.exit_code == 1
        assert "Provide either a file or a directory, not both" in result.stdout

    def test_validate_nested_directory(self, nested_directory):
        result = runner.invoke(main_app, ["validate", "yaml", "-d", str(nested_directory)])
        assert result.exit_code == 0
        assert "2 valid, 0 invalid" in result.stdout
