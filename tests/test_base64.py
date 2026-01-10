import pytest
from typer.testing import CliRunner

from devopstoolbox.main import app as main_app

runner = CliRunner()


@pytest.fixture
def text_file(tmp_path):
    """Create a text file for testing."""
    file = tmp_path / "test.txt"
    file.write_text("hello world")
    return file


@pytest.fixture
def multiline_file(tmp_path):
    """Create a multiline file for testing."""
    file = tmp_path / "multiline.txt"
    file.write_text("line1\nline2\nline3")
    return file


class TestBase64Util:
    def test_base64_encode(self):
        """Encode string"""
        result = runner.invoke(main_app, ["misc", "base64", "-e", "banana"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "YmFuYW5h"

    def test_base64_decode(self):
        """Decode string"""
        result = runner.invoke(main_app, ["misc", "base64", "-d", "YmFuYW5h"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "banana"

    def test_decode_invalid_base64(self):
        """Validate invalid string"""
        result = runner.invoke(main_app, ["misc", "base64", "-d", "!!!invalid!!!"])
        assert result.exit_code == 1
        assert "Invalid base64" in result.stdout

    def test_encode_file(self, text_file):
        """Encode file content to base64"""
        result = runner.invoke(main_app, ["misc", "base64", "-f", str(text_file)])
        assert result.exit_code == 0
        assert result.stdout.strip() == "aGVsbG8gd29ybGQ="

    def test_encode_multiline_file(self, multiline_file):
        """Encode multiline file content to base64"""
        result = runner.invoke(main_app, ["misc", "base64", "-f", str(multiline_file)])
        assert result.exit_code == 0
        assert result.stdout.strip() == "bGluZTEKbGluZTIKbGluZTM="

    def test_file_not_found(self, tmp_path):
        """Test with non-existent file"""
        result = runner.invoke(main_app, ["misc", "base64", "-f", str(tmp_path / "nonexistent.txt")])
        assert result.exit_code != 0
