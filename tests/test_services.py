"""Tests for devopstoolbox.k8s.services module."""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from devopstoolbox.k8s import services

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_kube_config():
    """Mock kubeconfig loading for all tests."""
    with patch("devopstoolbox.k8s.utils.load_kube_config"):
        yield


@pytest.fixture
def mock_service():
    """Create a mock service object."""
    service = Mock()
    service.metadata.namespace = "default"
    service.metadata.name = "test-service"
    service.spec.type = "ClusterIP"
    service.spec.internal_traffic_policy = "Cluster"
    return service


class TestServicesListCommand:
    """Tests for services list command."""

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_default_namespace(self, mock_api, mock_service):
        """Test listing services in default namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_services = Mock()
        mock_services.items = [mock_service]
        mock_v1.list_namespaced_service.return_value = mock_services

        result = runner.invoke(services.app, ["-n", "default"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_service.assert_called_once_with("default", watch=False)

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_specific_namespace(self, mock_api, mock_service):
        """Test listing services in a specific namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_services = Mock()
        mock_services.items = [mock_service]
        mock_v1.list_namespaced_service.return_value = mock_services

        result = runner.invoke(services.app, ["--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_service.assert_called_once_with("kube-system", watch=False)

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_all_namespaces(self, mock_api, mock_service):
        """Test listing services across all namespaces."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_services = Mock()
        mock_services.items = [mock_service]
        mock_v1.list_service_for_all_namespaces.return_value = mock_services

        result = runner.invoke(services.app, ["--all-namespaces"])

        assert result.exit_code == 0
        mock_v1.list_service_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_no_traffic_policy(self, mock_api):
        """Test handling services with no internal traffic policy."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        service = Mock()
        service.metadata.namespace = "default"
        service.metadata.name = "external-service"
        service.spec.type = "LoadBalancer"
        service.spec.internal_traffic_policy = None

        mock_services = Mock()
        mock_services.items = [service]
        mock_v1.list_namespaced_service.return_value = mock_services

        result = runner.invoke(services.app, [])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_handles_api_error(self, mock_api):
        """Test handling Kubernetes API errors."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1
        mock_v1.list_namespaced_service.side_effect = Exception("API Error")

        result = runner.invoke(services.app, [])

        assert result.exit_code == 0
        assert "Error" in result.output

    @patch("devopstoolbox.k8s.services.client.CoreV1Api")
    def test_list_services_multiple_types(self, mock_api):
        """Test listing services of different types."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        cluster_ip_svc = Mock()
        cluster_ip_svc.metadata.namespace = "default"
        cluster_ip_svc.metadata.name = "cluster-svc"
        cluster_ip_svc.spec.type = "ClusterIP"
        cluster_ip_svc.spec.internal_traffic_policy = "Cluster"

        node_port_svc = Mock()
        node_port_svc.metadata.namespace = "default"
        node_port_svc.metadata.name = "nodeport-svc"
        node_port_svc.spec.type = "NodePort"
        node_port_svc.spec.internal_traffic_policy = "Local"

        lb_svc = Mock()
        lb_svc.metadata.namespace = "default"
        lb_svc.metadata.name = "lb-svc"
        lb_svc.spec.type = "LoadBalancer"
        lb_svc.spec.internal_traffic_policy = None

        mock_services = Mock()
        mock_services.items = [cluster_ip_svc, node_port_svc, lb_svc]
        mock_v1.list_namespaced_service.return_value = mock_services

        result = runner.invoke(services.app, [])

        assert result.exit_code == 0
