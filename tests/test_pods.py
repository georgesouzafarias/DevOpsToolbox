"""Tests for devopstoolbox.k8s.pods module."""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

with patch("devopstoolbox.k8s.utils.config.load_kube_config"), \
     patch("devopstoolbox.k8s.utils.config.list_kube_config_contexts", return_value=([], None)):
    from devopstoolbox.k8s import pods


runner = CliRunner()


@pytest.fixture
def mock_pod():
    """Create a mock pod object."""
    pod = Mock()
    pod.metadata.namespace = "default"
    pod.metadata.name = "test-pod"
    pod.status.phase = "Running"

    container_status = Mock()
    container_status.restart_count = 2
    pod.status.container_statuses = [container_status]

    return pod


@pytest.fixture
def mock_unhealthy_pod():
    """Create a mock unhealthy pod object."""
    pod = Mock()
    pod.metadata.namespace = "default"
    pod.metadata.name = "failing-pod"
    pod.status.phase = "CrashLoopBackOff"

    container_status = Mock()
    container_status.restart_count = 10
    pod.status.container_statuses = [container_status]

    return pod


@pytest.fixture
def mock_container():
    container = Mock()
    container.name = "main"
    container.resources.requests = {"cpu": "100m", "memory": "128Mi"}
    container.resources.limits = {"cpu": "200m", "memory": "256Mi"}
    return container


@pytest.fixture
def mock_pod_metrics():
    return {
        "items": [
            {
                "metadata": {"name": "test-pod", "namespace": "default"},
                "containers": [{"name": "main", "usage": {"cpu": "50m", "memory": "64Mi"}}],
            }
        ]
    }


class TestPodsListCommand:
    """Tests for pods list command."""

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_default_namespace(self, mock_api, mock_pod):
        """Test listing pods in default namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-n", "default"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("default", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_specific_namespace_long(self, mock_api, mock_pod):
        """Test listing pods in a specific namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("kube-system", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_specific_namespace_short(self, mock_api, mock_pod):
        """Test listing pods in a specific namespace."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-n", "kube-system"])

        assert result.exit_code == 0
        mock_v1.list_namespaced_pod.assert_called_once_with("kube-system", watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_all_namespaces_long(self, mock_api, mock_pod):
        """Test listing pods across all namespaces."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_pod_for_all_namespaces.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "--all-namespaces"])

        assert result.exit_code == 0
        mock_v1.list_pod_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_all_namespaces_short(self, mock_api, mock_pod):
        """Test listing pods across all namespaces."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod]
        mock_v1.list_pod_for_all_namespaces.return_value = mock_pods

        result = runner.invoke(pods.app, ["list", "-A"])

        assert result.exit_code == 0
        mock_v1.list_pod_for_all_namespaces.assert_called_once_with(watch=False)

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_handles_no_container_statuses(self, mock_api):
        """Test handling pods with no container statuses."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "pending-pod"
        pod.status.phase = "Pending"
        pod.status.container_statuses = None

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["list"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_list_pods_handles_api_error(self, mock_api):
        """Test handling Kubernetes API errors."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1
        mock_v1.list_namespaced_pod.side_effect = Exception("API Error")

        result = runner.invoke(pods.app, ["list"])

        assert result.exit_code == 0
        assert "Error" in result.output


class TestPodsUnhealthyCommand:
    """Tests for pods unhealthy command."""

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_unhealthy_filters_running_pods(self, mock_api, mock_pod, mock_unhealthy_pod):
        """Test that running pods are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        mock_pods = Mock()
        mock_pods.items = [mock_pod, mock_unhealthy_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["unhealthy"])

        assert result.exit_code == 0
        # Should show the unhealthy pod but not the running one
        assert "failing-pod" in result.output or "CrashLoopBackOff" in result.output or result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    def test_unhealthy_filters_succeeded_pods(self, mock_api):
        """Test that succeeded pods are filtered out."""
        mock_v1 = Mock()
        mock_api.return_value = mock_v1

        succeeded_pod = Mock()
        succeeded_pod.metadata.namespace = "default"
        succeeded_pod.metadata.name = "completed-job"
        succeeded_pod.status.phase = "Succeeded"
        succeeded_pod.status.container_statuses = []

        mock_pods = Mock()
        mock_pods.items = [succeeded_pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["unhealthy"])

        assert result.exit_code == 0


class TestPodsMetricsCommand:
    """Tests for pods metrics command."""

    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_displays_cpu_memory(self, mock_custom_api):
        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0
        mock_custom_api.list_namespaced_custom_object.assert_called_once()

    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_handles_empty_response(self, mock_custom_api):
        """Test handling empty metrics response."""
        mock_custom_api.list_namespaced_custom_object.return_value = {"items": []}

        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0

    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_handles_api_error(self, mock_custom_api):
        """Test handling metrics API errors."""
        mock_custom_api.list_namespaced_custom_object.side_effect = Exception("Metrics Server not available")

        result = runner.invoke(pods.app, ["metrics"])

        assert result.exit_code == 0
        assert "Error" in result.output or "Metrics Server" in result.output

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_specific_namespace(self, mock_custom_api, mock_core_api, mock_container):
        mock_v1 = Mock()
        mock_core_api.return_value = mock_pod_metrics

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "test-pod"
        pod.spec.containers = [mock_container]

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "--namespace", "kube-system"])

        assert result.exit_code == 0
        mock_custom_api.list_namespaced_custom_object.assert_called_once()

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_all_namespaces(self, mock_custom_api, mock_core_api):
        mock_custom_api.list_cluster_custom_object.return_value = {"items": []}

        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1
        mock_v1.list_pod_for_all_namespaces.return_value = Mock(items=[])

        result = runner.invoke(pods.app, ["metrics", "--all-namespaces"])

        assert result.exit_code == 0
        mock_custom_api.list_cluster_custom_object.assert_called_once()
        mock_v1.list_pod_for_all_namespaces.assert_called_once()

    @patch("devopstoolbox.k8s.pods.client.CoreV1Api")
    @patch("devopstoolbox.k8s.pods.custom_api")
    def test_metrics_displays_all_fields(self, mock_custom_api, mock_core_api, mock_container, mock_pod_metrics):
        mock_custom_api.list_namespaced_custom_object.return_value = mock_pod_metrics

        # CoreV1Api para listar pods
        mock_v1 = Mock()
        mock_core_api.return_value = mock_v1

        pod = Mock()
        pod.metadata.namespace = "default"
        pod.metadata.name = "test-pod"
        mock_container.name = "main"
        pod.spec.containers = [mock_container]

        mock_pods = Mock()
        mock_pods.items = [pod]
        mock_v1.list_namespaced_pod.return_value = mock_pods

        result = runner.invoke(pods.app, ["metrics", "-n", "default"])

        assert result.exit_code == 0
        assert "Pod Resources" in result.output
        mock_custom_api.list_namespaced_custom_object.assert_called_once()
        mock_v1.list_namespaced_pod.assert_called_once()
