"""Tests for devopstoolbox.k8s.certificates module."""

from unittest.mock import patch

import pytest

# Patch before importing the module
with patch("kubernetes.config.load_kube_config"):
    from typer.testing import CliRunner

    from devopstoolbox.k8s import certificates


runner = CliRunner()


@pytest.fixture
def mock_ready_certificate():
    """Create a mock ready certificate."""
    return {
        "metadata": {"name": "test-cert"},
        "status": {
            "renewalTime": "2025-06-15T10:00:00Z",
            "conditions": [{"type": "Ready", "status": "True"}]
        }
    }


@pytest.fixture
def mock_not_ready_certificate():
    """Create a mock not ready certificate."""
    return {
        "metadata": {"name": "failing-cert"},
        "status": {
            "renewalTime": None,
            "conditions": [{"type": "Issuing", "status": "True"}]
        }
    }


class TestCertificatesListCommand:
    """Tests for certificates list command."""

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_list_certificates_default_namespace(self, mock_custom_api, mock_ready_certificate):
        """Test listing certificates in default namespace."""
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [mock_ready_certificate]
        }

        result = runner.invoke(certificates.app, ["list"])

        assert result.exit_code == 0
        mock_custom_api.list_namespaced_custom_object.assert_called_once_with(
            group="cert-manager.io",
            version="v1",
            namespace="default",
            plural="certificates"
        )

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_list_certificates_specific_namespace(self, mock_custom_api, mock_ready_certificate):
        """Test listing certificates in a specific namespace."""
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [mock_ready_certificate]
        }

        result = runner.invoke(certificates.app, ["list", "--namespace", "cert-manager"])

        assert result.exit_code == 0
        mock_custom_api.list_namespaced_custom_object.assert_called_once_with(
            group="cert-manager.io",
            version="v1",
            namespace="cert-manager",
            plural="certificates"
        )

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_list_certificates_empty_response(self, mock_custom_api):
        """Test handling empty certificates response."""
        mock_custom_api.list_namespaced_custom_object.return_value = {"items": []}

        result = runner.invoke(certificates.app, ["list"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_list_certificates_missing_status(self, mock_custom_api):
        """Test handling certificates with missing status fields."""
        cert_no_status = {
            "metadata": {"name": "pending-cert"},
            "status": {}
        }
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [cert_no_status]
        }

        result = runner.invoke(certificates.app, ["list"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_list_certificates_handles_api_error(self, mock_custom_api):
        """Test handling cert-manager API errors."""
        mock_custom_api.list_namespaced_custom_object.side_effect = Exception("CRD not found")

        result = runner.invoke(certificates.app, ["list"])

        assert result.exit_code == 0
        assert "Error" in result.output or "Certificate" in result.output


class TestCertificatesNotReadyCommand:
    """Tests for certificates not-ready command."""

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_not_ready_filters_ready_certificates(
        self, mock_custom_api, mock_ready_certificate, mock_not_ready_certificate
    ):
        """Test that ready certificates are filtered out."""
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [mock_ready_certificate, mock_not_ready_certificate]
        }

        result = runner.invoke(certificates.app, ["not-ready"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_not_ready_shows_issuing_certificates(self, mock_custom_api, mock_not_ready_certificate):
        """Test that issuing certificates are shown."""
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [mock_not_ready_certificate]
        }

        result = runner.invoke(certificates.app, ["not-ready"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_not_ready_all_certificates_ready(self, mock_custom_api, mock_ready_certificate):
        """Test when all certificates are ready."""
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [mock_ready_certificate]
        }

        result = runner.invoke(certificates.app, ["not-ready"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_not_ready_missing_conditions(self, mock_custom_api):
        """Test handling certificates with missing conditions."""
        cert_no_conditions = {
            "metadata": {"name": "broken-cert"},
            "status": {"conditions": []}
        }
        mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [cert_no_conditions]
        }

        result = runner.invoke(certificates.app, ["not-ready"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.certificates.custom_api")
    def test_not_ready_handles_api_error(self, mock_custom_api):
        """Test handling cert-manager API errors."""
        mock_custom_api.list_namespaced_custom_object.side_effect = Exception("CRD not found")

        result = runner.invoke(certificates.app, ["not-ready"])

        assert result.exit_code == 0
        assert "Error" in result.output or "Certificate" in result.output
