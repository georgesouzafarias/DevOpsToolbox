from typer.testing import CliRunner

from devopstoolbox.main import app as main_app

runner = CliRunner()


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
