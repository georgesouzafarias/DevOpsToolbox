"""Tests for `json_validator` CLI integrated through `main.app`."""

import json

from typer.testing import CliRunner

from devopstoolbox.main import app


runner = CliRunner()


def test_validate_valid_json(tmp_path):
	"""Running `validate json` on a valid JSON file exits 0 and reports valid."""
	p = tmp_path / "valid.json"
	p.write_text(json.dumps({"key": "value"}))

	result = runner.invoke(app, ["validate", "json", str(p)])

	assert result.exit_code == 0
	assert "Valid JSON" in result.output or "✔ Valid JSON" in result.output


def test_validate_invalid_json(tmp_path):
	"""Running `validate json` on an invalid JSON file exits non-zero and reports invalid."""
	p = tmp_path / "invalid.json"
	p.write_text("{ not: valid, }")

	result = runner.invoke(app, ["validate", "json", str(p)])

	assert result.exit_code != 0
	assert "Invalid JSON" in result.output or "✖ Invalid JSON" in result.output

