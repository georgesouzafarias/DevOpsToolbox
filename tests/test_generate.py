from typer.testing import CliRunner

from devopstoolbox.main import app as main_app

runner = CliRunner()


def test_generate_password_default_length():
    result = runner.invoke(main_app, ["misc", "generate"])
    assert result.exit_code == 0
    assert len(result.stdout.strip()) == 16


def test_generate_password_custom_length():
    result = runner.invoke(main_app, ["misc", "generate", "-l", "30"])
    assert result.exit_code == 0
    assert len(result.stdout.strip()) == 30


def test_generate_password_short_length():
    result = runner.invoke(main_app, ["misc", "generate", "--length", "8"])
    assert result.exit_code == 0
    assert len(result.stdout.strip()) == 8
