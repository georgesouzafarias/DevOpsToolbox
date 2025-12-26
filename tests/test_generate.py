from typer.testing import CliRunner

from devopstoolbox.generate import app

runner = CliRunner()


def test_generate_password_default_length():
    result = runner.invoke(app, [], standalone_mode=False)
    assert result.exception is None
    assert len(result.stdout.strip()) == 16
