"""Tests for devopstoolbox.main module."""

from unittest.mock import patch

from typer.testing import CliRunner

with patch("devopstoolbox.k8s.utils.config.load_kube_config"), patch("devopstoolbox.k8s.utils.config.list_kube_config_contexts") as mock_contexts:
    mock_contexts.return_value = ([], {"context": {"namespace": "default"}})
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

    def test_misc_subcommand_exists(self):
        """Test that misc subcommand is available."""
        result = runner.invoke(app, ["misc", "--help"])

        assert result.exit_code == 0
        assert "generate" in result.output
        assert "validate" in result.output
        assert "base64" in result.output

    def test_k8s_jobs_subcommand_exists(self):
        """Test that k8s jobs subcommand is available."""
        result = runner.invoke(app, ["k8s", "jobs", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output


class TestMainModule:
    """Tests for main module entry point."""

    def test_main_module_execution(self):
        """Test that the main module can be run as script."""
        import runpy
        import sys

        import pytest

        original_argv = sys.argv
        try:
            sys.argv = ["devopstoolbox", "--help"]
            # Run the module as __main__ - this will trigger the if __name__ == "__main__" block
            # SystemExit is expected because typer exits after showing help
            with pytest.raises(SystemExit) as exc_info:
                runpy.run_module("devopstoolbox.main", run_name="__main__", alter_sys=True)
            # Exit code 0 means success (help was displayed)
            assert exc_info.value.code == 0
        finally:
            sys.argv = original_argv
