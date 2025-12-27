"""Tests for devopstoolbox.main module."""

from unittest.mock import patch

from typer.testing import CliRunner

with patch("devopstoolbox.k8s.utils"):
    from devopstoolbox.main import app


runner = CliRunner()


class TestVersionCommand:
    """Tests for version command."""

    def test_version_displays_correctly(self):
        """Test that version command displays version string."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "v0.1.0" in result.output or "DevOpsToolbox" in result.output


class TestAppStructure:
    """Tests for CLI app structure."""

    def test_app_has_help(self):
        """Test that app displays help without arguments."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "k8s" in result.output
        assert "version" in result.output

    def test_k8s_subcommand_exists(self):
        """Test that k8s subcommand is available."""
        result = runner.invoke(app, ["k8s", "--help"])

        assert result.exit_code == 0
        assert "pods" in result.output
        assert "services" in result.output
        assert "certificates" in result.output

    def test_k8s_pods_subcommand_exists(self):
        """Test that k8s pods subcommand is available."""
        result = runner.invoke(app, ["k8s", "pods", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output
        assert "metrics" in result.output
        assert "unhealthy" in result.output

    def test_k8s_services_subcommand_exists(self):
        """Test that k8s services subcommand is available."""
        result = runner.invoke(app, ["k8s", "services", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output

    def test_k8s_certificates_subcommand_exists(self):
        """Test that k8s certificates subcommand is available."""
        result = runner.invoke(app, ["k8s", "certificates", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output
        assert "not-ready" in result.output
