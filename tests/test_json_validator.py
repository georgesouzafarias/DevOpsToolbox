from typer.testing import CliRunner
from devopstoolbox.main import app
import pytest

runner = CliRunner()

def test_validate_json_single_success():
    # Test a known valid file (adjust path as needed)
    result = runner.invoke(app, ["validate", "json", "tests/validator_test/valid_1.json"])
    assert result.exit_code == 0
    assert "✅ Valid" in result.stdout

def test_validate_json_single_fail():
    # Test a known broken file
    result = runner.invoke(app, ["validate", "json", "tests/validator_test/expected_comma.json"])
    assert result.exit_code == 1
    assert "❌ Invalid" in result.stdout
    assert "Line" in result.stdout

def test_validate_json_directory():
    # Test the whole directory
    result = runner.invoke(app, ["validate", "json", "tests/validator_test", "--dir"])
    # If any of your 12 files are invalid, exit_code should be 1
    assert result.exit_code == 1 
    assert "Scanning directory" in result.stdout